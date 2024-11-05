import json

Planning_example = {
    "thought": "**Insights:**\nYour insights on what should be the next interesting planning module for agents.\n**Overall Idea:**\nyour planning module description.\n**Implementation:**\ndescribe the implementation.",
    "module type": "planning",
    "name": "Name of your proposed planning module",
    "code": """
    class [Name of your proposed planning module]():
        def __init__(self, llms_type):
        # Initialization of the class, do not modify this part
            self. plan = []
            self.llm_type = llms_type[0]
        def __call__(self, task_type, task_description, feedback):
            # Assign few_shot based on the task type, do not modify this part.
            few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): task planning trajectory. task_description(str): current task.
            if feedback == '':
                prompt = '''You are a planner who divides a {task_type} task into several subtasks.
        Fill in your prompt here.
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}
    Here is the current task:
    Task: {task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a planner who divides a {task_type} task into several subtasks.
        Fill in your prompt here.
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Here is the current task:
    Task:{task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"

    '''
                    prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
"""
}

#下面是各模块的一些具体例子,thought是该模块的特性和大致描述，name是名字, module type是模块类型，code是IO标准化后的代码

planning_IO = {
    "thought":"Input the task description to a LLM and directly output the sub-tasks",
    "name": "Standard IO planning",
    "module type": "planning",
    "code": """
    class PLANNING_IO():
        # Initialization of the class, do not modify this part
        def __init__(self, llms_type):
            self.plan = []
            self.llm_type = llms_type[0]
        def __call__(self, task_type, task_description, feedback):
            # Assign few_shot based on the task type, do not modify this part.
            few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): task planning trajectory. task_description(str): current task. Do not add new {} content.
            if feedback == '':
                prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}
    Here is the current task:
    Task: {task_description}
    
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a planner who divides a {task_type} task into several subtasks. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Here is the current task:
    Task:{task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "50%"
}

planning_DEPS = {
    "thought":"Input a task description in a LLM and output sub-goals. It is commonly used for embodied intelligence tasks.",
    "name": "DEPS",
    "module type": "planning",
    "code": """
    class PLANNING_DEPS():
        # Initialization of the class, do not modify this part
        def __init__(self, llms_type):
            self.plan = []
            self.llm_type = llms_type[0]
        def __call__(self, task_type, task_description, feedback):
            # Assign few_shot based on the task type, do not modify this part.
            few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): task planning trajectory. task_description(str): current task. Do not add new {} content.
            if feedback == '':
                prompt = '''You are a helper AI agent in reasoning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Here is the current task:
    Task: {task_description}

    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a helper AI agent in reasoning. You need to generate the sequences of sub-goals (actions) for a {task_type} task in multi-hop questions. You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Here is the current task:
    Task:{task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "52%"
}

planning_HUGGINGGPT = {
    "thought":"Input a task description into a LLM and output as few sub-tasks as possible. It is often used for image processing tasks and focuses on the correlation between sub-tasks.",
    "name": "hugginggpt",
    "module type": "planning",
    "code": """
    class PLANNING_HUGGINGGPT():
        # Initialization of the class, do not modify this part
        def __init__(self, llms_type):
            self.plan = []
            self.llm_type = llms_type[0]
        def __call__(self, task_type, task_description, feedback):
            # Assign few_shot based on the task type, do not modify this part.
            few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): task planning trajectory. task_description(str): current task. Do not add new {} content.
            if feedback == '':
                prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Here is the current task:
    Task: {task_description}

    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Here is the current task:
    Task:{task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "48%"
}

planning_openagi = {
    "thought": "Input a task description in a LLM and output a to-do list. It is often used to solve tasks using various tools",
    "name": "openagi",
    "module type": "planning",
    "code": """
    class PLANNING_OPENAGI():
        # Initialization of the class, do not modify this part
        def __init__(self, llms_type):
            self.plan = []
            self.llm_type = llms_type[0]
        def __call__(self, task_type, task_description, feedback):
            # Assign few_shot based on the task type, do not modify this part.
            few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): task planning trajectory. task_description(str): current task. Do not add new {} content.
            if feedback == '':
                prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
    For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
    Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
    Develop a concise to-do list to achieve the objective.  
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Here is the current task:
    Task: {task_description}

    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
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
    Here is the current task:
    Task:{task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "45%"
}

planning_voyage = {
    "thought":"Input a task description in a LLM and output sub-goals.  It is often used to solve open world exploration problems",
    "name": "voyage",
    "module type": "planning",
    "code": """
    class PLANNING_VOYAGE():
        # Initialization of the class, do not modify this part
        def __init__(self, llms_type):
            self.plan = []
            self.llm_type = llms_type[0]
        def __call__(self, task_type, task_description, feedback):
            # Assign few_shot based on the task type, do not modify this part.
            few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): task planning trajectory. task_description(str): current task. Do not add new {} content.
            if feedback == '':
                prompt = '''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
    I'll give you a final task, you need to decompose the task into a list of subgoals.
    You must follow the following criteria:
    1) Return a  list of subgoals that can be completed in order to complete the specified task.
    2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
    You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Here is the current task:
    Task: {task_description}

    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
    I'll give you a final task, you need to decompose the task into a list of subgoals.
    You must follow the following criteria:
    1) Return a  list of subgoals that can be completed in order to complete the specified task.
    2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
    You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    reflexion:{feedback}
    Here is the current task:
    task:{task_description}
    # Requirement: In the generated answer, if there is a nested case of ''or', change the outside ' to ". Example 1: "{{'description': 'I need to compare the life spans of all the animals in the 'outside' location'}}" to "{{'description': "I need to compare the life spans of all the animals in the 'outside' location"}}", example 2: Replace "{{'description': 'I need to raise the ice's temperature'}}" with "{{'description': "I need to raise the ice's temperature'}}"
    '''
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "46%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview
You are an expert machine learning researcher testing various LLM agents. Your objective is to design planning modules such as prompts within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations).
Your aim is to design an agent with optimal planning module performing well on scienceworld (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ).

# Task Overview:
ScienceWorld is a complex interactive text environment that poses a significant challenge to agents' scientific commonsense. This environment requires agents to navigate through 8 distinct functional rooms (e.g., workshop, kitchen) and utilize the tools to complete tasks such as 'measure the melting point of the orange juice'.
To solve this task, you need to first decompose the task using the planning module. Reasoning and memory modules are then used to solve each subtask.

# A task planning trajectory from scienceworld:
Task description: Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
Planning module output:
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}

# Planning module utility code:
```python
import re
import ast
from utils import llm_response

class PLANNING_IO():
    def __init__(self, llms_type):
        self. plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = '''
Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}
'''
        if feedback == '':
            prompt = '''
    Fill in your prompt here.
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}
    
    Here is the current task:
    Task: {task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
        else:
            prompt = '''
    Fill in your prompt here.
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Here is the current task:
    Task:{task_description}
'''
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self. plan = dicts
        return self.plan
# Task detail description:
We need to write prompt words to allow the llm to decompose the task as in the examples:
examples(str) contain planning module output examples = '''Your task is to determine if a metal fork is electrically conductive.The metal fork is located around the kitchen.
sub-task 1: {{'description': "I first need to get into the kitchen.", 'reasoning instruction': "Look around and find the way to the kitchen", 'tool use instruction': "None"}}
sub-task 2: {{'description': "Then I need to find the metal fork and pick it up.", 'reasoning instruction': "Look around for the metal fork.", 'tool use instruction': "None"}}
sub-task 3: {{'description': "Then I need to navigate to room with electrical components", 'reasoning instruction': "Look around and find the way to room with electrical components", 'tool use instruction': "None"}}
sub-task 4: {{'description': "Finally, I need to find something I can use to test electrical conductivity.", 'reasoning instruction': "Look around, find an item that can measure electrical conductivity, and use it to measure the electrical conductivity of the metal fork.", 'tool use instruction': "None"}}'''
```

# Discovered architecture archive
Here is the archive of the discovered planning module architectures:

[ARCHIVE]

The performance represents the completion rate of the task.

The "generation" number indicates the sequential order of attempts made in designing the architecture. Each generation represents a distinct iteration or version, reflecting the evolution and refinement of the design.

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next interesting agent to try, then describe your planning module. 
The second key ("name") corresponds to the name of your next agent architecture.
Finally, the last key ("code") corresponds to the planning module in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next agent architecture:

[Planning_example]

You must strictly follow the exact input/output interface used above. Also, it could be helpful to set the LLM's role and temperature to further control the LLM's response.   DON'T try to use some function that doesn't exist.

# Your task
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new planning module including prompts.
Observe the discovered planning modules carefully and think about what insights, lessons, or stepping stones can be learned from them.
You only need to design prompts for the planning module.
THINK OUTSIDE THE BOX.
"""

Reflexion_prompt = f""""[EXAMPLE]Carefully review the proposed new architecture and reflect on the following points:"

1. **Interestingness**: Assess whether your proposed architecture is interesting or innovative compared to existing methods in the archive. If you determine that the proposed architecture is not interesting, suggest a new architecture that addresses these shortcomings. 
- Make sure to check the difference between the proposed architecture and previous attempts.
- Compare the proposal and the architectures in the archive CAREFULLY, including their actual differences in the implementation.
- Decide whether the current architecture is innovative.
- USE CRITICAL THINKING!

2. **Implementation Mistakes**: Identify any mistakes you may have made in the implementation. Review the code carefully, debug any issues you find, and provide a corrected version.

3. **Improvement**: Based on the proposed architecture, suggest improvements in the detailed implementation that could increase its performance or effectiveness. In this step, focus on refining and optimizing the existing implementation without altering the overall design framework, except if you want to propose a different architecture if the current is not interesting.
- Observe carefully about whether the implementation is actually doing what it is supposed to do.
- Check if there is redundant code or unnecessary steps in the implementation. Replace them with effective implementation.
- Try to avoid the implementation being too similar to the previous agent.

And then, you need to improve or revise the implementation, or implement the new proposed architecture based on the reflection.

Your response should be organized as follows:

"reflection": Provide your thoughts on the interestingness of the architecture, identify any mistakes in the implementation, and suggest improvements.

"thought": Revise your previous proposal or propose a new architecture if necessary, using the same format as the example response.

"name": Provide a name for the revised or new architecture. (Don't put words like "new" or "improved" in the name.)

"code": Provide the corrected code or an improved implementation. Make sure you actually implement your fix and improvement in this code.
"""

def get_prompt_planning(current_archive, adaptive=False):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Planning_example]", json.dumps(Planning_example))

    return system_prompt, prompt


def get_init_archive_planning():  #初始agent代码：Module-level搜索到的最好组合
    return [planning_IO, planning_DEPS, planning_HUGGINGGPT, planning_openagi, planning_voyage]

#搜索过程中如果创造的新代码有问题，调用反思让其重写，这里可以根据具体实施过程中容易出现的bug加一些典型错误例子供其参考
def get_reflexion_prompt(prev_example):
    prev_example_str = "Here is the previous agent you tried:\n" + json.dumps(prev_example) + "\n\n"
    r1 = Reflexion_prompt.replace("[EXAMPLE]", prev_example_str) if prev_example else Reflexion_prompt.replace("[EXAMPLE]", "")
    return r1
# You need to pay special attention to the requirements mentioned in the "Task detail description" to ensure that the output of the task is formatted.