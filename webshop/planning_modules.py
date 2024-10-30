import re
import ast
from utils import llm_response
from planning_prompt import *
"""
class PlanningTemplate():
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
"""

class PlanningIO():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt['online_shopping']
        if feedback == '':
            prompt = f'''You are a planner who divides a {task_type} task into three subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: {few_shot}

Task: {task_description}
'''
        else:
            prompt = f'''You are a planner who divides a {task_type} task into three subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: {few_shot}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        string = re.sub(r"(?<=\d)'|'(?=\d)", r"\'", string)
        pattern = r"([a-zA-Z])'([a-zA-Z])"
        string = re.sub(pattern, r"\1\'\2", string)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan
        
class PlanningDEPS():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt['online_shopping']
        if feedback == '':
            prompt = f'''You are a helper AI agent in reasoning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: {few_shot}

Task: {task_description}
'''
        else:
            prompt = f'''You are a helper AI agent in reasoning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: {few_shot}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        string = re.sub(r"(?<=\d)'|'(?=\d)", r"\'", string)
        pattern = r"([a-zA-Z])'([a-zA-Z])"
        string = re.sub(pattern, r"\1\'\2", string)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan
    
class PlanningVoyager():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt['online_shopping']
        if feedback == '':
            prompt = f'''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of sub-tasks that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: {few_shot}

Task: {task_description}
'''
        else:
            prompt = f'''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of subgoals that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {few_shot}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        string = re.sub(r"(?<=\d)'|'(?=\d)", r"\'", string)
        pattern = r"([a-zA-Z])'([a-zA-Z])"
        string = re.sub(pattern, r"\1\'\2", string)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

class PlanningOPENAGI():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt['online_shopping']
        if feedback == '':
            prompt = f'''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output must follow the example below.
The following are some examples:
Task: {few_shot}

Task: {task_description}
'''
        else:
            prompt = f'''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output format should follow the example below.
The following are some examples:
Task: {few_shot}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        string = re.sub(r"(?<=\d)'|'(?=\d)", r"\'", string)
        pattern = r"([a-zA-Z])'([a-zA-Z])"
        string = re.sub(pattern, r"\1\'\2", string)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

class PlanningHUGGINGGPT():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt['online_shopping']
        if feedback == '':
            prompt = f'''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: {few_shot}

Task: {task_description}
'''
        else:
            prompt = f'''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
Task: {few_shot}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        string = re.sub(r"(?<=\d)'|'(?=\d)", r"\'", string)
        pattern = r"([a-zA-Z])'([a-zA-Z])"
        string = re.sub(pattern, r"\1\'\2", string)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan
