from utils import llm_response
from collections import Counter
import re

class ReasoningBase:
    def __init__(self, profile_type_prompt, memory, llms_type):
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
    
    def process_task_description(self, task_description):
        task_name = re.findall(r'Instruction:\s+(.*?)\s+\[Search\]', task_description)
        if self.memory is not None:
            self.task_name_cache = task_name[1] if len(task_name) > 1 else None
            self.memory_cache = self.memory(task_description)
            if task_description.count('Reasoning') == 2:
                self.memory_cache = self.memory_cache.split('Observation')[0]
            elif task_description.count('Reasoning') == 4:
                self.memory_cache = 'Observation'.join(self.memory_cache.split('Observation')[0:3])
        else:
            self.memory_cache = ''
        
        split_text = task_description.rsplit('WebShop', 1)
        examples = split_text[0]
        task_description = 'WebShop' + split_text[1]
        
        return examples, task_description

class ReasoningIO(ReasoningBase):
    def __call__(self, task_description: str, feedback: str = ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        return llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])

class ReasoningCOT(ReasoningBase):
    def __call__(self, task_description: str, feedback: str = ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Solve the task step by step. Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        return llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])

class ReasoningCOTSC(ReasoningBase):
    def __call__(self, task_description: str, feedback: str = ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Solve the task step by step. Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=5)
        string_counts = Counter(reasoning_results)
        reasoning_result = string_counts.most_common(1)[0][0]
        return reasoning_result

class ReasoningTOT(ReasoningBase):
    def __call__(self, task_description: str, feedback :str= ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Solve the task step by step. Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=3)
        reasoning_result = self.get_votes(task_description, reasoning_results, examples)
        return reasoning_result
    def get_votes(self, task_description, reasoning_results, examples):
        if 'think'  in reasoning_results[0].lower():
            return reasoning_results[0]
        prompt = '''Given the process for one completed tasks and one ongoing task, and several answers for the next step, decide which answer best follows the process. Output "The best answer is {{s}}", where s is the integer id chosen.
Here are some examples.
{examples}
Here is the task:
{task_description}

'''     
        prompt = prompt.format(task_description=task_description, examples=examples)
        for i, y in enumerate(reasoning_results, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=0.3, n=5)
        vote_results = [0] * len(reasoning_results)
        for vote_output in vote_outputs:
            pattern = r".*best answer is .*(\d+).*"
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

class ReasoningDILU(ReasoningBase):
    def __call__(self, task_description: str, feedback :str= ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = [
            {
                "role": "system",
                "content": '''You are ChatGPT, a large language model trained by OpenAI. Now you act as a shopping expert, who can give accurate and correct instruction in shopping. You will be given a detailed description of the scenario of current frame along with your history of previous decisions. 
'''
            },
            {
                "role": "user",
                "content": f'''Above messages are some examples of how you make a step successfully in the past. Those scenarios are similar to the current scenario. You should refer to those examples to make a step for the current scenario. Your output must follow the examples.
{self.memory_cache}{examples}
{task_description}'''
            }
        ]
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return reasoning_result

class ReasoningSelfRefine(ReasoningBase):
    def __call__(self, task_description: str, feedback :str= ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Solve the task step by step. Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        reasoning_result = self.refine(reasoning_result)
        return reasoning_result
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

class ReasoningStepBack(ReasoningBase):
    def __call__(self, task_description: str, feedback :str= ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Solve the task step by step. Your output must follow the examples.
{memory}{examples}
{principle}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache, principle= self.principle)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return reasoning_result
    def stepback(self, task_description):
        stepback_prompt = f'''What common sense, instruction structure is involved in solving this task?
{task_description}'''
        principle = llm_response(prompt=stepback_prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return principle

class ReasoningHybridTOTSCSelfRefine(ReasoningBase):
    def __call__(self, task_description: str, feedback :str= ''):
        examples, task_description = self.process_task_description(task_description)
        prompt = '''Solve the task step by step. Your output must follow the examples process.  Don't refine your search. You have to choose one from a list of items.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
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
