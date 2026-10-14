import hashlib
from mcp.server.fastmcp import FastMCP, Context

EMAIL = "25ds1000059@ds.study.iitm.ac.in"

mcp = FastMCP(
    "exam-mcp-server",
    host="0.0.0.0",
    port=8000,
)

@mcp.tool(
    name="solve_challenge",
    description="Returns the first 16 lowercase hex characters of SHA-256(challenge:normalizedEmail)."
)
def solve_challenge(ctx: Context) -> str:
    request = ctx.request_context.request
    headers = request.headers

    challenge = headers.get("x-exam-challenge", "")
    timestamp = headers.get("x-exam-timestamp", "")
    signature = headers.get("x-exam-signature", "")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    text = f"{challenge}:{EMAIL}"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    return digest[:16]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
