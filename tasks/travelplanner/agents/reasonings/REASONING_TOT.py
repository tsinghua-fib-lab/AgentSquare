import re
from utils_llm import llm_response, get_price
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import os

class REASONING_TOT():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= '',stop_list = ['\n']):
        memory = ''
        tooluse = ''
        prompt = '''Solve the task step by step
{memory}
{tooluse}
Here is the task:
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=stop_list,n=5)
        reasoning_result = self.get_votes(task_description, reasoning_results, stop_list)
        return reasoning_result
    def get_votes(self, task_description, reasoning_results, stop_list):
        print('TOT is running...')
        prompt = '''Given a task and several answers, decide which answer is most promising.  Analyze each choice in detail, then conclude in the last line "The best choice is {{s}}", where s the integer id of the choice.
Here is the current task:
{task_description}
'''     
        prompt = prompt.format(task_description=task_description)
        for i, y in enumerate(reasoning_results, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=1,stop_strs = stop_list,n=5)
        vote_results = [0] * len(reasoning_results)
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(len(reasoning_results)):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
        ids = list(range(len(reasoning_results)))
        select_id = sorted(ids, key=lambda x: vote_results[x], reverse=True)[0]
        return reasoning_results[select_id]
        
