from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth import AuthenticationError, SupabaseJwtVerifier
from app.config import Settings

ISSUER = "https://example.supabase.co/auth/v1"
AUDIENCE = "authenticated"
KEY_ID = "test-key"


def _key_pair() -> tuple[rsa.RSAPrivateKey, dict[str, object]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_jwk.update({"kid": KEY_ID, "alg": "RS256", "use": "sig"})
    return private_key, public_jwk


def _token(private_key: rsa.RSAPrivateKey, subject: str, **overrides: object) -> str:
    now = datetime.now(UTC)
    payload: dict[str, object] = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": subject,
        "role": "authenticated",
        "is_anonymous": True,
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    payload.update(overrides)
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": KEY_ID})


@pytest.mark.asyncio
async def test_asymmetric_token_returns_only_verified_subject() -> None:
    private_key, public_jwk = _key_pair()

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == f"{ISSUER}/.well-known/jwks.json"
        return httpx.Response(200, json={"keys": [public_jwk]})

    settings = Settings(auth_issuer=ISSUER, auth_audience=AUDIENCE)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        verifier = SupabaseJwtVerifier(settings, client)
        subject_a = uuid4()
        subject_b = uuid4()
        user_a = await verifier.verify(_token(private_key, str(subject_a)))
        user_b = await verifier.verify(_token(private_key, str(subject_b)))

    assert user_a.id == subject_a
    assert user_b.id == subject_b
    assert user_a.id != user_b.id
    assert user_a.is_anonymous is True


@pytest.mark.asyncio
async def test_expired_or_wrong_audience_token_fails() -> None:
    private_key, public_jwk = _key_pair()

    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"keys": [public_jwk]})

    settings = Settings(auth_issuer=ISSUER, auth_audience=AUDIENCE)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        verifier = SupabaseJwtVerifier(settings, client)
        expired = _token(
            private_key,
            str(uuid4()),
            exp=datetime.now(UTC) - timedelta(seconds=1),
        )
        with pytest.raises(AuthenticationError, match="invalid or expired"):
            await verifier.verify(expired)

        wrong_audience = _token(private_key, str(uuid4()), aud="another-service")
        with pytest.raises(AuthenticationError, match="invalid or expired"):
            await verifier.verify(wrong_audience)


@pytest.mark.asyncio
async def test_legacy_token_is_validated_by_auth_server_without_shared_secret() -> None:
    subject = uuid4()

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://example.supabase.co/auth/v1/user"
        assert request.headers["apikey"] == "public-anon-key"
        assert request.headers["authorization"].startswith("Bearer ")
        return httpx.Response(200, json={"id": str(subject), "is_anonymous": True})

    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_anon_key="public-anon-key",
    )
    token = jwt.encode(
        {"sub": str(subject)},
        "test-only-secret-with-at-least-32-bytes",
        algorithm="HS256",
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        verifier = SupabaseJwtVerifier(settings, client)
        user = await verifier.verify(token)

    assert user.id == subject
    assert user.role == "authenticated"
