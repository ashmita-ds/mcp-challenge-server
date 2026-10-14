
import contextvars
import hashlib

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.types import ASGIApp, Scope, Receive, Send

EMAIL = "25ds1000059@ds.study.iitm.ac.in"

challenge_var = contextvars.ContextVar("exam_challenge", default="")

mcp = FastMCP("Exam Challenge Server")


class ChallengeHeaderMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        challenge = headers.get(
            b"x-exam-challenge", b""
        ).decode("ascii")

        token = challenge_var.set(challenge)

        try:
            await self.app(scope, receive, send)
        finally:
            challenge_var.reset(token)


@mcp.tool()
def solve_challenge() -> str:
    """Return the expected hash for the challenge in this request."""
    challenge = challenge_var.get()

    return hashlib.sha256(
        f"{challenge}:{EMAIL}".encode("utf-8")
    ).hexdigest()[:16]


security = TransportSecuritySettings(
    allowed_hosts=[
        "mcp-challenge-server-1naf.onrender.com",
        "mcp-challenge-server-1naf.onrender.com:*",
    ]
)

app = ChallengeHeaderMiddleware(
    mcp.streamable_http_app(transport_security=security)
)
