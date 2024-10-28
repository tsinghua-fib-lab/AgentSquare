import os
from utils_llm import llm_response, get_price
from collections import Counter
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


class REASONING_COT_SC():
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
        # if self.memory is not None:
        #     memory = self.memory('')
        # else:
        memory = ''
        # if self.tooluse is not None:
        #     tooluse = self.tooluse(task_description, tool_instruction, feedback)
        # else:
        tooluse = ''
        prompt = f'''Solve the task step by step
{memory}
{tooluse}
Here is the current task:
{task_description}'''
        # reasoning_results = [llm([HumanMessage(content=prompt)]).content for i in range(5)]
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list,n=5)
        string_counts = Counter(reasoning_results)
        reasoning_result = string_counts.most_common(1)[0][0]
        return reasoning_result
        
