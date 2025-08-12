import asyncio
from langchain_ollama import ChatOllama
from mcp_use import MCPAgent, MCPClient

async def main():
    client = MCPClient(config={
    "mcpServers": {
        "myServer": {
            "command": "uv",
            "args": [
                "--directory", "C:/MCP Files/server",
                "run", "mcp_server.py"
            ],
            "env": {
                "PYTHONUNBUFFERED": "1"
            }
        }
    }
})
    # Create LLM
    llm = ChatOllama(model="llama2", base_url="http://localhost:11434")
    # Create agent with tools
    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    # Run the query
    result = await agent.run("Find the user information of specific user from an external mock API (https://fake-json-api.mock.beeceptor.com/users), which returns informations for a list of users")

if __name__ == "__main__":
    asyncio.run(main())