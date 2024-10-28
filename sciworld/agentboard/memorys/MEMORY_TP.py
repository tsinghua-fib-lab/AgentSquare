import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import shutil
from utils_llm import llm_response
#需要根据具体任务对addmemorye和retrievememory进行修改，实现功能就是存入成功的问题解决轨迹,再根据目前任务生成适当输出，索引是任务名
class MEMORY_TP():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = None
        db_path = os.path.join(
            './db', 'tp1/') if db_path is None else db_path
        # if os.path.exists(db_path):
        #     shutil.rmtree(db_path)  # 删除现有的库
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )
        print("==========Loaded ",db_path," Memory, Now the database has ", len(
            self.scenario_memory._collection.get(include=['embeddings'])['embeddings']), " items.==========")

    def __call__(self, current_situation: str=''):
        if 'The correct trajectory is' in current_situation:
            self.addMemory(current_situation)
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        task_name = query_scenario
        # print(task_name)
        if self.scenario_memory._collection.count() == 0:
            print("The memory vector database is empty. Cannot perform search.")
            return ''  # 返回空，表示没有检索到任何记忆
        similarity_results = self.scenario_memory.similarity_search_with_score(
            task_name, k=1)
        few_experience_results = []
        for idx in range(0, len(similarity_results)):
            #fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            prompt = f"""You will be given a successful case where you successfully complete the task. Then you will be given a ongoing task. Do not summarize these two cases, but rather use the successful case to think about the strategy and path you took to attempt to complete the task in the ongoning task. Devise a concise, new plan of action that accounts for your task with reference to specific actions that you should have taken. You will need this later to solve the task. Give your plan after "Plan".
Success Case:
{similarity_results[idx][0].metadata['task_trajectory']}
Ongoning task:
{query_scenario}
Plan:
"""
            few_experience_results.append(llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)) 
        return 'Plan from successful attempt in similar task:\n' + '\n'.join(few_experience_results)

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r'Task : (.*?) \nThe correct trajectory is', current_situation)
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





