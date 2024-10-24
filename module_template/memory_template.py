import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import shutil
class MEMORY_TEMPLATE():
    def __init__(self, llms_type) -> None:
        # Initialization of the class
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', f'dilu/')
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )

    def __call__(self, current_situation: str=''):
        # Decide to store or read
        if:
            self.addMemory(current_situation.replace('success', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        # Retrive and read memory

    def addMemory(self, current_situation):
        # Store memory





