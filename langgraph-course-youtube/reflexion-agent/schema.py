from typing import List 
from pydantic import BaseModel, Field



class Reflection(BaseModel):
    missing:str = Field(
        description="Critique of what is missing"
    )
    superfluous:str = Field(
        description="Critique of what is superfluous"
    )

class AnswerQuestion(BaseModel):
    answer: str = Field(
        description="~100 word detailed tweet post to the user question/statement"
    )
    search_queries :List[str] = Field(
        description=
        "1-3 search queries for researching improvements to address the critique of your current answer"
    )
    reflection: Reflection = Field(
        description="Your reflection on the initial answer"
    )
    
    
class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question"""
    
    references: List[str] = Field(
        description="Citations motivating your updated answer"
    )