from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
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


async def main():
    async with MultiServerMCPClient(
        {
            "mcp-server" : {
                "url":"http://localhost:8000/sse",
                "transport":"sse"
            }
        }
    ) as client:
            
            agent  = create_react_agent(model, client.get_tools())
            agent_resopnse  = await agent.invoke({
                "messages": "What is (9x2) /3 ?"
            })
            
            for m in agent_resopnse["messages"]:
                m.pretty_print()



async def main_sse():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession (read, write) as session:
            await session.initialize()
            
            
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            
            agent_response = await agent.invoke ({
                "messages" : "What is (9x2)/3"
            })
            
            for m in agent_response["messages"]:
                m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main_sse())