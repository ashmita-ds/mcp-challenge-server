import hashlib
from mcp.server.fastmcp import FastMCP, Context

EMAIL = "25ds1000059@ds.study.iitm.ac.in"

mcp = FastMCP("exam-mcp-server")

@mcp.tool(
    name="solve_challenge",
    description="Returns the first 16 lowercase hex characters of SHA-256(challenge:normalizedEmail)."
)
def solve_challenge(ctx: Context) -> str:
    headers = ctx.request_context.request.headers

    challenge = headers.get("x-exam-challenge", "")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    text = f"{challenge}:{EMAIL}"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    return digest[:16]

app = mcp.streamable_http_app()
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
