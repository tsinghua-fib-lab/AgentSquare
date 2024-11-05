import json

Reasoning_example = {#这里改成自己的module模版
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Your code here
            return reasoning_result
"""
}

#下面是各模块的一些具体例子,thought是该模块的特性和大致描述，name是名字, module type是模块类型，code是IO标准化后的代码

#这里的七个改成自己的module模版
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # Variables: task_description(str) represents the ongoing task
            prompt = f'''
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            
            return reasoning_result
    """,
    "performance": "50%"
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # The key to COT is the prompt addition of "solve the task step by step". "Your instructions should follow the examples." can make the large language model more consistent with the format output in the examples.
            # Variables: task_description(str) represents the ongoing task.
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            return reasoning_result
    """,
    "performance": "54%"
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # Variables: task_description(str) represents the ongoing task
            prompt = f'''Solve the task step by step. Interact with a household to solve a task. Your instructions should follow the examples.
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
    "performance": "49%"
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified.
            # Variables: task_description(str) represents the ongoing task.
            prompt = f'''Solve the task step by step. Interact with a scienceworld environment to solve a task. Your instructions should follow the examples.
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            # The key to TOT is to call llm multiple times, generate multiple inference paths, and then evaluate them by voting to choose the best path. Return: reasoning_results: list[str]
            reasoning_results = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'], n=3)
            # Call the vote function, pick the inference path with the most votes.
            # Remember you can call this function directly, and I'll write it in the program. Arguments: task_description: str, reasoning_results: list[str], Return: reasoning_result: str
            reasoning_result = get_votes(task_description, reasoning_results)
            return reasoning_result
    """,
    "performance": "57%"
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # Variables: task_description(str) represents the ongoing task.
            prompt = f'''Solve the task step by step. Interact with a scienceworld environment to solve a task. Your instructions should follow the examples.
    Here is the task:
    {task_description}'''
            # Invoke the large language model
            # The key to Self_Refine is reflecting on its previous attempts and incorporating feedback, the model can refine its reasoning and provide a more accurate solution
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            # Call the refine function and get the result of self-reflection improvement
            # Remember when you want to refine your answer, you can call this function directly, and I'll write it in the program. Arguments: task_description: str, reasoning_result: str Return: reasoning_result: str
            reasoning_result = refine(task_description, reasoning_result)
            return reasoning_result
    """,
    "performance": "50%"
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
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            # The key to Dilu is to add a system prompt that makes it act like an expert, such as a domestic robot
            prompt = [
                {
                    "role": "system",
                    "content": '''You are ChatGPT, a large language model trained by OpenAI. Now you act as a mature scienceworld robot, who can give accurate and correct instruction in interacting with a scienceworld environment. You will be given a detailed description of the scenario of current frame along with your history of previous decisions. 
    '''
                },
                {
                    "role": "user",
                    "content": f'''Your instructions should follow the examples.
    Here is the task:
    {task_description}'''
                }
            ]
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            return reasoning_result
    """,
    "performance": "46%"
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
            self.principle = ''
        def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
            # Set the memory and tooluse to '', do not modify this part
            memory = ''
            tooluse = ''
            # This task only stepback in the first step of the subtask, if you need to call stepback, remember to add this judgment statement
            if self.principle == '':
                # The key to Stepback is to let LLM first think about the principles involved in solving this task which could be helpful
                # Remember you can call this function directly, and I'll write it in the program. Arguments: task_description: str Return: principle: str
                self.principle = stepback(task_description)
            # Prompt word for invoking llm, you can modify it, but the {} content cannot be modified
            prompt = f'''Solve the task step by step. Interact with a scienceworld environment to solve a task.
    Here is the task:
    {task_description}
    The common sense and instruction structure involved in solving this task is:
    {self.principle}
    '''
            # Invoke the large language model
            reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            return reasoning_result
    """,
    "performance": "46%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview 
You are an expert machine learning researcher testing various LLM agents. Your objective is to design reasoning modules such as prompts and control flows within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations). \
Your aim is to design an agent with optimal reasoning module performing well on scienceworld (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ).

# Task Overview: 
ScienceWorld is a complex interactive text environment that poses a significant challenge to agents' scientific commonsense. This environment requires agents to navigate through 8 distinct functional rooms (e.g., workshop, kitchen) and utilize the tools to complete tasks such as 'measure the melting point of the orange juice'.
To solve this task, you need to first decompose the task using the planning module. Reasoning and memory modules are then used to solve each subtask. This requires strong command following, as well as common sense reasoning.

# A task solving trajectory from Scienceworld, The reasoning module outputs one action at a time after 'ACTION:' : 
Task Description: Your task is to boil water. For compounds without a boiling point, combusting the substance is also acceptable. First, focus on the substance. Then, take actions that will cause it to change its state of matter.\n\nACTION: look around\nOBSERVATION: This room is called the hallway. In it, you see: \n\ta picture\n\ta substance called air\n\tthe agent\nYou also see:\n\tA door to the green house (that is open)\n\tA door to the living room (that is open)\n\tA door to the art studio (that is open)\n\tA door to the kitchen (that is open)\n\tA door to the bedroom (that is open)\n\tA door to the workshop (that is open)\n\nACTION: open door to kitchen\nOBSERVATION: The door is already open.\n\nACTION: go to kitchen\nOBSERVATION: You move to the kitchen.\n\nACTION: look around\nOBSERVATION: This room is called the kitchen. In it, you see: \n\ta substance called soap\n\ta painting\n\ta thermometer, currently reading a temperature of 10 degrees celsius\n\ta counter. On the counter is: a bowl (containing a banana, a potato, a red apple, an orange), a drawer.\n\ta sink, which is turned off. In the sink is: nothing.\n\ta table. On the table is: a glass cup (containing nothing).\n\ta chair. On the chair is: nothing.\n\ta freezer. The freezer door is closed. \n\ta lighter\n\ta stopwatch, which is deactivated. \n\ta fridge. The fridge door is closed. \n\ta substance called air\n\ta cupboard. The cupboard door is closed. \n\ta oven, which is turned off. The oven door is closed. \n\ta glass jar (containing a substance called sodium chloride)\n\tthe agent\n\ta stove, which is turned off. On the stove is: nothing.\nYou also see:\n\tA door to the outside (that is open)\n\tA door to the bathroom (that is open)\n\tA door to the hallway (that is open)\n\nACTION: pick up thermometer\nOBSERVATION: You move the thermometer to the inventory.\n\nACTION: open cupboard\nOBSERVATION: The cupboard is now open.\n\nACTION: pick up metal pot\nOBSERVATION: You move the metal pot to the inventory.\n\nACTION: move metal pot to sink\nOBSERVATION: You move the metal pot to the sink.\n\nACTION: activate sink\nOBSERVATION: The sink is now activated.\n\nACTION: deactivate sink\nOBSERVATION: The sink is now deactivated.\n\nACTION: pick up metal pot\nOBSERVATION: You move the metal pot to the inventory.\n\nACTION: focus on substance in metal pot\nOBSERVATION: You focus on the water.\n\nACTION: pick up metal pot\nOBSERVATION: You move the metal pot to the inventory.\n\nACTION: move metal pot to stove\nOBSERVATION: You move the metal pot to the stove.\n\nACTION: activate stove\nOBSERVATION: The stove is now activated.\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 13 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 20 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 28 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 38 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 48 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 58 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 68 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 78 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 88 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 98 degrees celsius\n\nACTION: examine steam\nOBSERVATION: a substance called steam\n\nACTION: use thermometer in inventory on steam\nOBSERVATION: the thermometer measures a temperature of 107 degrees celsius\n\nACTION: wait1\nOBSERVATION: You decide to wait for 1 iterations.\n
# Reasoning module utility code:这里改成自己的模块模版
```python
class REASONING():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        # Class initialization, do not modify this part
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        # Set the memory and tooluse to '', do not modify this part
        memory = ''
        tooluse = ''
        # currect task
        task_description = task_description
        '''
         Fill in your code here.
         '''
        return reasoning_result
# Task detail description:
Variables:
task_description(str) represents the ongoing task = 'Your task is to boil water. For compounds without a boiling point, combusting the substance is also acceptable. First, focus on the substance. Then, take actions that will cause it to change its state of matter.\n\nACTION: look around\nOBSERVATION: This room is called the hallway. In it, you see: \n\ta picture\n\ta substance called air\n\tthe agent\nYou also see:\n\tA door to the green house (that is open)\n\tA door to the living room (that is open)\n\tA door to the art studio (that is open)\n\tA door to the kitchen (that is open)\n\tA door to the bedroom (that is open)\n\tA door to the workshop (that is open)\n\nACTION: open door to kitchen\nOBSERVATION: The door is already open.\n\n'

The expected next reasoning module output is 'go to kitchen'. In order to accomplish this task, you must ensure that the output format is consistent with the example while you are reasoning, so you should pay attention to adding examples when writing prompts, and drive the output format of the large language model to be consistent with the example.
```

# Discovered architecture archive
Here is the archive of the discovered reasoning module architectures:

[ARCHIVE]

The performance represents the completion rate of the task. 

The "generation" number indicates the sequential order of attempts made in designing the architecture. Each generation represents a distinct iteration or version, reflecting the evolution and refinement of the design.

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next interesting agent to try, then describe your reasoning and the overall concept behind the agent design, and finally detail the implementation steps.
The second key ("name") corresponds to the name of your next agent architecture. 
Finally, the last key ("code") corresponds to the exact module function in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next agent architecture:

[Reasoning_example]

You must strictly follow the exact input/output interface used above. You need to specify the instruction, input information, and the required output fields for various LLM agents to do their specific part of the architecture.  Also, it could be helpful to set the LLM's role and temperature to further control the LLM's response. DON'T try to use some function that doesn't exist. In __call__(), you need to specify the instruction, input information, and the required output fields for various LLM agents to do their specific part of the architecture. 

# Your task 
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new reasoning module including prompts and control flows.
Observe the discovered agents carefully and think about what insights, lessons, or stepping stones can be learned from them.
Be creative when thinking about the next interesting agent to try. You are encouraged to draw inspiration from related agent papers or academic papers from other research areas.
Use the knowledge from the archive and inspiration from academic literature to propose the next interesting agentic system design.
For the directly callable function methods mentioned in the inference module example, you can call them directly and do not need to define them. If you need to create new function methods, you need to make sure that the function is complete and runnable.
You need to learn as much as possible from well-performed reasoning modules.
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

def get_prompt_reasoning(current_archive, adaptive=False):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Reasoning_example]", json.dumps(Reasoning_example))

    return system_prompt, prompt


def get_init_archive_reasoning():  #初始agent代码：Module-level搜索到的最好组合
    return [reasoning_IO, reasoning_CoT, reasoning_CoT_SC, reasoning_ToT, reasoning_self_refine, reasoning_Dilu, reasoning_Stepback]

#搜索过程中如果创造的新代码有问题，调用反思让其重写，这里可以根据具体实施过程中容易出现的bug加一些典型错误例子供其参考
def get_reflexion_prompt(prev_example):
    prev_example_str = "Here is the previous agent you tried:\n" + json.dumps(prev_example) + "\n\n"
    r1 = Reflexion_prompt.replace("[EXAMPLE]", prev_example_str) if prev_example else Reflexion_prompt.replace("[EXAMPLE]", "")
    return r1
# You need to pay special attention to the requirements mentioned in the "Task detail description" to ensure that the output of the task is formatted.