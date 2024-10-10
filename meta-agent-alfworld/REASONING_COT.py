import re
from utils import llm_response

class REASONING_COT():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        self.task_name_cache = None
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
        print(task_name[2])
        if self.memory is not None:
            if self.task_name_cache is not None and self.task_name_cache == task_name:
                pass
            else:
                self.task_name_cache = task_name
                # 读取记忆，一个有success，一个没有，以这个来区分，因为当时定义接口的时候，强行只能传一个参数，所以我alfworld这里就写成了这样
                self.memory_cache = self.memory(task_description)
                print('\n\n\n\n\n存的东西')
                print(self.memory_cache)
        else:
            self.memory_cache = ''
        if self.tooluse is not None:
            tooluse = self.tooluse(task_description, tool_instruction)
        else:
            tooluse = ''
        split_text = task_description.rsplit('You are in the', 1)
        examples = split_text[0]
        task_description = 'You are in the' + split_text[1]
        prompt = '''Solve the task step by step. Interact with a household to solve a task. Your instructions must follow the examples.{tooluse}
Here are some examples.
{examples}{memory}
Here is the task:
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache, tooluse=tooluse)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        
        return reasoning_result

