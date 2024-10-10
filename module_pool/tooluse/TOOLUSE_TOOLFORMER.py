import re
from utils import llm_response
from tooluse_IO_pool import tooluse_IO_pool
class TOOLUSE_TOOLFORMER():
    def __init__(self, llms_type):
        self.llm_type = llms_type[0]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        tool_pool = tooluse_IO_pool.get(task_description)
        
        prompt = f'''You have access to the following tools:
{tool_pool}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
{tool_instruction}
You must use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
You can only invoke one tool at a time.
You must begin your tool invocation with 'Action:' and end it with 'End Action'.
Your tool invocation format must follow the invocation format in the tool description.
{feedback_of_previous_tools}
'''        
        strings = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, n=3) 
        string = self.get_votes(tool_pool, tool_instruction, feedback_of_previous_tools, strings)
        return string
    def get_votes(self, tool_pool, tool_instruction, feedback_of_previous_tools, strings):
        prompt = f'''You have access to the following tools:
{tool_pool}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
{tool_instruction}
You must use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
You can only invoke one tool at a time.
You must begin your tool invocation with 'Action:' and end it with 'End Action'.
Your tool invocation format must follow the invocation format in the tool description.
{feedback_of_previous_tools}
------------
Given several answers, decide which answer is most promising. Output "The best answer is {{s}}", where s the integer id of the choice.
'''     
        for i, y in enumerate(strings, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=0.3, n=5)
        vote_results = [0] * len(strings)
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(len(strings)):
                    vote_results[vote] += 1
            else:
                pass
        ids = list(range(len(strings)))
        select_id = sorted(ids, key=lambda x: vote_results[x], reverse=True)[0]
        return strings[select_id]