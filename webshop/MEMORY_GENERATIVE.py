import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import shutil
from utils import llm_response
class MEMORY_GENERATIVE():
    def __init__(self, llms_type) -> None:
        global flag
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = None
        db_path = os.path.join('./db', f'generative/')
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
            task_name, k=3)
        fewshot_results = []
        important_scores = []
        for idx in range(0, len(similarity_results)):
            fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            prompt = f'''You will be given a successful case where you successfully complete the task.   Then you will be given a ongoing task.    Do not summarize these two cases, but rather think about how much the successful case inspired the task in progress, on a scale of 1-10 according to degree.  
Success Case:
{similarity_results[idx][0].metadata['task_trajectory']}
Ongoning task:
{query_scenario}
Your output format should be the following format:
Score: '''
            response = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            match = re.search(r'\d+', response)
            if match:
                important_scores.append(int(match.group()))
            else:
                important_scores.append(0)
        max_scores = max(important_scores)
        idx= important_scores.index(max_scores)
        return similarity_results[idx][0].metadata['task_trajectory']

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




