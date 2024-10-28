import os
import re
import ast
from utils_llm import llm_response, get_price

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
class PLANNING_IO():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        # one_shot = planning_prompt['scienceworld']
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

Here is the current task:
Task: {task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

end
--------------------
Reflexion:{feedback}
Here is the current task:
Task:{task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

class PLANNING_DEPS():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = '''You are a helper AI agent in planning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

Here is the current task:
task: {task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks, each of which is relevant, necessary, and valid, and you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

end
--------------------
reflexion:{feedback}
Here is the current task:
task:{task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

class PLANNING_HUGGINGGPT():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user"s request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

Here is the current task:
task: {task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user"s request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

end
--------------------
reflexion:{feedback}
Here is the current task:
task:{task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

class PLANNING_OPENAGI():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

Here is the current task:
task: {task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.
Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

end
--------------------
reflexion:{feedback}
Here is the current task:
task:{task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)

        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)

        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

class PLANNING_VOYAGE():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = '''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of subgoals that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

Here is the current task:
task: {task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of subgoals that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
The following are some examples:
task: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

end
--------------------
reflexion:{feedback}
Here is the current task:
task:{task_description}

# Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

'''
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

