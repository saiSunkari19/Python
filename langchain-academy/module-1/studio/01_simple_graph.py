from typing_extensions import TypedDict, Literal

class State(TypedDict):
    graph_state: str
    

# Nodes
def node_1(state):
    print("node-1")
    return {"graph_state" : state['graph_state'] + "I am"}

def node_2(state):
    print("node-2")
    return {"graph_state" : state['graph_state'] + " happy "}

def node_3(state):
    print("node-3")
    return {"graph_state" : state['graph_state'] + " cheerish"}


# Edges
import random 

def decide_mood(state) -> Literal["node_2", "node_3"]:
    
    user_input = state["graph_state"]
    
    if random.random() < 0.5:
        return "node_2"
    return "node_3"

# Graph construction 
# from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

# Build Graph 
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic 
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add 
graph = builder.compile()
res = graph.invoke({"graph_state":"Hi, this is Lance"})
print(res)
