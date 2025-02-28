from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.openai_tools import PydanticToolsParser, JsonOutputToolsParser
from langchain_core.messages import HumanMessage
import datetime

from dotenv import load_dotenv
from schema import AnswerQuestion, ReviseAnswer

pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion, ReviseAnswer])

parser = JsonOutputToolsParser(return_id=True)

load_dotenv()
actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system", 
    """You are an expert In Viral Tweet Generations Related to Convergence of AI and Blockchain.
    
    current time : {time}
    
    1. {first_instruction}
    2. Reflect and Critique your answer, Be severe to maximize improvement.
    3. After reflection, **list 1-3 search queries separately** for 
    researching improvement. Do not include them inside the reflection. 
    """,
         
         ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system", 
            "Answer the user's question above using the required format."
        ),
    ]
).partial(
    time=lambda:datetime.datetime.now().isoformat()
)

first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction = "Provide a detailed ~100 word tweet for user input"
)


llm = ChatOpenAI(
    model="gpt-4o-mini"
)

first_reponder_chain = first_responder_prompt_template | llm.bind_tools(
    tools= [AnswerQuestion], tool_choice= "AnswerQuestion"
) | pydantic_parser



# Revise section

revise_instructions = """Revise your previous answer using the new information
    - You should use the previous critique to add important information to answer.
        - you MUST include numerical citations in your revised answer to ensure it can be verified.
        - Add a "References" section to the bottom of your answer (which does not count towards the word limit). 
        In the form of:
                - [1] https://example.co
                - [2] https://example.co
        )
        - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more that 
        100 words.
"""

revise_chain = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer") | pydantic_parser


response = first_reponder_chain.invoke({
    "messages": [HumanMessage(content="what the current defi situation")]
})


print(response)