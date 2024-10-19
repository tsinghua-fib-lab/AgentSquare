import re
import ast
from utils import llm_response

class PLANNING_VOYAGE():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = f'''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of sub-tasks that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output must follow the example below.
The following are some examples:
Task: I would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
sub-task 1: {{'description': 'I first need to do a search to find items that might qualify.', 'reasoning instruction': 'Search based on attributes other than price.', 'tool use instruction': None}}
sub-task 2: {{'description': 'Then I need to find the most suitable item in the item list.', 'reasoning instruction': 'Find the most qualified item in the item list.', 'tool use instruction': None}}
sub-task 3: {{'description': 'Finally, I need to click the attributes of the selected item and decide to buy it.', 'reasoning instruction': 'Click the attributes of the selected item and  buy it.', 'tool use instruction': None}}

Task: {task_description}
'''
        else:
            prompt = f'''You are a helpful assistant that generates subgoals to complete any {task_type} task specified by me.
I'll give you a final task, you need to decompose the task into a list of subgoals.
You must follow the following criteria:
1) Return a  list of subgoals that can be completed in order to complete the specified task.
2) Give the reasoning instructions for each subgoal and the instructions for calling the tool. 
You also need to give the reasoning instructions for each subtask and the instructions for calling the tool. Your output format should follow the example below.
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

        
