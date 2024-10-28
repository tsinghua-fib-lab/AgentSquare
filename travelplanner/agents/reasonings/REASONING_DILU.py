import os
from utils_llm import llm_response, get_price
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

class REASONING_DILU():
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
        prompt = [
            {
                "role": "system",
                "content": '''You are ChatGPT, a large language model trained by OpenAI. Now you act as a mature travelplanner, who can give accurate and correct instruction in gathering information from travelplanner sandbox and make travel plans. You will be given a detailed description of the scenario of current frame. 
'''
            },
            {
                "role": "user",
                "content": f''' 
{memory}
{tooluse}
Here is the current task:
{task_description}
'''
            }
        ]
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list)
        # reasoning_result = llm([HumanMessage(content=prompt)]).content
        return reasoning_result

