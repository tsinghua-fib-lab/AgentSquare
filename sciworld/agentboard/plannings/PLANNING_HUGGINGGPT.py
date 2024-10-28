import os
import re
import ast
from utils_llm import llm_response, get_price

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

        
