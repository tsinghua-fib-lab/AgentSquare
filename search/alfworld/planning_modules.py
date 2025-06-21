import re
import ast
from utils import llm_response
from planning_prompt import *

class PlanningBase():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        # raise NotImplementedError("Subclasses should implement this method")
        pass
    
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt[task_type]
        prompt = self.create_prompt(task_type, task_description, feedback, few_shot)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan
    
class PlanningIO(PlanningBase):
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

Task: {task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)
        return prompt

class PlanningDEPS(PlanningBase):
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        if feedback == '':
            prompt = '''You are a helper AI agent in reasoning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

Task: {task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a helper AI agent in reasoning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)
        return prompt

class PlanningTD(PlanningBase):
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks with explicit temporal dependencies.
Consider the order of actions and their dependencies to ensure logical sequencing.
Your output format must follow the example below, specifying the order and dependencies.
The following are some examples:
Task: {example}

Task: {task_description}
'''
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
        return prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)

class PlanningVoyager(PlanningBase):
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        if feedback == '':
            prompt = '''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of subgoals that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

Task: {task_description}
'''
        else:
            prompt = '''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a list of subgoals that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

end
--------------------
reflexion:{feedback}
task:{task_description}
'''
        return prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)

class PlanningOPENAGI(PlanningBase):
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        if feedback == '':
            prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output format should follow the example below.
The following are some examples:
Task: {example}

Task: {task_description}
'''
        else:
            prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.
Your output format should follow the example below.
The following are some examples:
Task: {example}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        return prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)

class PlanningHUGGINGGPT(PlanningBase):
    def create_prompt(self, task_type, task_description, feedback, few_shot):
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

Task: {task_description}
'''
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {example}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        return prompt.format(example=few_shot, task_description=task_description, task_type=task_type, feedback=feedback)


