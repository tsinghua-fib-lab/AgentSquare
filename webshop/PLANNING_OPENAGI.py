import re
import ast
from utils import llm_response

class PLANNING_OPENAGI():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = f'''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output must follow the example below.
The following are some examples:
Task: I would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
sub-task 1: {{'description': 'I first need to do a search to find items that might qualify.', 'reasoning instruction': 'Search based on attributes other than price.', 'tool use instruction': None}}
sub-task 2: {{'description': 'Then I need to find the most suitable item in the item list.', 'reasoning instruction': 'Find the most qualified item in the item list.', 'tool use instruction': None}}
sub-task 3: {{'description': 'Finally, I need to click the attributes of the selected item and decide to buy it.', 'reasoning instruction': 'Click the attributes of the selected item and  buy it.', 'tool use instruction': None}}

Task: {task_description}
'''
        else:
            prompt = f'''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output format should follow the example below.
The following are some examples:
Task: I would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
sub-task 1: {{'description': 'I first need to do a search to find items that might qualify.', 'reasoning instruction': 'Identify search terms including 3 ounce bottle, bright citrus deodorant and sensitive skin.', 'tool use instruction': None}}
sub-task 2: {{'description': 'Then I need to find the most suitable item in the item list.', 'reasoning instruction': 'Select the most suitable products', 'tool use instruction': None}}
sub-task 3: {{'description': 'Finally, I need to determine the attributes of the selected item and decide to buy it.', 'reasoning instruction': 'Click product attributes and purchase.', 'tool use instruction': None}}

end
--------------------
Reflexion:{feedback}
Task:{task_description}
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        string = re.sub(r"(?<=\d)'|'(?=\d)", r"\'", string)
        pattern = r"([a-zA-Z])'([a-zA-Z])"
        string = re.sub(pattern, r"\1\'\2", string)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

        
