import os
import re
import ast
from utils_llm import llm_response, get_price

class PLANNING_OPENAGI():
    def __init__(self, llms_type):
        self.plan = []
        self.llm_type = llms_type[0]
    def __call__(self, task_type, task_description, feedback):
        if feedback == '':
            prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.  
Your output format should follow the example below.
The following are some examples:
task: Goal: Please create a 3-day travel plan from Washington to Myrtle Beach within a budget of $1,400.
sub-task 1: {{"description": "To create a comprehensive travel plan, first of all, I need to gather information on flights from Washington to Myrtle Beach for the specified dates.", "reasoning instruction": "a 3-day travel plan from Washington to Myrtle Beach", "tool use instruction": "I need to gather information on flights from Washington to Myrtle Beach for the specified dates."}}
sub-task 2: {{"description": "Then I should select the flight that best fits the budget and schedule for the trip, and I should note this flight in the Notebook.", "reasoning instruction": "I have already gathered information on flights from Washington to Myrtle Beach for the specified dates.", "tool use instruction": "I should note this flight in the Notebook."}}
sub-task 3: {{"description": "Now that the flight is selected and noted, I need to find accommodation options in Myrtle Beach that are within the remaining budget.", "reasoning instruction": "I should proceed to search for accommodations that are affordable and well-rated.", "tool use instruction": "I need to discover accommodations in my desired city."}}
sub-task 4: {{"description": "Then I should select an accomodation  that is affordable yet comfortable, and I should note this accommodation in the Notebook", "reasoning instruction": "I have already gathered information about accomdation.", "tool use instruction": "I should note this accommodation in the Notebook."}}
sub-task 5: {{"description": "With the flight and accommodation noted, the next step is to find dining options in Myrtle Beach.", "reasoning instruction": "The flight and accommodation noted, then I should proceed to search for dining options and attractions in Myrtle Beach.", "tool use instruction": "I should explore dining options in Myrtle Beach."}}
sub-task 6: {{"description": "To maintain the budget, I should note down a mix of restaurants with lower average costs but good ratings.", "reasoning instruction": "I have already gathered information about restaurants.", "tool use instruction": "I will note these restaurants in the Notebook"}}
sub-task 7: {{"description": "Having noted down some budget-friendly dining options, I should now focus on identifying attractions in Myrtle Beach that will be enjoyable and cost-effective.", "reasoning instruction": "I should find attractions in Myrtle Beach.", "tool use instruction": "I need to find attractions in Myrtle Beach."}}
sub-task 8: {{"description": "Then I will note these attractions in the Notebook.", "reasoning instruction": "I have already gathered information about attractions.", "tool use instruction": "I will note these attractions in the Notebook."}}
sub-task 9: {{"description": "With the attractions noted, I should now estimate the local transportation costs within Myrtle Beach.", "reasoning instruction": "The attractions noted", "tool use instruction": "I should estimate the local transportation costs within Myrtle Beach."}}
sub-task 10: {{"description": "This estimation should be noted in the Notebook", "reasoning instruction": "I have already gathered information about costs.", "tool use instruction": "I should note these in the Notebook."}}
sub-task 11: {{"description": "With all the necessary information now recorded in the Notebook, including the flight, accommodation, dining options, attractions, and an estimate for local transportation costs, I can proceed to use the Planner tool to create a detailed travel plan. ", "reasoning instruction": "All the necessary information is now recorded in the Notebook", "tool use instruction": "I will input the query into the Planner tool, referencing the indices in the Notebook where the relevant information is stored."}}

Here is the current task:
task: {task_description}

Your last subtask must be to call Planner tool to create a detailed travel plan.

'''
            prompt = prompt.format(task_description=task_description, task_type=task_type)
        else:
            prompt = '''You are a planner who is an expert at coming up with a todo list for a given {task_type} objective.
For each task, you also need to give the reasoning instructions for each subtask and the instructions for calling the tool.
Ensure the list is as short as possible, and tasks in it are relevant, effective and described in a single sentence.
Develop a concise to-do list to achieve the objective.
Your output format should follow the example below.
The following are some examples:
task: Goal: Please create a 3-day travel plan from Washington to Myrtle Beach within a budget of $1,400.
sub-task 1: {{"description": "To create a comprehensive travel plan, first of all, I need to gather information on flights from Washington to Myrtle Beach for the specified dates.", "reasoning instruction": "a 3-day travel plan from Washington to Myrtle Beach", "tool use instruction": "I need to gather information on flights from Washington to Myrtle Beach for the specified dates."}}
sub-task 2: {{"description": "Then I should select the flight that best fits the budget and schedule for the trip, and I should note this flight in the Notebook.", "reasoning instruction": "I have already gathered information on flights from Washington to Myrtle Beach for the specified dates.", "tool use instruction": "I should note this flight in the Notebook."}}
sub-task 3: {{"description": "Now that the flight is selected and noted, I need to find accommodation options in Myrtle Beach that are within the remaining budget.", "reasoning instruction": "I should proceed to search for accommodations that are affordable and well-rated.", "tool use instruction": "I need to discover accommodations in my desired city."}}
sub-task 4: {{"description": "Then I should select an accomodation  that is affordable yet comfortable, and I should note this accommodation in the Notebook", "reasoning instruction": "I have already gathered information about accomdation.", "tool use instruction": "I should note this accommodation in the Notebook."}}
sub-task 5: {{"description": "With the flight and accommodation noted, the next step is to find dining options in Myrtle Beach.", "reasoning instruction": "The flight and accommodation noted, then I should proceed to search for dining options and attractions in Myrtle Beach.", "tool use instruction": "I should explore dining options in Myrtle Beach."}}
sub-task 6: {{"description": "To maintain the budget, I should note down a mix of restaurants with lower average costs but good ratings.", "reasoning instruction": "I have already gathered information about restaurants.", "tool use instruction": "I will note these restaurants in the Notebook"}}
sub-task 7: {{"description": "Having noted down some budget-friendly dining options, I should now focus on identifying attractions in Myrtle Beach that will be enjoyable and cost-effective.", "reasoning instruction": "I should find attractions in Myrtle Beach.", "tool use instruction": "I need to find attractions in Myrtle Beach."}}
sub-task 8: {{"description": "Then I will note these attractions in the Notebook.", "reasoning instruction": "I have already gathered information about attractions.", "tool use instruction": "I will note these attractions in the Notebook."}}
sub-task 9: {{"description": "With the attractions noted, I should now estimate the local transportation costs within Myrtle Beach.", "reasoning instruction": "The attractions noted", "tool use instruction": "I should estimate the local transportation costs within Myrtle Beach."}}
sub-task 10: {{"description": "This estimation should be noted in the Notebook", "reasoning instruction": "I have already gathered information about costs.", "tool use instruction": "I should note these in the Notebook."}}
sub-task 11: {{"description": "With all the necessary information now recorded in the Notebook, including the flight, accommodation, dining options, attractions, and an estimate for local transportation costs, I can proceed to use the Planner tool to create a detailed travel plan. ", "reasoning instruction": "All the necessary information is now recorded in the Notebook", "tool use instruction": "I will input the query into the Planner tool, referencing the indices in the Notebook where the relevant information is stored."}}

end
Your last subtask must be to call Planner tool to create a detailed travel plan.
--------------------
reflexion:{feedback}
Here is the current task:
task:{task_description}


'''
            prompt = prompt.format(task_description = task_description, task_type=task_type, feedback = feedback)

        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)

        dict_strings = re.findall(r"\{[^{}]*\}", string)
        dicts = [ast.literal_eval(ds) for ds in dict_strings]
        self.plan = dicts
        return self.plan

        
