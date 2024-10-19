import re
from utils import llm_response

class REASONING_HYBRID_TOT_SC_SELFREFINE():
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
        prompt = '''{tooluse}Solve the task step by step. Your output must follow the examples process.  Don't refine your search. You have to choose one from a list of items.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache, tooluse=tooluse)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=3)
        from collections import Counter
        string_counts = Counter(reasoning_results)
        best_path = string_counts.most_common(1)[0][0]
        refined_result = self.refine(best_path)
        return refined_result
    def refine(self, reasoning_result):
        prompt = f'''You need to check that the syntactic structure of the step meets the requirements.
requirements: 1. search[] 2. click[] 3. : think[]
examples:
search[roasted coffee beans dairy free cinnamon bun flavored]  correct
think[For a light weight a34 color photo background, the item has options '9x6ft | 2.7x1.8m' and 'a34' and seems good to buy.]  correct
click[a34]  correct
click[Buy Now]  correct
click[dairy free]  correct
Click[dairy free]  error, revised: click[dairy free]  correct
Just focus on syntactic structure.
step: {reasoning_result}
You can only output in two formats:
"correct" or "error, revised:"
'''     
        feedback_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.0)
        if 'correct' in feedback_result.lower():
            return reasoning_result
        else:
            return feedback_result.split(':')[-1]