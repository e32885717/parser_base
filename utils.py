from typing import Callable, Any
from fastapi.routing import APIRoute
from fastapi import Request, Response
import zlib
import json

# GZIP SUPPORT

class GzipRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = zlib.decompress(body)
            self._body = body
        return self._body

class GzipRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            request = GzipRequest(request.scope, request.receive)
            return await original_route_handler(request)
        return custom_route_handler

# PrettyJSON
class PrettyJSONResponse(Response):
    media_type = "application/json"
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")