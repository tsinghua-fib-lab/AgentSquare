import os
import re
import ast
from utils import get_chat, get_completion, get_price
#from prompt import *

class IOPLANNING():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. 
The robot has four actions: pickup, putdown, stack, and unstack. The domain assumes a world where there are a set of blocks that can be stacked on top of each other, an arm that can hold one block at a time, and a table where blocks can be placed.\n    The actions defined in this domain include:\n    pickup <block>: allows the arm to pick up a block from the table if it is clear and the arm is empty. After the pickup action, the arm will be holding the block, and the block will no longer be on the table or clear.\n    putdown <block>: allows the arm to put down a block on the table if it is holding a block. After the putdown action, the arm will be empty, and the block will be on the table and clear.\n    stack <block> <block>: allows the arm to stack a block on top of another block if the arm is holding the top block and the bottom block is clear. After the stack action, the arm will be empty, the top block will be on top of the bottom block, and the bottom block will no longer be clear.\n    unstack <block> <block>: allows the arm to unstack a block from on top of another block if the arm is empty and the top block is clear. After the unstack action, the arm will be holding the top block, the top block will no longer be on top of the bottom block, and the bottom block will be clear.
Your output format should follow the example below.
The following are some examples:
task: Goal: The goal is to satisfy the following conditions: b1 is on b2., b2 is on b3.\nObservation: B1 is on the table. B2 is on the table. B3 is on the table. Robot arm is empty. The b1 is clear. The b2 is clear. The b3 is clear.
sub-task 1: {{'description': 'I need to stack b2 on b3 first', 'reasoning instruction': 'b2 is on b3', 'tool use instruction': None}}
sub-task 2: {{'description': 'Then I need to stack b1 on b2', 'reasoning instruction': 'b1 is on b2', 'tool use instruction': None}}

task: {task_description}
'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. 
The robot has four actions: pickup, putdown, stack, and unstack. The domain assumes a world where there are a set of blocks that can be stacked on top of each other, an arm that can hold one block at a time, and a table where blocks can be placed.\n    The actions defined in this domain include:\n    pickup <block>: allows the arm to pick up a block from the table if it is clear and the arm is empty. After the pickup action, the arm will be holding the block, and the block will no longer be on the table or clear.\n    putdown <block>: allows the arm to put down a block on the table if it is holding a block. After the putdown action, the arm will be empty, and the block will be on the table and clear.\n    stack <block> <block>: allows the arm to stack a block on top of another block if the arm is holding the top block and the bottom block is clear. After the stack action, the arm will be empty, the top block will be on top of the bottom block, and the bottom block will no longer be clear.\n    unstack <block> <block>: allows the arm to unstack a block from on top of another block if the arm is empty and the top block is clear. After the unstack action, the arm will be holding the top block, the top block will no longer be on top of the bottom block, and the bottom block will be clear.
Your output format should follow the example below.
The following are some examples:
task: Goal: The goal is to satisfy the following conditions: b1 is on b2., b2 is on b3.\nObservation: B1 is on the table. B2 is on the table. B3 is on the table. Robot arm is empty. The b1 is clear. The b2 is clear. The b3 is clear.
sub-task 1: {{'description': 'I need to stack b2 on b3 first', 'reasoning instruction': 'Stack b2 on b3', 'tool use instruction': None}}
sub-task 2: {{'description': 'Then I need to stack b1 on b2', 'reasoning instruction': 'Stack b1 on b2', 'tool use instruction': None}}

#Requirement: If your output contains ' 'or ', change the outermost ' ' to " ".In short, in the case of quotation marks nesting, please change the way of the outermost quotation marks to distinguish it from the middle quotation marks. Example 1: {'description': "I need to compare the life spans of all the animals in the 'outside' location", 'reasoning instruction': 'Focus on the animal with the longest life span', 'tool use instruction': None} Example 2:{'description': "Increase the ice's temperature using the blast furnace or stove", 'reasoning instruction': 'Need to change the state of matter of the ice', 'tool use instruction': 'stack ice blast_furnace OR stack ice stove'}.

end
--------------------
reflexion:{feedback}
task:{task_description}
'''
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)
        if self.engine == 'gpt-3.5-turbo-instruct':
            string = get_completion(prompt=prompt, model=self.llm_type, temperature=0.1)
        else:
            string = get_chat(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r'\{[^{}]*\}', string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

        
