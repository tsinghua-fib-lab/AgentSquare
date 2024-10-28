import os
from utils_llm import llm_response, get_price

class REASONING_SELFREFINE():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        memory = ''
        tooluse = ''
        prompt = '''
{memory}
{tooluse}
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=['\n']).replace('>', '').strip()
        reasoning_result = self.refine(task_description, reasoning_result)
        return reasoning_result
    def refine(self, task_description, reasoning_results):
        task_description = task_description + ' previous step:' + reasoning_results + '\nrewrite: '
        prompt = '''You are interacting with a scienceworld enviroment to solve a task. You need to check your previous step for errors, such as 1. Formatting errors, your instruction format should follow the example instruction format, 2. Logic error, you can only pick up what exists in that place.
If there is no error, do not modify it. Output the step directly.
{task_description}
'''     
        prompt = prompt.format(task_description=task_description)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=['\n']).split(':')[-1].strip()
        return reasoning_result
        
