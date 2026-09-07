const forwardedRequestHeaders = [
  "authorization",
  "content-type",
  "idempotency-key",
  "x-request-id",
] as const;

async function proxy(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  if (path.length === 0 || path[0] !== "v1") {
    return Response.json(
      { error: { code: "route_not_allowed", message: "Route is not available.", retryable: false } },
      { status: 404 },
    );
  }

  const backendOrigin = process.env.API_BASE_URL;
  if (!backendOrigin) {
    return Response.json(
      {
        error: {
          code: "backend_unconfigured",
          message: "The analysis service is not configured.",
          retryable: false,
        },
      },
      { status: 503 },
    );
  }

  const incomingUrl = new URL(request.url);
  const backendUrl = new URL(`/${path.map(encodeURIComponent).join("/")}`, backendOrigin);
  backendUrl.search = incomingUrl.search;
  const headers = new Headers();
  for (const name of forwardedRequestHeaders) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  try {
    const body =
      request.method === "GET" || request.method === "HEAD"
        ? undefined
        : await request.arrayBuffer();
    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body,
      cache: "no-store",
      redirect: "error",
    });
    const responseHeaders = new Headers();
    responseHeaders.set(
      "content-type",
      response.headers.get("content-type") ?? "application/json",
    );
    const requestId = response.headers.get("x-request-id");
    if (requestId) responseHeaders.set("x-request-id", requestId);
    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch {
    return Response.json(
      {
        error: {
          code: "backend_unavailable",
          message: "The analysis service could not be reached.",
          retryable: true,
        },
      },
      { status: 503 },
    );
  }
}

export const dynamic = "force-dynamic";
export const GET = proxy;
export const POST = proxy;
