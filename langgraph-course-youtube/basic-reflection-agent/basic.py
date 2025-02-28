from dotenv import load_dotenv
from IPython.display import Image, display
from chains import generation_chain, reflection_chain
from langchain_core.messages import HumanMessage

from langgraph.graph import END, MessageGraph
load_dotenv()
    
graph = MessageGraph()

def generate_node(state):
    return generation_chain.invoke({
        "messages":state
    })


def reflection_node(state):
    response = reflection_chain.invoke({
        "messages":state
    })
    
    return [HumanMessage(content=response.content)]

graph.add_node("generation", generate_node)
graph.add_node("reflection", reflection_node)

def should_continue(state):
    if(len(state)) >4 :
        return END
    else:
        return "reflection"
        
        

graph.set_entry_point("generation")
graph.add_conditional_edges("generation", should_continue)
graph.add_edge("reflection", "generation")
app = graph.compile()

# Draw Image
image = app.get_graph(xray=True).draw_mermaid_png()
display(Image(image))
with open("basic-reflection-agent/relection_agent_flow.png", "wb") as f :
    f.write(image)


# Stream message
input = HumanMessage(content="write tweet about langgraph")
for step in app.stream(
   input, 
    stream_mode="updates"
    ):
    print(f"{step}\n\n-----------\n")
