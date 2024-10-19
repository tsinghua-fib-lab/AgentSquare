import os
import re
from utils import llm_response
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from tooluse_IO_pool import tooluse_IO_pool
class TOOLUSE_TOOLBENCH():
    def __init__(self, llms_type):
        self.llm_type = llms_type[0]
        self.scenario_memory = {}
        for name, tools in tooluse_IO_pool.items():
            db_path = os.path.join('./db', f'api_pool{name}/') 
            self.embedding = OpenAIEmbeddings()       
            self.scenario_memory[name] = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
            api_pattern = re.compile(r"\[(\d+)\] ([^:]+): (.+?)(?=\[\d+\]|\Z)", re.DOTALL)
            api_matches = api_pattern.findall(tools)
            documents = []
            for match in api_matches:
                api_id, api_name, api_description = match
                first_sentence = api_description.split('.')[0].strip() + '.'
                full_description = f"[{api_id}] {api_name}: {api_description.strip()}"
                doc = Document(
                    page_content=first_sentence,
                    metadata={
                        "name": api_name.strip(),
                        "description": full_description
                    }
                )
                documents.append(doc)
            if self.scenario_memory[name]._collection.count() != 0:
                continue
            self.scenario_memory[name].add_documents(documents)
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        similarity_results = self.scenario_memory[task_description].similarity_search_with_score(tool_instruction, k=4)
        tool_pool = []
        for idx in range(0, len(similarity_results)):
            tool_pool.append(similarity_results[idx][0].metadata['description'])
        prompt = f'''
You have access to the following tools:
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
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        return string