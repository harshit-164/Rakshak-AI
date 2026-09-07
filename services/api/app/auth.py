from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings

ASYMMETRIC_ALGORITHMS = ("RS256", "ES256")
JWKS_CACHE_SECONDS = 600


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    role: str
    is_anonymous: bool


@dataclass(frozen=True)
class AuthenticatedRequest:
    user: AuthenticatedUser
    access_token: str = field(repr=False)


class AuthenticationError(ValueError):
    """Safe authentication failure with no token detail."""


class SupabaseJwtVerifier:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client or httpx.AsyncClient(timeout=5.0)
        self._jwks: dict[str, Any] | None = None
        self._jwks_loaded_at = 0.0
        self._jwks_lock = asyncio.Lock()

    @property
    def issuer(self) -> str:
        if self._settings.auth_issuer:
            return self._settings.auth_issuer.rstrip("/")
        if self._settings.supabase_url:
            return f"{self._settings.supabase_url.rstrip('/')}/auth/v1"
        raise AuthenticationError("authentication is not configured")

    async def verify(self, token: str) -> AuthenticatedUser:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise AuthenticationError("invalid access token") from exc

        algorithm = header.get("alg")
        key_id = header.get("kid")
        if algorithm in ASYMMETRIC_ALGORITHMS and isinstance(key_id, str):
            return await self._verify_asymmetric(token, algorithm, key_id)
        if algorithm == "HS256":
            return await self._verify_legacy_with_auth_server(token)
        raise AuthenticationError("unsupported token signing algorithm")

    async def _verify_asymmetric(
        self, token: str, algorithm: str, key_id: str
    ) -> AuthenticatedUser:
        jwks = await self._get_jwks()
        matching_keys = [key for key in jwks.get("keys", []) if key.get("kid") == key_id]
        if len(matching_keys) != 1:
            self._jwks_loaded_at = 0
            jwks = await self._get_jwks()
            matching_keys = [key for key in jwks.get("keys", []) if key.get("kid") == key_id]
        if len(matching_keys) != 1:
            raise AuthenticationError("token signing key is unavailable")

        try:
            key = jwt.PyJWK.from_dict(matching_keys[0], algorithm=algorithm).key
            payload = jwt.decode(
                token,
                key=key,
                algorithms=[algorithm],
                audience=self._settings.auth_audience,
                issuer=self.issuer,
                options={"require": ["exp", "iss", "sub", "role"]},
            )
            subject = UUID(payload["sub"])
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError("invalid or expired access token") from exc

        if payload.get("role") != "authenticated":
            raise AuthenticationError("token role is not authorized")
        return AuthenticatedUser(
            id=subject,
            role="authenticated",
            is_anonymous=bool(payload.get("is_anonymous", False)),
        )

    async def _verify_legacy_with_auth_server(self, token: str) -> AuthenticatedUser:
        if not self._settings.supabase_url or not self._settings.supabase_anon_key:
            raise AuthenticationError("legacy token verification is not configured")
        try:
            response = await self._client.get(
                f"{self._settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "apikey": self._settings.supabase_anon_key,
                    "Authorization": f"Bearer {token}",
                },
            )
            response.raise_for_status()
            user = response.json()
            subject = UUID(user["id"])
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError("invalid or expired access token") from exc

        return AuthenticatedUser(
            id=subject,
            role="authenticated",
            is_anonymous=bool(user.get("is_anonymous", False)),
        )

    async def _get_jwks(self) -> dict[str, Any]:
        now = time.monotonic()
        if self._jwks and now - self._jwks_loaded_at < JWKS_CACHE_SECONDS:
            return self._jwks
        async with self._jwks_lock:
            now = time.monotonic()
            if self._jwks and now - self._jwks_loaded_at < JWKS_CACHE_SECONDS:
                return self._jwks
            try:
                response = await self._client.get(f"{self.issuer}/.well-known/jwks.json")
                response.raise_for_status()
                document = response.json()
                if not isinstance(document.get("keys"), list):
                    raise ValueError("invalid JWKS document")
            except (httpx.HTTPError, TypeError, ValueError) as exc:
                raise AuthenticationError("token signing keys are unavailable") from exc
            self._jwks = document
            self._jwks_loaded_at = now
            return document

    async def close(self) -> None:
        await self._client.aclose()


@dataclass(frozen=True)
class AuthRuntime:
    verifier: SupabaseJwtVerifier


_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_auth_runtime() -> AuthRuntime:
    return AuthRuntime(verifier=SupabaseJwtVerifier(get_settings()))


async def get_authenticated_request(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    runtime: Annotated[AuthRuntime, Depends(get_auth_runtime)],
) -> AuthenticatedRequest:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid demo session is required.",
        )
    try:
        user = await runtime.verifier.verify(credentials.credentials)
        return AuthenticatedRequest(user=user, access_token=credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The demo session is invalid or expired.",
        ) from exc


async def get_current_user(
    request: Annotated[AuthenticatedRequest, Depends(get_authenticated_request)],
) -> AuthenticatedUser:
    return request.user


CurrentRequest = Annotated[AuthenticatedRequest, Depends(get_authenticated_request)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
