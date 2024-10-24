from utils import llm_response

class TOOLUSE_TEMPLATE():
    def __init__(self, llms_type):
        # Initialization of the class
        self.llm_type = llms_type[0]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        # Import the tool pool based on the task
        tool_pool
        # Design prompt
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
        # Call the llm 
        tooluse_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1) 
        return tooluse_result