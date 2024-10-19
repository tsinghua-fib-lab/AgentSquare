import re
from utils import llm_response
from collections import Counter

class REASONING_COT_SC():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        task_name = re.findall(r'Instruction:\s+(.*?)\s+\[Search\]', task_description)        
        if self.memory is not None:
            self.task_name_cache = task_name[1]
            self.memory_cache = self.memory(task_description)
            if task_description.count('Reasoning') == 2:
                self.memory_cache = self.memory_cache.split('Observation')[0]
            elif task_description.count('Reasoning') == 4:
                self.memory_cache = 'Observation'.join(self.memory_cache.split('Observation')[0:3])
            else:
                self.memory_cache = self.memory_cache
        else:
            self.memory_cache = ''
        if self.tooluse is not None:
            tooluse = self.tooluse(task_description, tool_instruction)
        else:
            tooluse = ''
        split_text = task_description.rsplit('WebShop', 1)
        examples = split_text[0]
        task_description = 'WebShop' + split_text[1]
        prompt = '''{tooluse}Solve the task step by step. Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache, tooluse=tooluse)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=5)
        string_counts = Counter(reasoning_results)
        reasoning_result = string_counts.most_common(1)[0][0]
        
        return reasoning_result
