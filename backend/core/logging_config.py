# backend/core/logging_config.py
#
# Request-ID tracing middleware and logging helpers.
#
# Design goals:
#   - Every log line emitted during a request includes a UUID4 request_id so
#     you can `grep <request_id>` in Render's log stream and see the full
#     lifecycle end-to-end.
#   - The request_id is read from the incoming `X-Request-ID` header if the
#     client / load balancer supplies one; otherwise a new UUID4 is generated.
#   - The request_id is also written back into the response headers so API
#     clients can correlate their own logs with server-side traces.
#
# Implementation notes:
#   - Uses stdlib `contextvars` to bind the request_id to the current async
#     context without touching global state or requiring structlog.
#   - A custom `logging.Filter` reads the ContextVar and injects `request_id`
#     into every LogRecord, which lets the %(request_id)s format token in
#     main.py's basicConfig work automatically.

import logging
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── ContextVar ────────────────────────────────────────────────────────────────
# Holds the request_id for the current async task.  Falls back to "-" when
# accessed outside a request context (e.g. startup logs).
_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def get_request_id() -> str:
    """Return the request_id bound to the current execution context."""
    return _request_id_var.get()


# ── Logging filter ────────────────────────────────────────────────────────────

class RequestIDFilter(logging.Filter):
    """Injects ``request_id`` into every LogRecord so formatters can use it.

    Retained for callers that want to attach it to a specific handler.  The
    record factory below is what actually guarantees coverage — see the note
    there for why a logger-level filter is not enough.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = get_request_id()  # type: ignore[attr-defined]
        return True


# ── Guaranteed request_id on every record ─────────────────────────────────────
# A filter attached to the ROOT LOGGER only runs for records logged directly on
# the root logger.  Records created by a child logger — i.e. every
# `logging.getLogger(__name__)` call in this codebase — propagate to the root's
# HANDLERS but deliberately skip the root's FILTERS (see the stdlib
# `Logger.callHandlers` / `Logger.handle` split).  Those records therefore
# reached main.py's `%(request_id)s` formatter with no such attribute and blew
# up with `KeyError: 'request_id'`, so every application log line was silently
# dropped — including the "skills extracted | count=0" line that would have
# exposed the zero-score bug immediately.
#
# Overriding the record factory sets the attribute at construction time, which
# covers every logger, every handler, and any import order relative to
# `logging.basicConfig`.
_OLD_FACTORY = logging.getLogRecordFactory()


def _record_factory(*args, **kwargs) -> logging.LogRecord:
    record = _OLD_FACTORY(*args, **kwargs)
    record.request_id = get_request_id()  # type: ignore[attr-defined]
    return record


# Guard against double-installation under uvicorn's reloader, which can import
# this module more than once in the same interpreter.
if not getattr(_OLD_FACTORY, "_bridgr_request_id", False):
    _record_factory._bridgr_request_id = True  # type: ignore[attr-defined]
    logging.setLogRecordFactory(_record_factory)


# ── Middleware ─────────────────────────────────────────────────────────────────

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Per-request middleware that:

    1. Reads ``X-Request-ID`` from incoming headers (or generates a UUID4).
    2. Binds it into the ``_request_id_var`` ContextVar for the duration of
       the request so every logger call picks it up automatically.
    3. Writes ``X-Request-ID`` back into the response headers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Honour an upstream-supplied ID (e.g. from a load balancer) or mint one.
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = _request_id_var.set(request_id)
        try:
            response: Response = await call_next(request)
        finally:
            # Always restore context, even if an exception is raised.
            _request_id_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
