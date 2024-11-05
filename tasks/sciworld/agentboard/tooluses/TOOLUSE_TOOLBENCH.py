import os
import re
from utils_llm import llm_response, get_price
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document

class TOOLUSE_TOOLBENCH():
    def __init__(self, llms_type):
        db_path = os.path.join('./db', 'api_pool/') 
        self.llm_type = llms_type[0]
        self.embedding = OpenAIEmbeddings()       
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )
        api_string = """
[1] find_flights: Finds flights based on source, destination and date. Arguments: from_location (str), to_location (str), date (str) in YYYY-MM-DD format.
Returns a list of flights, each represented as a dictionary with keys "from_location", "to_location" (destination), "date", and "price".
Example: [{"from_location": "A", "to_location": "B", "date": "2023-12-25", "price": 450}]
    Signature: find_flights(destination: str, date: str) -> List[Dict]
[2] book_hotel: Books a hotel based on location and preferences. Arguments: location (str), *preferences (variable number of str arguments).
Returns a list of hotels, each represented as a dictionary with keys "location", "preferences", "price_per_night", and "rating".
Example: [{"location": "A", "preferences": ["wifi", "pool"], "price_per_night": 120, "rating": 4}]
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
"""
        # 正则表达式匹配每个API的段落
        api_pattern = re.compile(r"\[(\d+)\] ([^:]+): (.+?)(?=\[\d+\]|\Z)", re.DOTALL)
        api_matches = api_pattern.findall(api_string)
        # 生成文档列表
        documents = []
        for match in api_matches:
            api_id, api_name, api_description = match
            
            # 提取第一句话作为page_content
            first_sentence = api_description.split('.')[0].strip() + '.'

            # 构建完整的API描述
            full_description = f"[{api_id}] {api_name}: {api_description.strip()}"
            
            # 创建文档对象
            doc = Document(
                page_content=first_sentence,
                metadata={
                    "name": api_name.strip(),
                    "description": full_description
                }
            )
            documents.append(doc)
        self.scenario_memory.add_documents(documents)
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        similarity_results = self.scenario_memory.similarity_search_with_score(tool_instruction, k=3)
        prompt = f'''
{similarity_results}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task: {task_description}
{tool_instruction}
You should use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can only invoke one tool at a time.
You should begin your tool invocation with 'Action:' and end it with 'End Action'.
{feedback_of_previous_tools}
Your output should be of the following format
'Action: tool_name, argument.. End Action'
'''
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        return string

