import os, getpass
from dotenv import load_dotenv
load_dotenv()


def _set_env(var:str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass("f{var}:")

_set_env("OPENAI_API_KEY")

from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AnyMessage, AIMessage

def multiply(a:int, b: int) -> int:
    """ Multiply a and b.
    
    Args: 
        a: first int
        b: second int
    """
    return a * b

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools([multiply])
# tool_call = llm_with_tools.invoke([HumanMessage(content=f"what is   2  * 3")])
# print(tool_call.additional_kwargs['tool_calls'])

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition



# Node 
def tool_calling_llm (state: MessagesState):
    return {"messages" : [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm",END)

graph  = builder.compile()

msgs = [AIMessage(content="Hi How can I help you?"), HumanMessage(content="what is 12 multiply 4")]
msgs = graph.invoke({"messages": msgs})

for m in msgs["messages"]:
    m.pretty_print()
    print(m)
    


class MessagesState (TypedDict):
    messages : list[AnyMessage]
    
    