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
            few_shot = planning_prompt[task_type]
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): two task planning trajectory. task_description(str): current task.
            if feedback == '':
                prompt = '''You are a planner who divides a {task_type} task into several subtasks.
        '''
        Fill in your prompt here.
        '''
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Task: {task_description}
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a planner who divides a {task_type} task into several subtasks.
        '''
        Fill in your prompt here.
        '''
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Task:{task_description}
    '''
                    prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self. plan = dicts
            return self.plan
"""
}


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
            few_shot = planning_prompt[task_type]
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): two task planning trajectory. task_description(str): current task. Do not add new {} content.
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
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "40%"
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
            few_shot = planning_prompt[task_type]
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): two task planning trajectory. task_description(str): current task. Do not add new {} content.
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
                
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # String parsing, do not modify this part.
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            dicts = [ast.literal_eval(ds) for ds in dict_strings]
            self.plan = dicts
            return self.plan
    """,
    "performance": "38%"
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
            few_shot = planning_prompt[task_type]
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): two task planning trajectory. task_description(str): current task. Do not add new {} content.
            if feedback == '':
                prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Task: {task_description}
    '''
                prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
            else:
                prompt = '''You are a planner who divides a {task_type} task into several subtasks. Think step by step about all the tasks needed to resolve the user's request. Parse out as few tasks as possible while ensuring that the user request can be resolved. Pay attention to the dependencies and order among tasks. you also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Task:{task_description}
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
    "performance": "39%"
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
            few_shot = planning_prompt[task_type]
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): two task planning trajectory. task_description(str): current task. Do not add new {} content.
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
    Task:{task_description}
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
    "performance": "41%"
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
            few_shot = planning_prompt[task_type]
            # The prompt words of the planning module, the difference between different modules is also mainly here, is the place where you need to focus on modification. task_type(str): current task type. example(str): two task planning trajectory. task_description(str): current task. Do not add new {} content.
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
    task:{task_description}
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
    "performance": "30%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview
You are an expert machine learning researcher testing various LLM agents. Your objective is to design planning modules such as prompts within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations).
Your aim is to design an agent with optimal planning module performing well on ALFworld (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ).

# Task Overview:
ALFworld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).
To solve this task, you need to first decompose the task using the planning module. Reasoning and memory modules are then used to solve each subtask.

# A task planning trajectory from Alfworld:
Task description: You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.     \nYour task is to: put a clean lettuce in diningtable.
Planning module output:
sub-task 1: {{'description': 'First I need to find and take a lettuce', 'reasoning instruction': 'Find and take a lettuce', 'tool use instruction': None}}
sub-task 2: {{'description': 'Next, I need to clean it with sinkbasin', 'reasoning instruction': 'Clean the lettuce with sinkbasin', 'tool use instruction': None}}
sub-task 3: {{'description': 'Finally, I need to put it in diningtable', 'reasoning instruction': 'Go to diningtable and put the lettuce in diningtable', 'tool use instruction': None}}

# Planning module utility code:
```python
import re
import ast
from utils import llm_response
from planning_prompt import *

class PLANNING_IO():
    def __init__(self, llms_type):
        self. plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        few_shot = planning_prompt[task_type]
        if feedback == '':
            prompt = '''
    '''
    Fill in your prompt here.
    '''
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    Task: {task_description}
'''
            prompt = prompt.format(example=few_shot, task_description=task_description, task_type=task_type)
        else:
            prompt = '''
    '''
    Fill in your prompt here.
    '''
    Your output format should follow the example below.
    The following are some examples:
    Task: {example}

    end
    --------------------
    Reflexion:{feedback}
    Task:{task_description}
'''
                prompt = prompt.format(example=few_shot, task_description = task_description, task_type=task_type, feedback = feedback)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self. plan = dicts
        return self.plan
# Tsak detail description:
We need to write prompt words to allow the llm to decompose the task as in the examples:
examples(str) contain planning module output examples = '''You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.     \nYour task is to: put a clean lettuce in diningtable.
sub-task 1: {{'description': 'First I need to find and take a lettuce', 'reasoning instruction': 'Find and take a lettuce', 'tool use instruction': None}}
sub-task 2: {{'description': 'Next, I need to clean it with sinkbasin', 'reasoning instruction': 'Clean the lettuce with sinkbasin', 'tool use instruction': None}}
sub-task 3: {{'description': 'Finally, I need to put it in diningtable', 'reasoning instruction': 'Go to diningtable and put the lettuce in diningtable', 'tool use instruction': None}} '''
```

# Discovered architecture archive
Here is the archive of the discovered planning module architectures:

[ARCHIVE]

The performance represents the completion rate of the task.

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next interesting agent to try, then describe your planning module.
The second key ("name") corresponds to the name of your next agent architecture.
Finally, the last key ("code") corresponds to the planning module in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next agent architecture:

[Planning_example]

You must strictly follow the exact input/output interface used above. Also, it could be helpful to set the LLM's role and temperature to further control the LLM's response. DON'T try to use some function that doesn't exist.

# Your task
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new planning module including prompts.
Observe the discovered planning modules carefully and think about what insights, lessons, or stepping stones can be learned from them.
THINK OUTSIDE THE BOX.
"""

def get_prompt_planning(current_archive):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Planning_example]", json.dumps(Planning_example))

    return system_prompt, prompt

def get_init_archive_planning(): 
    return [planning_IO, planning_DEPS, planning_HUGGINGGPT, planning_openagi, planning_voyage]
