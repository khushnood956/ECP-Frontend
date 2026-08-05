import time
import uuid

from fastapi import Request

from app.core.logging.logger import get_logger, request_id_ctx_var

logger = get_logger(__name__)


class RequestLoggingMiddleware:
    """
    Pure ASGI Middleware that ensures every request has an X-Request-ID.
    It sets the ID in contextvars, request.state, logs request/response metadata,
    and appends the ID to the response header.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive)
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Set to request state
        scope["state"] = scope.get("state", {})
        scope["state"]["request_id"] = request_id

        # Set context var
        token = request_id_ctx_var.set(request_id)

        start_time = time.time()
        logger.info(f"Incoming Request: {request.method} {request.url.path}")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                # Ensure X-Request-ID is in the response headers
                headers.append((b"x-request-id", request_id.encode("latin-1")))

                status_code = message["status"]
                process_time = (time.time() - start_time) * 1000
                logger.info(
                    f"Outgoing Response: {request.method} {request.url.path} "
                    f"- Status: {status_code} - Time: {process_time:.2f}ms"
                )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} - Time: {process_time:.2f}ms",
                exc_info=True,
            )
            raise
        finally:
            request_id_ctx_var.reset(token)
