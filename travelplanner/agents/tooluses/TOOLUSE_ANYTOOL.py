import os
import json
import re
import ast 
from utils_llm import llm_response, get_price
import random
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

class TOOLUSE_ANYTOOL():
    def __init__(self, llms_type):
        self.tool_base = []
        self.llm_type = llms_type[0]
        self.tool_description = functions_info = {
    "FlightSearch[Departure City, Destination City, Date]": {
        "description": "A flight information retrieval tool.",
        "arguments": {
            "Departure City": "The city you'll be flying out from",
            "Destination City": "The city you aim to reach",
            "Date": "The date of your travel in YYYY-MM-DD format"
        },
        "example": "FlightSearch[New York, London, 2022-10-01] would fetch flights from New York to London on October 1, 2022.",
        "signature": "FlightSearch[Departure City, Destination City, Date]"
    },
    "GoogleDistanceMatrix[Origin, Destination, Mode]": {
        "description": "Estimate the distance, time and cost between two cities.",
        "arguments": {
            "Origin": "The departure city of your journey",
            "Destination": "The destination city of your journey",
            "Mode": "The method of transportation. Choices include 'self-driving' and 'taxi'"
        },
        "example": "GoogleDistanceMatrix[Paris, Lyon, self-driving] would provide driving distance, time and cost between Paris and Lyon.",
        "signature": "GoogleDistanceMatrix[Origin, Destination, Mode]"
    },
    "AccommodationSearch[City]": {
        "description": "Discover accommodations in your desired city.",
        "arguments": {
            "City": "The name of the city where you're seeking accommodation."
        },
        "Example": "AccommodationSearch[Rome] would present a list of hotel rooms in Rome.",
        "signature": "AccommodationSearch[City]"
    },
    "RestaurantSearch[City]": {
        "description": "Explore dining options in a city of your choice.",
        "arguments": {
            "City": "The name of the city where you're seeking restaurants."
        },
        "Example": "RestaurantSearch[Tokyo] would show a curated list of restaurants in Tokyo.",
        "signature": "RestaurantSearch[City]"
    },
    "AttractionSearch[City]": {
        "description": "Find attractions in a city of your choice.",
        "arguments": {
            "City": "The name of the city where you're seeking attractions."
        },
        "Example": "AttractionSearch[London] would return attractions in London.",
        "signature": "AttractionSearch[City]"
    },
    "CitySearch[State]": {
        "description": "Find cities in a state of your choice.",
        "arguments": {
            "State": "The name of the state where you're seeking cities."
        },
        "Example": "CitySearch[California] would return cities in California.",
        "signature": "CitySearch[State]"
    },
    "NotebookWrite[Short Description]": {
        "description": "Writes a new data entry into the Notebook tool with a short description. This tool should be used immediately after FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch or GoogleDistanceMatrix. Only the data stored in Notebook can be seen by Planner. So you should write all the information you need into Notebook.",
        "arguments": {
            "Short Description": "A brief description or label for the stored data. You don't need to write all the information in the description. The data you've searched for will be automatically stored in the Notebook."
        },
        "Example": "NotebookWrite[Flights from Rome to Paris in 2022-02-01] would store the informatrion of flights from Rome to Paris in 2022-02-01 in the Notebook.",
        "signature": "NotebookWrite[Short Description]"
    },
    "Planner[Query]": {
        "description": "A smart planning tool that crafts detailed plans based on user input and the information stroed in Notebook.",
        "arguments": {
            "Query": "The query from user."
        },
        "Example": "Planner[Give me a 3-day trip plan from Seattle to New York] would return a detailed 3-day trip plan.",
        "signature": "Planner[Query]"
    }
}

        self.tool_pool = {'FlightSearch[Departure City, Destination City, Date]': "Description: A flight information retrieval tool.Parameters:Departure City: The city you'll be flying out from.Destination City: The city you aim to reach.Date: The date of your travel in YYYY-MM-DD format.Example: FlightSearch[New York, London, 2022-10-01] would fetch flights from New York to London on October 1, 2022.", 
'GoogleDistanceMatrix[Origin, Destination, Mode]': "Description: Estimate the distance, time and cost between two cities.Parameters:Origin: The departure city of your journey.Destination: The destination city of your journey.Mode: The method of transportation. Choices include 'self-driving' and 'taxi'.Example: GoogleDistanceMatrix[Paris, Lyon, self-driving] would provide driving distance, time and cost between Paris and Lyon.",
'AccommodationSearch[City]': "Description: Discover accommodations in your desired city.Parameter: City - The name of the city where you're seeking accommodation.Example: AccommodationSearch[Rome] would present a list of hotel rooms in Rome.", 
'RestaurantSearch[City]': "Description: Explore dining options in a city of your choice.Parameter: City – The name of the city where you're seeking restaurants.Example: RestaurantSearch[Tokyo] would show a curated list of restaurants in Tokyo.",
'AttractionSearch[City]': "Description: Find attractions in a city of your choice.Parameter: City – The name of the city where you're seeking attractions.Example: AttractionSearch[London] would return attractions in London.",
'CitySearch[State]': "Description: Find cities in a state of your choice.Parameter: State – The name of the state where you're seeking cities.Example: CitySearch[California] would return cities in California.",
'NotebookWrite[Short Description]':"Description: Writes a new data entry into the Notebook tool with a short description. This tool should be used immediately after FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch or GoogleDistanceMatrix. Only the data stored in Notebook can be seen by Planner. So you should write all the information you need into Notebook.Parameters: Short Description - A brief description or label for the stored data. You don't need to write all the information in the description. The data you've searched for will be automatically stored in the Notebook.Example: NotebookWrite[Flights from Rome to Paris in 2022-02-01] would store the informatrion of flights from Rome to Paris in 2022-02-01 in the Notebook.",
'Planner[Query]':"Description: A smart planning tool that crafts detailed plans based on user input and the information stroed in Notebook.Parameters: Query: The query from user.Example: Planner[Give me a 3-day trip plan from Seattle to New York] would return a detailed 3-day trip plan."
}

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
        if matching_dict and 'tool list' in matching_dict and matching_dict['tool list']:
            matched_tools = {tool: self.tool_description[tool] for tool in matching_dict['tool list'] if tool in self.tool_description}
        else:
            matched_tools = random.choice(list(self.tool_description.keys()))
        prompt = f'''
{matched_tools}
The user's query is :{task_description}
The tool-use instruction for current task is :{tool_instruction}

You can only invoke one tool at a time.
{feedback_of_previous_tools}

Each action only calls one function once. Do not add any description in the action.
You answer should follow the format: tool_type[tool_arg], such as FlightSearch[New York, London, 2022-10-01]

'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1,stop_strs=['\n'])
        # llm = ChatOpenAI(temperature=1,
        #              max_tokens=256,
        #              model_name=self.llm_type,
        #              openai_api_key=os.environ.get("OPENAI_API_KEY"),
        #              model_kwargs={"stop": ['\n']}
        #             )
        # string = llm([HumanMessage(content=prompt)]).content
        return string

