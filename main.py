
import contextvars
import hashlib

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.types import ASGIApp, Scope, Receive, Send

EMAIL = "25ds1000059@ds.study-iitm.ac.in"

challenge_var = contextvars.ContextVar("exam_challenge", default="")

security = TransportSecuritySettings(
    allowed_hosts=[
        "mcp-challenge-server-1naf.onrender.com",
        "mcp-challenge-server-1naf.onrender.com:*",
    ]
)

mcp = FastMCP(
    "exam-mcp-server",
    transport_security=security,
)


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


@mcp.tool(
    name="solve_challenge",
    description=(
        "Returns the first 16 lowercase hex characters of "
        "SHA-256(challenge:normalizedEmail)."
    ),
)
def solve_challenge() -> str:
    """Calculate the challenge hash using the request header."""
    challenge = challenge_var.get()

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    text = f"{challenge}:{EMAIL}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


app = ChallengeHeaderMiddleware(mcp.streamable_http_app())


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

