import os

class HostMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in (
          "http"
        ):
            await self.app(scope, receive, send)
            return
        headers = dict(scope["headers"])
        headers[b"host"] = bytes(os.getenv("TITILER_BASE_URL"), 'utf-8')
        scope["headers"] = [(k, v) for k, v in headers.items()]

        await self.app(scope, receive, send)
