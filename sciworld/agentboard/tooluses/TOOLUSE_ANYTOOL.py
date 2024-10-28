import os
import json
import re
import ast 
from utils_llm import llm_response, get_price

class TOOLUSE_ANYTOOL():
    def __init__(self, llms_type):
        self.tool_base = []
        self.llm_type = llms_type[0]
        self.tool_description = functions_info = {
    "find_flights": {
        "description": "Finds flights based on source, destination and date.",
        "arguments": {
            "from_location": "str",
            "to_location": "str",
            "date": "str (in YYYY-MM-DD format)"
        },
        "returns": "List of flights, each represented as a dictionary with keys 'from_location', 'to_location' (destination), 'date', and 'price'.",
        "example": [{"from_location": "A", "to_location": "B", "date": "2023-12-25", "price": 450}],
        "signature": "find_flights(from_location: str, to_location: str, date: str) -> List[Dict]"
    },
    "book_hotel": {
        "description": "Books a hotel based on location and preferences.",
        "arguments": {
            "location": "str",
            "*preferences": "variable number of str arguments"
        },
        "returns": "List of hotels, each represented as a dictionary with keys 'location', 'preferences', 'price_per_night', and 'rating'.",
        "example": [{"location": "A", "preferences": ["wifi", "pool"], "price_per_night": 120, "rating": 4}],
        "signature": "book_hotel(location: str, *preferences: str) -> List[Dict]"
    },
    "budget_calculator": {
        "description": "Calculates the total budget for a trip.",
        "arguments": {
            "flight_price": "float",
            "hotel_price_per_night": "float",
            "num_nights": "int"
        },
        "returns": "Total budget (float).",
        "signature": "budget_calculator(flight_price: float, hotel_price_per_night: float, num_nights: int) -> float"
    },
    "max": {
        "description": "Finds the maximum value among the given arguments.",
        "arguments": {
            "*args": "variable number of float arguments"
        },
        "returns": "Maximum value (float).",
        "signature": "max(*args: float) -> float"
    },
    "min": {
        "description": "Finds the minimum value among the given arguments.",
        "arguments": {
            "*args": "variable number of float arguments"
        },
        "returns": "Minimum value (float).",
        "signature": "min(*args: float) -> float"
    },
    "sum": {
        "description": "Sums the given arguments.",
        "arguments": {
            "*args": "variable number of float arguments"
        },
        "returns": "Sum of values (float).",
        "signature": "sum(*args: float) -> float"
    }
}

        self.tool_pool = {'find_flights': 'Finds flights based on source, destination and date. Arguments: from_location (str), to_location (str), date (str) in YYYY-MM-DD format. Returns a list of flights, each represented as a dictionary with keys "from_location", "to_location" (destination), "date", and "price".', 
'book_hotel': 'Books a hotel based on location and preferences. Arguments: location (str), *preferences (variable number of str arguments). Returns a list of hotels, each represented as a dictionary with keys "location", "preferences", "price_per_night", and "rating".',
'budget_calculator': 'Calculates the total budget for a trip. Arguments: flight_price (float), hotel_price_per_night (float), num_nights (int). Returns the total budget (float).', 
'max': 'Finds the maximum value among the given arguments. Accepts variable number of float arguments.',
'min': 'Finds the minimum value among the given arguments. Accepts variable number of float arguments.',
'sum': 'Sums the given arguments. Accepts variable number of float arguments.'}

        category_prompt = f'''{self.tool_pool}
You have a series of tools, you need to divide them into several categories, such as data calculation, trip booking and so on.
All tools should be included in categorys.
your output format should be as follows:
category 1 : {{'category name': 'category description', 'tool list': ['tool 1 name', 'tool 2 name']}}
category 2 : {{'category name': 'category description', 'tool list': ['tool 1 name', 'tool 2 name']}}
'''
        string = llm_response(prompt=category_prompt, model=self.llm_type, temperature=0.1)
        dict_strings = re.findall(r"\{[^{}]*\}", string)
        self.dicts = [ast.literal_eval(ds) for ds in dict_strings]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        prompt = f'''{self.dicts}
You need to select the appropriate tool category from the list of available tools according to the task description to complete the task: {task_description}
{tool_instruction}
You can only invoke one category at a time.
{feedback_of_previous_tools}
Output category name directly.
Your output should be of the following format:
Category name: 
'''
        category_name = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1).split(':')[-1].strip()
        matching_dict = None
        for d in self.dicts:
            if d.get('category name') == category_name:
                matching_dict = d
                break
        matched_tools = {tool: self.tool_description[tool] for tool in matching_dict['tool list'] if tool in self.tool_description}
        prompt = f'''
{matched_tools}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task: {task_description}
{tool_instruction}
You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can only invoke one tool at a time.
You should begin your tool invocation with 'Action:' and end it with 'End Action'.
{feedback_of_previous_tools}
Your output should be of the following format:
'Action: tool_name, argument_1, argument_2 End Action'
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        return string

