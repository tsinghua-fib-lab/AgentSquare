from utils_llm import llm_response
from collections import Counter
import re

"""
class ReasoningTemplate():
    def __init__(self, profile_type_prompt, memory, llms_type):
        # Initialization of the class
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
    def __call__(self, task_description: str, feedback :str= ''):
        # Whether to call the memory module
        if self.memory is not None:
            self.memory_cache = self.memory(task_description)
        else:
            self.memory_cache = ''
        # few-shot
        examples
        # Design prompt
        prompt = '''Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        # Call the llm 
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        
        return reasoning_result
"""

class REASONING_IO():
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
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        
        return reasoning_result
    
class REASONING_COT():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        memory = ''
        tooluse = ''
        prompt = '''Solve the task step by step. Interact with a scienceworld environment to solve a task. Your instructions should follow the examples.
{memory}
{tooluse}
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        
        return reasoning_result

class REASONING_COT_SC():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        memory = ''
        tooluse = ''
        prompt = f'''Solve the task step by step
{memory}
{tooluse}
{task_description}'''
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=['\n'],n=5) 
        string_counts = Counter(reasoning_results)
        reasoning_result = string_counts.most_common(1)[0][0]
        return reasoning_result

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

class REASONING_STEPBACK():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        self.principle = ''
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        memory = ''
        tooluse = ''
        if self.principle == '':#这个任务只在子任务的第一步进行stepback
            self.principle = self.stepback(task_description)
            
        prompt = f'''Solve the task step by step. Interact with a scienceworld environment to solve a task. 
Here is the task:
{task_description}
The common sense and instruction structure involved in solving this task is:
{self.principle}
{memory}
{tooluse}
'''
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
       
        return reasoning_result
    def stepback(self, task_description):
        stepback_prompt = f'''What common sense, instruction structure is involved in solving this task?
{task_description}'''
        principle = llm_response(prompt=stepback_prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return principle

class REASONING_TOT():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        memory = ''
        tooluse = ''
        prompt = '''Solve the task step by step
{memory}
{tooluse}
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory, tooluse=tooluse)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=1, stop_strs=['\n'],n=5) 
        reasoning_result = self.get_votes(task_description, reasoning_results)
        return reasoning_result
    def get_votes(self, task_description, reasoning_results):
        prompt = '''Given a task and several answers, decide which answer is most promising.  Analyze each choice in detail, then conclude in the last line "The best choice is {{s}}", where s the integer id of the choice.
{task_description}
'''     
        prompt = prompt.format(task_description=task_description)
        for i, y in enumerate(reasoning_results, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=1,n=5) 
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

