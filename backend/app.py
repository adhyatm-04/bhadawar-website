"""FastAPI application for the Bhadawar API and local website preview."""
from __future__ import annotations

import os
import urllib.parse
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
from starlette.concurrency import run_in_threadpool

from backend.runtime import (
    API_ONLY_MODE,
    BASE_DIR,
    DATABASE_URL,
    PUBLIC_PREVIEW_MODE,
    REDIS_URL,
    _ensure_postgres_schema,
    validate_production_services,
)
from backend.state import validate_redis_connection
from server import BhadawarRequestContext


@asynccontextmanager
async def lifespan(_app):
    validate_production_services()
    if DATABASE_URL:
        await run_in_threadpool(_ensure_postgres_schema)
    if REDIS_URL:
        await run_in_threadpool(validate_redis_connection)
    yield


app = FastAPI(title="Bhadawar Hotel API", docs_url=None, redoc_url=None, lifespan=lifespan)
BASE_PATH = Path(BASE_DIR).resolve()
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
    "form-action 'self' https://api.razorpay.com; "
    "script-src 'self' 'unsafe-inline' https://checkout.razorpay.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' data: https://fonts.gstatic.com; "
    "img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; "
    "connect-src 'self' https:; frame-src https://www.google.com https://maps.google.com https://*.razorpay.com",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(self), camera=(), microphone=()",
}


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


def _run_legacy_api(method: str, path: str, headers, body: bytes, client_host: str):
    if not headers.get('Content-Length'):
        headers = dict(headers)
        headers['Content-Length'] = str(len(body))
    context = BhadawarRequestContext(path, method, headers, body, client_host)
    handler = getattr(context, f"do_{method}", None)
    if handler is None:
        context.send_error(405)
    else:
        handler()
    return context.response_status, context.response_headers, context.wfile.getvalue()


async def _api_response(request: Request) -> Response:
    body = await request.body()
    client_host = request.client.host if request.client else "127.0.0.1"
    status, headers, content = await run_in_threadpool(
        _run_legacy_api,
        request.method.upper(),
        request.url.path + (f"?{request.url.query}" if request.url.query else ""),
        request.headers,
        body,
        client_host,
    )
    response = Response(content=content, status_code=status)
    for name, value in headers:
        response.headers.append(name, value)
    return response


@app.api_route("/api", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], include_in_schema=False)
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], include_in_schema=False)
async def api_dispatch(request: Request):
    return await _api_response(request)


def _not_found() -> Response:
    return Response("Not Found", status_code=404, media_type="text/plain")


async def _serve_static(path: str, request: Request) -> Response:
    if API_ONLY_MODE:
        return _not_found()

    decoded = urllib.parse.unquote(path or "index.html").replace("\\", "/")
    parts = [part for part in decoded.split("/") if part]
    lowered = decoded.lower()
    blocked_extensions = (
        ".py", ".md", ".db", ".sqlite", ".sqlite3", ".log", ".db-wal", ".db-shm",
        ".db-journal", ".sqlite-wal", ".sqlite-shm", ".sqlite-journal",
    )
    if any(part.startswith(".") for part in parts) or lowered.endswith(blocked_extensions):
        return _not_found()
    if PUBLIC_PREVIEW_MODE and parts and parts[0].lower() in {"work", "outputs", "__pycache__"}:
        return _not_found()

    if lowered in {"corporate-menu.js", "corporate-menu.json"}:
        client_host = request.client.host if request.client else "127.0.0.1"
        context = BhadawarRequestContext(request.url.path, "GET", request.headers, b"", client_host)
        if (context._staff() or {}).get("role") != "admin":
            return _not_found()

    target = (BASE_PATH / decoded).resolve()
    try:
        if os.path.commonpath((str(BASE_PATH), str(target))) != str(BASE_PATH):
            return _not_found()
    except ValueError:
        return _not_found()
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return _not_found()
    return FileResponse(target)


@app.get("/", include_in_schema=False)
async def serve_index(request: Request):
    return await _serve_static("index.html", request)


@app.get("/{path:path}", include_in_schema=False)
async def serve_site_file(path: str, request: Request):
    return await _serve_static(path, request)
