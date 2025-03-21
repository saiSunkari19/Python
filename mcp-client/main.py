from typing import Optional
from contextlib import AsyncExitStack
import sys, asyncio
import os

from langchain_openai import ChatOpenAI,AzureChatOpenAI

from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


from anthropic import Anthropic 
from dotenv import load_dotenv


load_dotenv()
class MCPClient:
    def __init__(self):
        
        # Initialise session and client objects
        self.session: Optional[ClientSession]= None
        self.exit_stack = AsyncExitStack()
        self.antropic = Anthropic()
        self.client =  AzureChatOpenAI(
            azure_deployment="gpt-4o-mini",
            model_name="gpt-4o-mini",
            api_version="2024-02-15-preview",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint="https://degents-azure-open-ai.openai.azure.com/",
        )    
        
    
    # Connect to Server
    async def  connect_to_server(self, server_script_path: str):
        """Connect to MCP Server
        Args:
            server_script_path: Path to server script (.py or .js)        
        """
        
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        
        if not (is_python or is_js):
            raise ValueError("Server script must be .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command = command,
            args = [server_script_path],
            env = None
        )       
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print(f"\n Connected with Server with Tools ", [tool.name for tool in tools])
            
    # Process query and handling tool calls
    async def process_query(self, query: str)->str:
        """Process a query using LLM and available tools 

        Args:
            query (str): Description of the query

        Returns:
            str: Return the string response from the query to handle for LLM 
        """
        messages = [
            {
                "role":"user",
                "content": query
            }
        ]
        
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name, 
            "description": tool.description, 
            "input_schema" : tool.inputSchema
        } for tool in response.tools]
        
        # Initial Claude API Call 
        # response = self.antropic.messages.create(
        #     model ="claude-3-5-sonnet-20241022",
        #     max_tokens=1000, 
        #     messages = messages, 
        #     tools = available_tools
        # )
        
        
        
        # Initial OpenAI API Call 
        # response = await self.client.invoke(messages)
        tools = await load_mcp_tools(self.session)
        agent = create_react_agent(self.client, tools)
        response = await agent.ainvoke({"messages":messages})
        
        # Process reponse and handle tool calls 
        final_text = []
        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content) 
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                
                # Execute the tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                assistant_message_content.append(content)
                
                messages.append({
                    "role": "assistant", 
                    "content" : assistant_message_content
                })
                
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type" : "tool_result",
                            "tool_use_id": content.id, 
                            "content": result.content
                        }
                    ]
                })
                
                print(f"before cluder here ")
                # Get the next reponse from Claude
                response = self.antropic.messages.create(
                model ="claude-3-5-sonnet-20241022",
                max_tokens=1000, 
                messages = messages, 
                tools = available_tools
                )
                
                print(f"before agter here ")

                final_text.append(response.content[0].text)
        return "\n".join(final_text)
        
    # Adding chat interface
    async def chat_loop(self):
        """Run an interactive chat loop
        """    
        print("\n MCP Client Started")
        print("Type your queries or 'quit' to exit." )
        
        while True :
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query=query)
                print("\n"+ response)
            except Exception as e :
                print(f"\n Error: {str(e)}")
    
    
    # Clean up
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
                
            
            

## Main entry point

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit()
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()
        


if __name__ == "__main__":
    import sys
    asyncio.run(main())
