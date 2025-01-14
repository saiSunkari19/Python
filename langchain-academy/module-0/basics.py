import os, getpass
from dotenv import load_dotenv

load_dotenv()
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}")

_set_env("OPENAI_API_KEY")
_set_env("TAVILY_API_KEY")


from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

gpt4o_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt35_chat = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


# Create Message 
msg = HumanMessage(content="Hello World", name="Sai")

# Message list 
msgs = [msg]

# Invoke the model with a list of msgs
res=gpt4o_chat.invoke(msgs)
print(res)

res=gpt35_chat.invoke(msgs)
print(res)

# Tavily Search 
tavily_search = TavilySearchResults(max_results=3)
search_docs = tavily_search.invoke("langGraph vs langSmith")
print(search_docs)



