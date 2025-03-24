from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import AzureChatOpenAI ,ChatOpenAI
from dotenv import load_dotenv

import os, asyncio
load_dotenv()

model =  AzureChatOpenAI(
            azure_deployment="gpt-4o-mini",
            model_name="gpt-4o-mini",
            api_version="2024-02-15-preview",
            api_key= os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint="https://agents-azure-open-ai.openai.azure.com",
            max_tokens=100
        )  

# model  = ChatOpenAI(model="gpt-4o")
#stdio
server_params  = StdioServerParameters(
    command= "python",
    args=["/Users/sai/go/src/github.com/saiSunkari19/python/mcp-with-langgraph/mcpServer.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Initiliase the connection
            await session.initialize()
            
            # Get Tools 
            tools = await load_mcp_tools(session)
            
            agent  = create_react_agent(model, tools)
            agent_resopnse  = agent.invoke({
                "messages": "What is (9x2) /3 ?"
            })
            
            for m in agent_resopnse["messages"]:
                m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())