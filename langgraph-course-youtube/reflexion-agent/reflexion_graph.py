

from langgraph.graph import END, MessageGraph
from chains import revise_chain, first_reponder_chain
from execute_tools import execute_tools
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from typing import List
from IPython.display import Image, display


graph = MessageGraph()
MAX_ITERATIONS = 5


graph.add_node("draft", first_reponder_chain)
graph.add_node("reviser",revise_chain)
graph.add_node("execute_tools",execute_tools)

graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "reviser")

def event_loop(state:List[BaseMessage]) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage)for item in state) 
    num_iterations = count_tool_visits
    
    if num_iterations > MAX_ITERATIONS:
       return END
    return "execute_tools"

graph.add_conditional_edges("reviser", event_loop)
graph.set_entry_point("draft")

app = graph.compile()

# Draw Image
image = app.get_graph(xray=True).draw_mermaid_png()
display(Image(image))
with open("reflexion-agent/reflexion_agent_flow.png", "wb") as f :
    f.write(image)
        
        
        
reponse = app.invoke(
    "Write tweet about recent Recent AI Trends in Crypto"
)

print(reponse[-1].tool_calls[0]["args"]["answer"])


# Stream message
input = HumanMessage(content="Write tweet about recent AI and DEFI trends")
for step in app.stream(
   input, 
    stream_mode="updates"
    ):
    print(f"{step}\n\n-----------\n")



# for messsage, metadata in app.stream(
#     input,
#     stream_mode="messages",
# ):
#     if metadata["langgraph_node"] == END :
#         print(messsage, end="|")

