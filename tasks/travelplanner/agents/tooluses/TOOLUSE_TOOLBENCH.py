import os
import re
from utils_llm import get_chat,llm_response, get_price
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

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

[1] FlightSearch[Departure City, Destination City, Date]:A flight information retrieval tool.
Parameters:
Departure City: The city you'll be flying out from.
Destination City: The city you aim to reach.
Date: The date of your travel in YYYY-MM-DD format.
Example: FlightSearch[New York, London, 2022-10-01] would fetch flights from New York to London on October 1, 2022.

[2] GoogleDistanceMatrix[Origin, Destination, Mode]:Estimate the distance, time and cost between two cities.
Parameters:
Origin: The departure city of your journey.
Destination: The destination city of your journey.
Mode: The method of transportation. Choices include 'self-driving' and 'taxi'.
Example: GoogleDistanceMatrix[Paris, Lyon, self-driving] would provide driving distance, time and cost between Paris and Lyon.

[3] AccommodationSearch[City]:Discover accommodations in your desired city.
Parameter: City - The name of the city where you're seeking accommodation.
Example: AccommodationSearch[Rome] would present a list of hotel rooms in Rome.

[4] RestaurantSearch[City]:Explore dining options in a city of your choice.
Parameter: City – The name of the city where you're seeking restaurants.
Example: RestaurantSearch[Tokyo] would show a curated list of restaurants in Tokyo.

[5] AttractionSearch[City]:Find attractions in a city of your choice.
Parameter: City – The name of the city where you're seeking attractions.
Example: AttractionSearch[London] would return attractions in London.

[6] CitySearch[State]:Find cities in a state of your choice.
Parameter: State – The name of the state where you're seeking cities.
Example: CitySearch[California] would return cities in California.

[7] NotebookWrite[Short Description]:Writes a new data entry into the Notebook tool with a short description. This tool should be used immediately after FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch or GoogleDistanceMatrix. Only the data stored in Notebook can be seen by Planner. So you should write all the information you need into Notebook.
Parameters: Short Description - A brief description or label for the stored data. You don't need to write all the information in the description. The data you've searched for will be automatically stored in the Notebook.
Example: NotebookWrite[Flights from Rome to Paris in 2022-02-01] would store the informatrion of flights from Rome to Paris in 2022-02-01 in the Notebook.

[8] Planner[Query]:A smart planning tool that crafts detailed plans based on user input and the information stroed in Notebook.
Parameters: 
Query: The query from user.
Example: Planner[Give me a 3-day trip plan from Seattle to New York] would return a detailed 3-day trip plan.
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
        if documents:
            self.scenario_memory.add_documents(documents)
        else :
            print()
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        similarity_results = self.scenario_memory.similarity_search_with_score(tool_instruction, k=3)
        prompt = f'''
{similarity_results}
The user's query is :{task_description}
The tool-use instruction for current task is :{tool_instruction}
{feedback_of_previous_tools}

Each action only calls one function once. Do not add any description in the action.
You answer should follow the format: tool_type[tool_arg], such as FlightSearch[New York, London, 2022-10-01]
'''
        
        # llm = ChatOpenAI(temperature=1,
        #              max_tokens=256,
        #              model_name=self.llm_type,
        #              openai_api_key=os.environ.get("OPENAI_API_KEY"),
        #              model_kwargs={"stop": ['\n']}
        #             )
        # string = llm([HumanMessage(content=prompt)]).content
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        return string

