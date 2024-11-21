import json

Reasoning_example = {
    "thought": "**Insights:**\nYour insights on what should be the next interesting reasoning module for agents.\n**Overall Idea:**\nyour reasoning and the overall concept behind the agent design.\n**Implementation:**\ndescribe the implementation step by step.",
    "module type": "reasoning",
    "name": "Name of your proposed reasoning module",
    "code": """
    class [Name of your proposed reasoning module]():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Your code here
            return reasoning_result
"""
}

reasoning_IO = {
    "thought":"Directly reason with problem as input and output the reasoning results",
    "name": "Standard IO Reasoning",
    "module type": "reasoning",
    "code": """
    class REASONING_IO():
            # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # Variables: tooluse(str) is empty, self.memory_cache(str) contains a similar task solving trajectory, examples(str) contain two task resolution trajectory examples, task_description(str) represents the ongoing task
            prompt = f'''Interact with a household to solve a task.{tooluse}
    Here are some examples.
    {examples}{self.memory_cache}
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            
            return reasoning_result
    """,
    "performance": "41%"
}

reasoning_CoT = {
    "thought":"By encouraging the LLM to think step by step rather than directly outputting an answer, chain-of-thought reasoning enables complex problem-solving through intermediate steps. This practice improves the model's ability to handle tasks that require deeper reasoning and provides insight into its decision-making process.",
    "name": "Chain-of-Thought",
    "module type": "reasoning",
    "code": """
    class REASONING_COT():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # The key to COT is the prompt addition of "solve the task step by step". "Your instructions should follow the examples." can make the large language model more consistent with the format output in the examples.
            # Variables: tooluse(str) is empty, self.memory_cache(str) contains a similar task solving trajectory, examples(str) contain two task resolution trajectory examples, task_description(str) represents the ongoing task.
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.{tooluse}
    Here are some examples.
    {examples}{self.memory_cache}
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            return reasoning_result
    """,
    "performance": "48%"
}

reasoning_CoT_SC = {
    "thought":"While an LLM can arrive at the correct answer, its reasoning may vary. By repeatedly asking the same question with high temperature settings, we can generate different reasoning paths. We then combine multiple answers from these Chain-of-Thought (CoT) agents to produce a more accurate final answer through ensembling.",
    "name": "Self-Consistency with Chain-of-Thought",
    "module type": "reasoning",
    "code": """
    class REASONING_COT_SC():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # Variables: tooluse(str) is empty, self.memory_cache(str) contains a similar task solving trajectory, examples(str) contain two task resolution trajectory examples, task_description(str) represents the ongoing task
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.{tooluse}
    Here are some examples.
    {examples}{self.memory_cache}
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            # The key to COT-SC is to call the llm multiple times, answering according to its self-consistency. "n = 5" means that the results of 5 requests will be returned. Return: reasoning_results: list[str]
            reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=5)
            # Import the cllections packages to find the most common answers
            from collections import Counter
            string_counts = Counter(reasoning_results)
            reasoning_result = string_counts.most_common(1)[0][0]
            return reasoning_result
    """,
    "performance": "50%"
}

reasoning_ToT = {
    "thought": "Generalize over 'Chain-of-Thought', by considering multiple different reasoning paths and self-evaluating choices to decide the next course of action, as well as looking ahead or backtracking when necessary to make global choices",
    "name": "Tree-of-Thoughts",
    "module type": "reasoning",
    "code": """
    class REASONING_TOT():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified.
            # Variables: tooluse(str) is empty, self.memory_cache(str) contains a similar task solving trajectory, examples(str) contain two task resolution trajectory examples, task_description(str) represents the ongoing task.
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.{tooluse}
    Here are some examples.
    {examples}{self.memory_cache}
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            # The key to TOT is to call llm multiple times, generate multiple inference paths, and then evaluate them by voting to choose the best path. Return: reasoning_results: list[str]
            reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=3)
            # Call the vote function, pick the inference path with the most votes.
            # Remember you can call this function directly, and I'll write it in the program. Arguments: task_description: str, reasoning_results: list[str], , examples: str Return: reasoning_result: str
            reasoning_result = get_votes(task_description, reasoning_results, , examples)
            return reasoning_result
    """,
    "performance": "51%"
}

reasoning_self_refine = {
    "thought":"To enhance its performance, an LLM can iteratively improve its answer based on feedback. By reflecting on its previous attempts and incorporating feedback, the model can refine its reasoning and provide a more accurate solution.",
    "name": "Self_Refine",
    "module type": "reasoning",
    "code": """
    class REASONING_SELF_REFINE():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # Variables: tooluse(str) is empty, self.memory_cache(str) contains a similar task solving trajectory, examples(str) contain two task resolution trajectory examples, task_description(str) represents the ongoing task.
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.{tooluse}
    Here are some examples.
    {examples}{self.memory_cache}
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            # The key to Self_Refine is reflecting on its previous attempts and incorporating feedback, the model can refine its reasoning and provide a more accurate solution
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            # Call the refine function and get the result of self-reflection improvement
            # Remember when you want to refine your answer, you can call this function directly, and I'll write it in the program. Arguments: reasoning_result: str Return: reasoning_result: str
            reasoning_result = refine(reasoning_result)
            return reasoning_result
    """,
    "performance": "48%"
}

reasoning_Dilu = {
    "thought":"Role-playing can better guide large language models to solve specific domain problems",
    "name": "Dilu",
    "module type": "reasoning",
    "code": """
    class REASONING_DILU():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # The key to Dilu is to add a system prompt that makes it act like an expert, such as a domestic robot
            prompt = [
                {
                    "role": "system",
                    "content": '''You are ChatGPT, a large language model trained by OpenAI. Now you act as a mature domestic robot, who can give accurate and correct instruction in interacting with a household. You will be given a detailed description of the scenario of current frame along with your history of previous decisions. 
    '''
                },
                {
                    "role": "user",
                    "content": f'''Above messages are some examples of how you make a step successfully in the past. Those scenarios are similar to the current scenario. You should refer to those examples to make a step for the current scenario. Your instructions should follow the examples.{tooluse}
    Here are two examples.
    {examples}{self.memory_cache}
    Here is the task:
    {task_description}'''
                }
            ]
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            return reasoning_result
    """,
    "performance": "37%"
}

reasoning_Stepback = {
    "thought":"Let LLM first think about the principles involved in solving this task which could be helpful. By understanding the underlying principles, the model can better reason through the problem and provide a more accurate solution.",
    "name": "Stepback",
    "module type": "reasoning",
    "code": """
    class REASONING_STEPBACK():
        # Initialization of the class, do not modify this part
        def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
            self.feedback = ''
            self.profile_type_prompt = profile_type_prompt
            self.memory = memory
            self.llm_type = llms_type[0]
            self.tooluse = tooluse
            self.task_name_cache = None
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
            # Call tools use modules and memory modules, do not modify this part
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)
            if self.memory is not None:
                if self.task_name_cache is not None and self.task_name_cache == task_name:
                    pass
                else:
                    self.task_name_cache = task_name
                    self.memory_cache = self.memory(task_description)
            else:
                self.memory_cache = ''
            if self.tooluse is not None:
                tooluse = self.tooluse(task_description, tool_instruction)
            else:
                tooluse = ''
            # Split into two parts, on is the task soleution track example, the other is the current task
            split_text = task_description.rsplit('You are in the', 1)
            # task solution track examples
            examples = split_text[0]
            # currect task
            task_description = 'You are in the' + split_text[1]
            # This task only stepback in the first step of the subtask, if you need to call stepback, remember to add this judgment statement
            if task_description.split('Your')[-1].count('>') == 1:
                # The key to Stepback is to let LLM first think about the principles involved in solving this task which could be helpful
                # Remember you can call this function directly, and I'll write it in the program. Arguments: task_description: str Return: principle: str
                self.principle = stepback(task_description)
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.{tooluse}
    Here are some examples.
    {examples}{self.memory_cache}
    Here is the task:
    {self.principle}
    {task_description}'''
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            return reasoning_result
    """,
    "performance": "44%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview
You are an expert machine learning researcher testing various LLM agents. Your objective is to design reasoning modules such as prompts and control flows within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations). \
Your aim is to design an agent with optimal reasoning module performing well on ALFworld (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ).

# Task Overview:
ALFworld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).
To solve this task, you need to first decompose the task using the planning module. Reasoning and memory modules are then used to solve each subtask. This requires strong command following, as well as common sense reasoning.

# A task solving trajectory from Alfworld, The reasoning module outputs one step at a time after '>' : 
You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.\nYour task is to: put a clean lettuce in diningtable.\n> think: To solve the task, I need to find and take a lettuce, then clean it with sinkbasin, then put it in diningtable. \nOK.\n> think: First I need to find a lettuce. A lettuce is more likely to appear in fridge (1), diningtable (1), sinkbasin (1), stoveburner (1-3), cabinet (1-13). I can check one by one, starting with fridge 1.\nOK.\n> go to fridge 1\nThe fridge 1 is closed.\n> open fridge 1\nYou open the fridge 1. The fridge 1 is open. In it, you see a cup 3, a egg 2, a potato 3, and a potato 2.\n> go to diningtable 1\nOn the diningtable 1, you see a apple 1, a bread 1, a butterknife 2, a cup 2, a fork 2, a knife 2, a knife 1, a ladle 1, a lettuce 1, a mug 2, a mug 1, a pan 2, a peppershaker 1, a spatula 3, a tomato 2, and a tomato 1.\n> think: Now I find a lettuce (1). Next, I need to take it.\nOK.\n> take lettuce 1 from diningtable 1\nYou pick up the lettuce 1 from the diningtable 1.\n> think: Now I take a lettuce (1). Next, I need to go to sinkbasin (1) and clean it.\nOK.\n> go to sinkbasin 1\nOn the sinkbasin 1, you see a apple 2, a ladle 2, a spoon 1, and a tomato 3.\n> clean lettuce 1 with sinkbasin 1\nYou clean the lettuce 1 using the sinkbasin 1.\n> think: Now I clean a lettuce (1). Next, I need to put it in/on diningtable 1.\nOK.\n> go to diningtable 1\nOn the diningtable 1, you see a apple 1, a bread 1, a butterknife 2, a cup 2, a fork 2, a knife 2, a knife 1, a ladle 1, a mug 2, a mug 1, a pan 2, a peppershaker 1, a spatula 3, a tomato 2, and a tomato 1.\n> put lettuce 1 in/on diningtable 1\nYou put the lettuce 1 in/on the diningtable 1.\n
# Reasoning Module Template:
```python
class REASONING():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        # Class initialization, do not modify this part
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        self.task_name_cache = None
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str=''):
        # Call tools use modules and memory modules, do not modify this part
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)
        if self.memory is not None:
            if self.task_name_cache is not None and self.task_name_cache == task_name:
                pass
            else:
                self.task_name_cache = task_name
                self.memory_cache = self.memory(task_description)
        else:
            self.memory_cache = ''
        if self.tooluse is not None:
            tooluse = self.tooluse(task_description, tool_instruction)
        else:
            tooluse = ''
        # Split into two parts, on is the task soleution track example, the other is the current task
        split_text = task_description.rsplit('You are in the', 1)
        # task solution track examples
        examples = split_text[0]
        # currect task
        task_description = 'You are in the' + split_text[1]
        '''
        Fill in your code here.
        '''
        return reasoning_result
# Tsak detail description:
Variables:
examples(str) contain task resolution trajectory examples = 'You are in the middle of a room. Looking quickly around you, you see a bathtubbasin 1, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.\nYour task is to: Now I take a soapbottle (2), end.go to garbagecan and put the soapbottle in garbagecan.\n> think: I need to put it in/on garbagecan 1.\nOK.\n> go to garbagecan 1\nOn the garbagecan 1, you see nothing.\n> put soapbottle 2 in/on garbagecan 1, end\nYou put the soapbottle 2 in/on the garbagecan 1.\n'
task_description(str) represents the ongoing task = 'You are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.\nYour task is to: Now I take a spraybottle (2), end.go to toilet and put the spraybottle on toilet.\n> think: I need to put it in/on toilet 1.\nOK.\n> '

The expected next reasoning module output is 'go to toilet 1'. In order to accomplish this task, you must ensure that the output format is consistent with the example while you are reasoning, so you should pay attention to adding examples when writing prompts, and drive the output format of the large language model to be consistent with the example.
```

# Discovered architecture archive
Here is the archive of the discovered reasoning module architectures:

[ARCHIVE]

The performance represents the completion rate of the task. 

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next interesting agent to try, then describe your reasoning and the overall concept behind the agent design, and finally detail the implementation steps.
The second key ("name") corresponds to the name of your next agent architecture. 
Finally, the last key ("code") corresponds to the exact module function in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next agent architecture:

[Reasoning_example]

You must strictly follow the exact input/output interface used above. Also, it could be helpful to set the LLM’s role and temperature to further control the LLM’s response. DON'T try to use some function that doesn't exist. In __call__(), you need to specify the instruction, input information, and the required output fields for various LLM agents to do their specific part of the architecture. 

# Your task
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new reasoning module including prompts and control flows.
Observe the discovered agents carefully and think about what insights, lessons, or stepping stones can be learned from them.
Be creative when thinking about the next interesting agent to try. You are encouraged to draw inspiration from related agent papers or academic papers from other research areas.
Use the knowledge from the archive and inspiration from academic literature to propose the next interesting agentic system design.
For the directly callable function methods mentioned in the inference module example, you can call them directly and do not need to define them. If you need to create new function methods, you need to make sure that the function is complete and runnable.
You need to learn as much as possible from well-performed reasoning modules.
THINK OUTSIDE THE BOX.

"""

def get_prompt_reasoning(current_archive):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Reasoning_example]", json.dumps(Reasoning_example))

    return system_prompt, prompt

def get_init_archive_reasoning():
    return [reasoning_IO, reasoning_CoT, reasoning_CoT_SC, reasoning_ToT, reasoning_self_refine, reasoning_Dilu, reasoning_Stepback]

