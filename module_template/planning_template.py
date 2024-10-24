import re
import ast
from utils import llm_response

class PLANNING_IO():
    def __init__(self, llms_type):
        # Initialization of the class
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        # Design prompt
        if feedback == '':
            prompt = f'''You are a planner who divides a {task_type} task into three subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.

Task: {task_description}
'''
        else:
            prompt = f'''You are a planner who divides a {task_type} task into three subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        # Call the llm
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        # Parse output
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

        
