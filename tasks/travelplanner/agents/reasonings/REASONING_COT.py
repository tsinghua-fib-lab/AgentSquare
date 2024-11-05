import os
from utils_llm import llm_response, get_price
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

class REASONING_COT():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= '',stop_list = ['\n']):
        # llm = ChatOpenAI(temperature=1,
        #              max_tokens=256,
        #              model_name=self.llm_type,
        #              openai_api_key=os.environ.get("OPENAI_API_KEY"),
        #              model_kwargs={"stop": stop_list})
        memory = ''
        tooluse = ''
        prompt = '''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.
{memory}
{tooluse}
Here is the current task:
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list)
        # reasoning_result = llm([HumanMessage(content=prompt)]).content
        
        return reasoning_result
    

