import os
from utils_llm import llm_response, get_price

class REASONING_DILU():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        memory = ''
        tooluse = ''
        prompt = [
            {
                "role": "system",
                "content": '''You are ChatGPT, a large language model trained by OpenAI. Now you act as a scientific assistant robot, who can give accurate and correct instruction in interacting with a scienceworld environment. You will be given a detailed description of the scenario of current frame . 
'''
            },
            {
                "role": "user",
                "content": f'''
{memory}
{tooluse}
{task_description}
'''
            }
        ]
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return reasoning_result

