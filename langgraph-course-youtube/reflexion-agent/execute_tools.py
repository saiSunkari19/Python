import json
from typing import List
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, HumanMessage
from chains import parser
from langgraph.prebuilt import ToolInvocation, ToolExecutor
from langchain_community.tools import TavilySearchResults
from collections import defaultdict


tavily_tool = TavilySearchResults(max_results=5)
tool_executor = ToolExecutor([tavily_tool])


def execute_tools(state: List[BaseMessage]) -> List[ToolMessage]:
    last_ai_message: AIMessage = state[-1]
    parsed_tool_calls = parser.invoke(last_ai_message)
    
    ids = []
    tool_invocations = []
    
    
    for parsed_call in parsed_tool_calls:
        for query in parsed_call["args"]["search_queries"]:
            tool_invocations.append(
                ToolInvocation(
                    tool="tavily_search_results_json",
                    tool_input=query
                )
            )
            ids.append(parsed_call["id"])
    outputs = tool_executor.batch(tool_invocations)
    
    
    # Map each output to its corresponding ID and tool input
    outputs_map = defaultdict(dict)
    for _id, output, invocation in zip (ids, outputs,tool_invocations):
        outputs_map[_id][invocation.tool_input] = output
        
    # Convert the mapped outputs to ToolMessage objects
    
    tool_messages = []
    
    for _id, mapped_output in outputs_map.items():
        tool_messages.append(
            ToolMessage(
                content=json.dumps(mapped_output), tool_call_id=_id
            )
        )
    return tool_messages


# raw_res = execute_tools(
#         state=[
#             HumanMessage(
#                 content="Write about how small business can leverage AI to grow"
#             ),
#             AIMessage(
#                 content="", 
#                 tool_calls=[
#                     {
#                         "name": "AnswerQuestion",
#                         "args": {
#                             'answer': '', 
#                             'search_queries': [
#                                     'AI tools for small business', 
#                                     'AI in small business marketing', 
#                                     'AI automation for small business'
#                             ], 
#                             'reflection': {
#                                 'missing': '', 
#                                 'superfluous': ''
#                             }
#                         },
#                         "id": "call_KpYHichFFEmLitHFvFhKy1Ra",
#                     }
#                 ],
#             ),
#         ]
#     )


# print(raw_res, 'raw')
# res = json.loads(raw_res[0].content)
# print(res)
