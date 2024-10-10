import re
import ast 
from utils import llm_response
from tooluse_IO_pool import tooluse_IO_pool
class TOOLUSE_ANYTOOL():
    def __init__(self, llms_type):
        self.dicts = {}
        self.tool_description = {}
        self.llm_type = llms_type[0]
        for name, tools in tooluse_IO_pool.items():
            pattern = r'\[\d+\] (\w+): (.+?)(?=\[\d+\]|\Z)'
            matches = re.findall(pattern, tools, re.DOTALL)
            self.tool_description[name] = {key: value.strip() for key, value in matches}
            category_prompt = f'''{self.tool_description[name]}
    You have a series of tools, you need to divide them into several categories, such as data calculation, trip booking and so on.
    All tools should be included in categories.
    your output format must be as follows:
    category 1 : {{'category name': 'category description', 'tool list': ['tool 1 name', 'tool 2 name']}}
    category 2 : {{'category name': 'category description', 'tool list': ['tool 1 name', 'tool 2 name']}}
    '''
            string = llm_response(prompt=category_prompt, model=self.llm_type, temperature=0.1)
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            self.dicts[name] = [ast.literal_eval(ds) for ds in dict_strings]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        prompt = f'''{self.dicts[task_description]}
You need to select the appropriate tool category from the list of available tools according to the task description to complete the task: 
{tool_instruction}
You can only invoke one category at a time.
Completed steps: {feedback_of_previous_tools}
You need to think about what tools do you need next.
Output category name directly.
Your output must be of the following format:
Category name: 
'''
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
        return string