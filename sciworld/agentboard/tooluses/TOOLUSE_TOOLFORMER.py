import re
from utils_llm import llm_response, get_price

class TOOLUSE_TOOLFORMER():
    def __init__(self,llms_type):
        self.tool_base = []
        self.llm_type = llms_type[0]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        prompt = f'''
[1] find_flights: Finds flights based on source, destination and date. Arguments: from_location (str), to_location (str), date (str) in YYYY-MM-DD format.
Returns a list of flights, each represented as a dictionary with keys "from_location", "to_location" (destination), "date", and "price".
Example: [{{"from_location": "A", "to_location": "B", "date": "2023-12-25", "price": 450}}]
    Signature: find_flights(destination: str, date: str) -> List[Dict]
[2] book_hotel: Books a hotel based on location and preferences. Arguments: location (str), *preferences (variable number of str arguments).
Returns a list of hotels, each represented as a dictionary with keys "location", "preferences", "price_per_night", and "rating".
Example: [{{"location": "A", "preferences": ["wifi", "pool"], "price_per_night": 120, "rating": 4}}]
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
You need to select the appropriate tool from the list of available tools according to the task description to complete the task: {task_description}
{tool_instruction}
You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can only invoke one tool at a time.
You should begin your tool invocation with 'Action:' and end it with 'End Action'.
{feedback_of_previous_tools}
Your output should be of the following format
'Action: tool_name, argument_1, argument_2 End Action'
'''
        strings = [llm_response(prompt=prompt, model=self.llm_type, temperature=1) for i in range(3)]
        reasoning_result = self.get_votes(task_description, strings)
        return strings
    def get_votes(self, task_description, reasoning_results):
        prompt = '''Task:
[1] find_flights: Finds flights based on source, destination and date. Arguments: from_location (str), to_location (str), date (str) in YYYY-MM-DD format.
Returns a list of flights, each represented as a dictionary with keys "from_location", "to_location" (destination), "date", and "price".
Example: [{{"from_location": "A", "to_location": "B", "date": "2023-12-25", "price": 450}}]
    Signature: find_flights(destination: str, date: str) -> List[Dict]
[2] book_hotel: Books a hotel based on location and preferences. Arguments: location (str), *preferences (variable number of str arguments).
Returns a list of hotels, each represented as a dictionary with keys "location", "preferences", "price_per_night", and "rating".
Example: [{{"location": "A", "preferences": ["wifi", "pool"], "price_per_night": 120, "rating": 4}}]
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
You need to select the appropriate tool from the list of available tools according to the task description to complete the task: {task_description}
You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
------------
Given a task and several answers, decide which answer is most promising. Analyze each choice in detail, then conclude in the last line "The best answer is {{s}}", where s the integer id of the choice.
{task_description}
'''     
        prompt = prompt.format(task_description=task_description)
        for i, y in enumerate(reasoning_results, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = [llm_response(prompt=prompt, model=self.llm_type, temperature=1) for i in range(5)]
        vote_results = [0] * len(reasoning_results)
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(len(reasoning_results)):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
        ids = list(range(len(reasoning_results)))
        select_id = sorted(ids, key=lambda x: vote_results[x], reverse=True)[0]
        return reasoning_results[select_id]
        

