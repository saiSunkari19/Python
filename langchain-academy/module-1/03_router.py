import os, getpass
from dotenv import load_dotenv

load_dotenv()

def _set_env(var:str) :
    if not os.environ.get(var) :
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("AZURE_OPENAI_API_KEY")


from langchain_openai import ChatOpenAI, AzureChatOpenAI

def multiply(a:int, b:int) -> int:
    """
    Multiply two numbers

    Args:
        a : first int
        b: second int
    """
    return a * b



llm = AzureChatOpenAI(
            azure_deployment="gpt-4o-mini",
            model_name="gpt-4o-mini",
            api_version="2024-02-15-preview",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint="https://degents-azure-open-ai.openai.azure.com/",
        )        
llm_with_tools = llm.bind_tools([multiply]) # Bind tools to the LLM

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition


# Node that calls the tool
def tool_calling_llm(state: MessagesState):
    return { "messages":[llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", END)

graph = builder.compile()

from langchain_core.messages import HumanMessage
msgs = [HumanMessage(content="what is  2 * 3")]

msgs = graph.invoke({"messages": msgs})
for m in msgs["messages"]:
    m.pretty_print()
    print(m)





        
        