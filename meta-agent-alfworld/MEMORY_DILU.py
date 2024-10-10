import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import shutil
#需要根据具体任务对addmemorye和retrievememory进行修改，实现功能就是存入成功的问题解决轨迹，索引是任务名
class MEMORY_DILU():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = None
        db_path = os.path.join(
            './db', 'dilu/') if db_path is None else db_path
        if os.path.exists(db_path):
            shutil.rmtree(db_path)  # 删除现有的库
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )
        print("==========Loaded ",db_path," Memory, Now the database has ", len(
            self.scenario_memory._collection.get(include=['embeddings'])['embeddings']), " items.==========")

    def __call__(self, current_situation: str=''):
        if 'success.' in current_situation:
            self.addMemory(current_situation.replace('success.', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        query_scenario = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]        
        print(query_scenario)
        if self.scenario_memory._collection.count() == 0:
            print("The memory vector database is empty. Cannot perform search.")
            return ''  # 返回空，表示没有检索到任何记忆
        similarity_results = self.scenario_memory.similarity_search_with_score(
            query_scenario, k=1)
        fewshot_results = []
        for idx in range(0, len(similarity_results)):
            fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
        return '\n'.join(fewshot_results)

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
        sce_descrip = task_name.group(1)
        #print(task_trajectory)
        doc = Document(
            page_content=sce_descrip,
            metadata={"task_name": sce_descrip,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

        print("Add a memory item. Now the database has ", len(
            self.scenario_memory._collection.get(include=['embeddings'])['embeddings']), " items.")





