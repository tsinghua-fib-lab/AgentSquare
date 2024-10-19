from utils import llm_response
from collections import Counter
class REASONING_COT():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        task_description = task_description
        if self.memory is not None:
            memory = self.memory('')
        else:
            memory = ''
        prompt = '''Solve the task step by step
{memory}
{task_description}'''
        prompt = prompt.format(task_description=task_description, memory=memory)
        reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=5)
        string_counts = Counter(reasoning_results)
        reasoning_result = string_counts.most_common(1)[0][0]
        return reasoning_result