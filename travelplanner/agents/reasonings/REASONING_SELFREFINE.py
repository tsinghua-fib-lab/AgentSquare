import os
from utils_llm import llm_response, get_price
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

class REASONING_SELFREFINE():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= '',stop_list = ['\n']):

        memory = ''
        tooluse = ''
        prompt = '''Your instructions should follow the examples.
{memory}
{tooluse}
Here is the current task:
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        # reasoning_result = llm([HumanMessage(content=prompt)]).content.replace('>', '').strip()
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list).strip()
        reasoning_result = self.refine(task_description, reasoning_result,stop_list)
        return reasoning_result
    def refine(self, task_description, reasoning_results,stop_list):

        task_description = task_description + ' previous step:' + reasoning_results + '\nrewrite: '
        prompt = '''You're trying to make a travel plan. You need to check your previous step for errors, such as 1. Commensense error: you can't book a ticket that doesn't exist that day or book a hotel that's over budget 2. No consideration of user needs: users want to travel with their pets, and you can't book a hotel that doesn't allow pets.
If there is no error, do not modify it. Output the step directly.
Tasks:
{task_description}
'''     
        prompt = prompt.format(task_description=task_description)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list).split(':')[-1].strip()
        return reasoning_result
        
