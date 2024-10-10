import re
import ast
from utils import llm_response
from planning_prompt import *

class TemporalDependencyPlanner():
    def __init__(self, llms_type):
        # Initialization of the class, do not modify this part
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        # Assign few_shot based on the task type, do not modify this part.
        few_shot = planning_prompt[task_type]
        # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification.
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks with explicit temporal dependencies.
Consider the order of actions and their dependencies to ensure logical sequencing.
Your output format must follow the example below, specifying the order and dependencies.
The following are some examples:
Task: {example}

Task: {task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks with explicit temporal dependencies.
Consider the order of actions and their dependencies to ensure logical sequencing.
Your output format should follow the example below, specifying the order and dependencies.
The following are some examples:
Task: {example}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)
        # Invoke the large language model
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        # String parsing, do not modify this part.
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

