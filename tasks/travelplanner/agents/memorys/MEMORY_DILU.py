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
            './db', 'chroma_5_shot_20_mem6/') if db_path is None else db_path
        # if os.path.exists(db_path):
        #     shutil.rmtree(db_path)  # 删除现有的库
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )
        print("==========Loaded ",db_path," Memory, Now the database has ", len(
            self.scenario_memory._collection.get(include=['embeddings'])['embeddings']), " items.==========")

    def __call__(self, current_situation: str=''):
        if 'The generated plan is:' in current_situation:
            self.addMemory(current_situation)
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        similarity_results = self.scenario_memory.similarity_search_with_score(
            query_scenario, k=3)
        fewshot_results = []
        for idx in range(0, len(similarity_results)):
            fewshot_results.append(similarity_results[idx][0].metadata)
        print("-"*100)
        print(fewshot_results)
        return str(fewshot_results)

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r"The query is: (.*?).The generated plan is", current_situation)
        if task_name is not None:
            sce_descrip = task_name.group(1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_name": sce_descrip,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])

            print("Add a memory item. Now the database has ", len(
                self.scenario_memory._collection.get(include=['embeddings'])['embeddings']), " items.")
        print(sce_descrip)





