import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import shutil
from utils import llm_response
class MEMORY_TP():
    def __init__(self, llms_type) -> None:
        global flag
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = None
        db_path = os.path.join('./db', f'tp/')
        flag += 1
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )

    def __call__(self, current_situation: str=''):
        if 'success' in current_situation:
            self.addMemory(current_situation.replace('success', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        task_name = re.findall(r'Instruction:\s+(.*?)\s+\[Search\]', query_scenario)[1]      
        if self.scenario_memory._collection.count() == 0:
            return ''
        similarity_results = self.scenario_memory.similarity_search_with_score(
            task_name, k=1)
        few_experience_results = []
        task_description = 'Webshop' + query_scenario.rsplit('Webshop', 1)[1]
        for idx in range(0, len(similarity_results)):
            prompt = f"""You will be given a successful case where you successfully complete the task. Then you will be given a ongoing task. Do not summarize these two cases, but rather use the successful case to think about the strategy and path you took to attempt to complete the task in the ongoning task. Devise a concise, new plan of action that accounts for your task with reference to specific actions that you should have taken. You will need this later to solve the task. Give your plan after "Plan".
Success Case:
{similarity_results[idx][0].metadata['task_trajectory']}
Ongoning task:
{task_description}
Plan:
"""
            few_experience_results.append(llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)) 
        return 'Plan from successful attempt in similar task:\n' + '\n'.join(few_experience_results)

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r'Instruction:\s+(.*?)\s+\[Search\]', current_situation)
        sce_descrip = task_name.group(1)
        doc = Document(
            page_content=sce_descrip,
            metadata={"task_name": sce_descrip,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])





