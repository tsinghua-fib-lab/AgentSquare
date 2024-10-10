import re
from utils import llm_response

class REASONING_TOT():
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
        prompt = '''Solve the task step by step. Interact with a household to solve a task. Your instructions must follow the examples.{tooluse}
Here are some examples.
{examples}{memory}
Here is the task:
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache, tooluse=tooluse)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=3)
        reasoning_result = self.get_votes(task_description, reasoning_results, examples)
        return reasoning_result
    def get_votes(self, task_description, reasoning_results, examples):
        if 'think'  in reasoning_results[0].lower():
            return reasoning_results[0]
        prompt = '''Given the reasoning process for two completed tasks and one ongoing task, and several answers for the next step, decide which answer best follows the reasoning process for example command format. Output "The best answer is {{s}}", where s is the integer id chosen.
Here are some examples.
{examples}
Here is the task:
{task_description}

'''     
        prompt = prompt.format(task_description=task_description, examples=examples)
        for i, y in enumerate(reasoning_results, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=0.7, n=5)
        vote_results = [0] * len(reasoning_results)
        for vote_output in vote_outputs:
            pattern = r".*best answer is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(len(reasoning_results)):
                    vote_results[vote] += 1
            else:
                pass
        ids = list(range(len(reasoning_results)))
        select_id = sorted(ids, key=lambda x: vote_results[x], reverse=True)[0]
        return reasoning_results[select_id]
        
