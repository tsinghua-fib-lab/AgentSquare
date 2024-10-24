from utils import llm_response

class REASONING_TEMPLATE():
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
        examples = examples
        # Design prompt
        prompt = '''Your output must follow the examples.
{memory}{examples}
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache)
        # Call the llm 
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        
        return reasoning_result
    
