import re
from utils import llm_response

class REASONING_STEPBACK():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        self.task_name_cache = None
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)
        if self.memory is not None:
            if self.task_name_cache is not None and self.task_name_cache == task_name:
                pass
            else:
                self.task_name_cache = task_name
                self.memory_cache = self.memory(task_description)
        else:
            self.memory_cache = ''
        if self.tooluse is not None:
            tooluse = self.tooluse(task_description, tool_instruction)
        else:
            tooluse = ''
        split_text = task_description.rsplit('You are in the', 1)
        examples = split_text[0]
        task_description = 'You are in the' + split_text[1]
        if task_description.split('Your')[-1].count('>') == 1:#这个任务只在子任务的第一步进行stepback
            self.principle = self.stepback(task_description)
            
        prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions must follow the examples.{tooluse}
Here are some examples.
{examples}{self.memory_cache}{self.principle}
Here is the task:
{task_description}'''
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return reasoning_result
    def stepback(self, task_description):
        last_index = task_description.rfind('>')
        task_description = task_description[:last_index]
        stepback_prompt = f'''What common sense, instruction structure is involved in solving this task?
{task_description}'''
        principle = llm_response(prompt=stepback_prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return principle
