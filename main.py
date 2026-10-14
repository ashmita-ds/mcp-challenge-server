
import hashlib

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "25ds1000059@ds.study-iitm.ac.in"

security = TransportSecuritySettings(
    allowed_hosts=[
        "mcp-challenge-server-1naf.onrender.com",
        "mcp-challenge-server-1naf.onrender.com:*",
    ]
)

mcp = FastMCP("exam-mcp-server")


@mcp.tool(
    name="solve_challenge",
    description=(
        "Returns the first 16 lowercase hex characters of "
        "SHA-256(challenge:normalizedEmail)."
    ),
)
def solve_challenge(ctx: Context) -> str:
    """Calculate the hash from the incoming challenge header."""
    headers = ctx.headers or {}
    challenge = headers.get("x-exam-challenge", "")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    text = f"{challenge}:{EMAIL}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


app = mcp.streamable_http_app(
    transport_security=security,
    host="0.0.0.0",
)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        transport_security=security,
        host="0.0.0.0",
    )
