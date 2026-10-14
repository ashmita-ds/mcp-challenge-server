
import hashlib
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Exam Challenge Server")

EMAIL = "25ds1000059@ds.study.iitm.ac.in"


@mcp.tool()
async def solve_challenge(ctx: Context) -> str:
    """Solve the current exam challenge from the HTTP request headers."""
    request = ctx.request_context.request
    challenge = request.headers.get("x-exam-challenge", "")

    result = hashlib.sha256(
        f"{challenge}:{EMAIL}".encode("utf-8")
    ).hexdigest()[:16]

    return result


app = mcp.streamable_http_app()
