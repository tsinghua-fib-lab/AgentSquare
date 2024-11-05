from openai import OpenAI
import os
from utils import get_chat, get_completion, get_price
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class COTREASONING():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        task_description = task_description
        memory = self.memory('')
        tooluse = self.tooluse(task_description, tool_instruction)
        prompt = '''Solve the task step by step
{memory}
{tooluse}
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        if self.llm_type == 'gpt-3.5-turbo-instruct':
            reasoning_result = get_completion(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        else:
            reasoning_result = get_chat(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        
        return reasoning_result

