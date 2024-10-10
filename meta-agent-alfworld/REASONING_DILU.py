import re
from utils import llm_response

class REASONING_DILU():
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
        prompt = [
            {
                "role": "system",
                "content": '''You are ChatGPT, a large language model trained by OpenAI. Now you act as a mature domestic robot, who can give accurate and correct instruction in interacting with a household. You will be given a detailed description of the scenario of current frame along with your history of previous decisions. 
'''
            },
            {
                "role": "user",
                "content": f'''Above messages are some examples of how you make a step successfully in the past. Those scenarios are similar to the current scenario. You should refer to those examples to make a step for the current scenario. Your instructions must follow the examples.{tooluse}
Here are two examples.
{examples}{self.memory_cache}
Here is the task:
{task_description}'''
            }
        ]
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return reasoning_result

