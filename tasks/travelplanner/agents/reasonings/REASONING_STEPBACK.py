import os
from utils_llm import llm_response, get_price
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

class REASONING_STEPBACK():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= '',stop_list = ['\n']):
        memory = ''
        tooluse = ''
        if self.principle == '':#这个任务只在子任务的第一步进行stepback
            self.principle = self.stepback(task_description,stop_list)
            
        prompt = f'''Solve the task step by step. Gather information from travelplanner sandbox to solve a task. 
Here is the task:
{task_description}
The common sense and instruction structure involved in solving this task is:
{self.principle}
{memory}
{tooluse}
'''
        # reasoning_result = llm([HumanMessage(content=prompt)]).content
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list)
       
        return reasoning_result
    def stepback(self, task_description,stop_list):
        stepback_prompt = f'''What common sense, instruction structure is involved in solving this task?
{task_description}'''
        principle = llm_response(prompt=stepback_prompt, model=self.llm_type, temperature=0.1, stop_strs=stop_list)
        return principle
