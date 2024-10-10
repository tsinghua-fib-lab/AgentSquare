import json

Tooluse_example = {
    "thought": "**Insights:**\nYour insights on what should be the next interesting tooluse module for agents.\n**Overall Idea:**\nyour tooluse module description.\n**Implementation:**\ndescribe the implementation.",
    "module type": "tooluse",
    "name": "Name of your proposed tooluse module",
    "code": """
    class TOOLUSE_IO():
        # Initialization of the class
        def __init__(self, llms_type):
            self.llm_type = llms_type[0]
        def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
            '''
            Fill in your code here.
            '''
            return string
"""
}

tooluse_IO = {
    "thought":"Input the task description to a tool use module and directly output the response",
    "name": "IO",
    "module type": "tooluse",
    "code": """
    class TOOLUSE_IO():
        # Initialization of the class
        def __init__(self, llms_type):
            self.llm_type = llms_type[0]
        def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
            # tool_pool contains tools that can be called
            tool_pool = tooluse_IO_pool.get(task_description)
            # Prompt word for invoking llm. Identify the tool based on the tool instruction. Do not modify this prompt.
            prompt = f'''You have access to the following tools:
    {tool_pool}
    You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
    {tool_instruction}
    You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
    You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
    You can only invoke one tool at a time.
    You should begin your tool invocation with 'Action:' and end it with 'End Action'.
    Your tool invocation format must follow the invocation format in the tool description.
    {feedback_of_previous_tools}
    '''        
            # Invoke the large language model
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1) 
            return string
    """,
    "performance": "25%"
}

tooluse_Anytool = {
    "thought":"Select the tool category based on the task description, and then select the specific tool.",
    "name": "Anytool",
    "module type": "tooluse",
    "code": """
    class TOOLUSE_ANYTOOL():
        def __init__(self, llms_type):
            # Initialization of the class
            self.llm_type = llms_type[0]
        def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
            # dicts includes different categories of tools, and each category has corresponding tool sets. 
            # Remember you can call tool_category directly, and I'll write it in the program.
            dicts = tool_category()
            # The key to any tool is hierarchical search: first, identify the category of the tool based on the tool instruction, and then find the specific tool within that category.
            # Prompt word for invoking llm. Identify the category of the tool based on the tool instruction. Do not modify this prompt.
            prompt = f'''{dicts[task_description]}
    You need to select the appropriate tool category from the list of available tools according to the task description to complete the task: 
    {tool_instruction}
    You can only invoke one category at a time.
    Completed steps: {feedback_of_previous_tools}
    You need to think about what tools do you need next.
    Output category name directly.
    Your output should be of the following format:
    Category name: 
    '''
            # Invoke the large language model
            # Analyze the selected category name and output the tool set for that category. Do not modify this part.
            category_name = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1).split(':')[-1].strip()
            matching_dict = None
            for d in self.dicts[task_description]:
                if d.get('category name').lower().strip() in category_name.lower().strip():
                    matching_dict = d
                    break
            if matching_dict is not None:
                matched_tools = {tool: self.tool_description[task_description][tool] for tool in matching_dict['tool list'] if tool in self.tool_description[task_description]}
            else:
                matched_tools = self.tool_description[task_description]
            # Prompt word for invoking llm. Identify the tool based on the tool instruction. Do not modify this prompt.
            prompt = f'''You have access to the following tools:
    {matched_tools}
    You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
    {tool_instruction}
    You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
    You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
    You can only invoke one tool at a time.
    You should begin your tool invocation with 'Action:' and end it with 'End Action'.
    Your tool invocation format must follow the invocation format in the tool description.
    {feedback_of_previous_tools}
    '''
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # Invoke the large language model
            return string
    """,
    "performance": "22%"
}

tooluse_Toolbench = {
    "thought":"Convert the instructions and API documentation into vector representations, and then retrieve the most relevant API by calculating the vector similarity.",
    "name": "Toolbench",
    "module type": "tooluse",
    "code": """
    class TOOLUSE_TOOLBENCH():
        def __init__(self, llms_type):
            self.llm_type = llms_type[0]
        def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
            # scenario_memory is a vector database that contains various tools.
            scenario_memory = tool_database()
            # Find the most relevant tools from the database based on the tool instruction.
            similarity_results = self.scenario_memory[task_description].similarity_search_with_score(tool_instruction, k=4)
            tool_pool = []
            for idx in range(0, len(similarity_results)):
                tool_pool.append(similarity_results[idx][0].metadata['description'])
            # Prompt word for invoking llm. Identify the tool based on the tool instruction. Do not modify this prompt.
            prompt = f'''
    You have access to the following tools:
    {tool_pool}
    You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
    {tool_instruction}
    You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
    You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
    You can only invoke one tool at a time.
    You should begin your tool invocation with 'Action:' and end it with 'End Action'.
    Your tool invocation format must follow the invocation format in the tool description.
    {feedback_of_previous_tools}
    '''
            string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            # Invoke the large language model
            return string
    """,
    "performance": "28%"
}

tooluse_Toolformer = {
    "thought": "Determine the best response using an LLM by inputting the problem description into a tool-use module, performing three selections, and directly outputting the best one.",
    "name": "Toolformer",
    "module type": "tooluse",
    "code": """
    class TOOLUSE_TOOLFORMER():
        def __init__(self, llms_type):
            # Initialization of the class
            self.llm_type = llms_type[0]
        def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
            # tool_pool contains tools that can be called
            tool_pool = tooluse_IO_pool.get(task_description)
            # Prompt word for invoking llm. Identify the tool based on the tool instruction.  Do not modify this prompt.
            prompt = f'''You have access to the following tools:
    {tool_pool}
    You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
    {tool_instruction}
    You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
    You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
    You can only invoke one tool at a time.
    You should begin your tool invocation with 'Action:' and end it with 'End Action'.
    Your tool invocation format must follow the invocation format in the tool description.
    {feedback_of_previous_tools}
    '''        
            # Invoke the large language model
            # The key to Toolformer is to call llm multiple times, generate multiple answers, and then evaluate them by voting to choose the best answer. Return: strings: list[str]
            strings = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, n=3) 
            # Call the vote function, pick the inference path with the most votes.
            # Remember you can call this function directly, and I'll write it in the program.
            string = get_votes(tool_pool, tool_instruction, feedback_of_previous_tools, strings)
            return string
    """,
    "performance": "26%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview 
You are an expert machine learning researcher testing various LLM agents. Your objective is to design tool-use modules such as prompts and control flows within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations).
Your aim is to design an agent with optimal tool-use module performing well on M3ToolEval (a tool-use benchmarks contain complex tasks requiring the composition of multiple tools including web browsing, finance, travel itinerary planning, science, and information processing).

# Task Overview: 
M3ToolEval is a tool-use benchmarks contain complex tasks requiring the composition of multiple tools. It evaluates LLMs' capabilities in solving complex tasks that typically require multiple calls to multiple tools in multi-turn interactions.

# A task solving trajectory from M3tool: 
You have access to the following tools:
[1] find_flights: Finds flights based on source, destination and date. Arguments: from_location (str), to_location (str), date (str) in YYYY-MM-DD format.
Returns a list of flights, each represented as a dictionary with keys "from_location", "to_location" (destination), "date", and "price".
Example: [{"from_location": "A", "to_location": "B", "date": "2023-12-25", "price": 450}]
    Signature: find_flights(destination: str, date: str) -> List[Dict]
[2] book_hotel: Books a hotel based on location and preferences. Arguments: location (str), *preferences (variable number of str arguments).
Returns a list of hotels, each represented as a dictionary with keys "location", "preferences", "price_per_night", and "rating".
Example: [{"location": "A", "preferences": ["wifi", "pool"], "price_per_night": 120, "rating": 4}]
    Signature: book_hotel(location: str, *preferences: str) -> List[Dict]
[3] budget_calculator: Calculates the total budget for a trip. Arguments: flight_price (float), hotel_price_per_night (float), num_nights (int).
Returns the total budget (float).
    Signature: budget_calculator(flight_price: float, hotel_price_per_night: float, num_nights: int) -> float
[4] max: Finds the maximum value among the given arguments. Accepts variable number of float arguments.
    Signature: max(*args: float) -> float
[5] min: Finds the minimum value among the given arguments. Accepts variable number of float arguments.
    Signature: min(*args: float) -> float
[6] sum: Sums the given arguments. Accepts variable number of float arguments.
    Signature: sum(*args: float) -> float
You can use the tools by outputing the tool name followed by its arguments, delimited by commas.
Instruction: You are at "E". Plan a trip to "A" on 2023-12-25, staying in a hotel with wifi and a pool for 5 nights. Give me the total budget for the trip.
Thought: I need to find a flight from "E" to "A" on 2023-12-25, book a hotel in "A" with wifi and a pool for 5 nights, and then calculate the total budget for the trip.
Action: find_flights, E, A, 2023-12-25 End Action
[{'from_location': '"E"', 'to_location': '"A"', 'date': '2023-12-25', 'price': 450}]
Action: book_hotel, A, wifi, pool End Action
[{'location': '"A"', 'preferences': ['wifi', 'pool'], 'price_per_night': 120, 'rating': 4}, {'location': '"A"', 'preferences': ['wifi', 'pool'], 'price_per_night': 50, 'rating': 3}]
Action: budget_calculator, 450, 120, 5 End Action
1050
Answer: 1050

# Tool-use module utility code:
```python
import os
import re
import ast 
from utils import llm_response
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from tooluse_IO_pool import *
class TOOLUSE_IO():
    def __init__(self, llms_type):
        self.llm_type = llms_type[0]
        '''
        Fill in your code here.
        '''
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        '''
        Fill in your code here.
        '''
        return string
```

# Discovered architecture archive
Here is the archive of the discovered tool-use module architectures:

[ARCHIVE]

The performance represents the completion rate of the task. 

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next interesting agent to try, then describe your tool-use module. 
The second key ("name") corresponds to the name of your next tool-use module architecture.
Finally, the last key ("code") corresponds to the tool-use module in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next  tool-use module architecture:

[Tool-use_example]

You must strictly follow the exact input/output interface used above.  Also, it could be helpful to set the LLM’s role and temperature to further control the LLM’s response. DON'T try to use some function that doesn't exist. In __call__(), you need to specify the instruction, input information, and the required output fields for various LLM agents to do their specific part of the architecture. 

# Your task 
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new tool-use module including prompts and control flows.
Observe the discovered agents carefully and think about what insights, lessons, or stepping stones can be learned from them.
Be creative when thinking about the next interesting agent to try. You are encouraged to draw inspiration from related agent papers or academic papers from other research areas.
Use the knowledge from the archive and inspiration from academic literature to propose the next interesting agentic system design.
For the directly callable function methods mentioned in the tool-use module example, you can call them directly and do not need to define them.
You need to learn as much as possible from well-performed tool-use modules.
Don't make it too complicated.

"""
def get_prompt_tooluse(current_archive):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Tool-use_example]", json.dumps(Tooluse_example))

    return system_prompt, prompt


def get_init_archive_tooluse():
    return [tooluse_Anytool, tooluse_IO, tooluse_Toolbench, tooluse_Toolformer]