from typing import Any, List, Dict
import httpx
from mcp.server.fastmcp import FastMCP, Context

API_URL = "https://fake-json-api.mock.beeceptor.com/users"

# Create the MCP server instance
mcp = FastMCP("users_server")

@mcp.tool()
async def find_users(ctx: Context, search: str = "") -> List[Dict[str, Any]]:
    """
    Fetch users from the Beeceptor mock API and optionally filter by name substring.

    Args:
        search: Optional case-insensitive substring to match within the user's name.

    Returns:
        A list of user objects (JSON) matching the filter. If search is empty, returns all users.
    """
    await ctx.info("Fetching users from Beeceptor Fake JSON API...")
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(API_URL)
        resp.raise_for_status()
        data = resp.json()

    if not isinstance(data, list):
        raise ValueError("Unexpected response format: expected a JSON list")

    if not search:
        return data

    s = search.lower()
    return [u for u in data if s in str(u.get("name", "")).lower()]

if __name__ == "__main__":
    # Run the MCP server over stdio (required for MCP clients like mcp-use)
    mcp.run(transport="stdio")
