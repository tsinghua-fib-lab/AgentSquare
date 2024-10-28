import os
import json
from utils_llm import llm_response, get_price

class TOOLUSE_IO():
    def __init__(self, llms_type):
        self.tool_base = []
        self.llm_type = llms_type[0]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        prompt = f'''
The tool pools is NONE, which means there is no tool to use.
You need to select the appropriate tool from the list of available tools according to the task description to complete the task: {task_description}
{tool_instruction}
You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can only invoke one tool at a time.
You should begin your tool invocation with 'Action:' and end it with 'End Action'.
{feedback_of_previous_tools}
Your output should be of the following format
'Action: tool_name, argument_1, argument_2 End Action'
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        print(string)
        return string


