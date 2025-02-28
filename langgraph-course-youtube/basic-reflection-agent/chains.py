from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
import getpass
import os
from langchain_openai import AzureOpenAI, ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")


generation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are a twitter techie influencer assistant tasked with writing excellent twitter posts."
         "Generate best tweet possible from the user's request"
         "If the user provides critique, respond with a revised version of your previous attempts."
         ),
        MessagesPlaceholder(variable_name="messages")
    ]
)


reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", 
            "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
            "Always provide detailed recommendations, including requests for length, virality, style, etc."
        ),
        MessagesPlaceholder(variable_name="messages")
        
    ]
    )



# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
llm = ChatOpenAI(
    model="gpt-4o-mini"
)
generation_chain = generation_prompt | llm
reflection_chain = reflection_prompt | llm 