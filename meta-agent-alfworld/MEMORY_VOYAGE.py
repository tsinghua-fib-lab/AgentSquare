voyage_prompt = '''You are a helpful assistant that writes a description of the task resolution trajectory.

1) Try to summarize the trajectory in no more than 6 sentences.
2) Your response should be a single line of text.

For example:
Trajectory:
You are in the middle of a room. Looking quickly around you, you see a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a diningtable 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
Your task is to: heat some egg and put it in diningtable.
> think: To solve the task, I need to find and take an egg, then heat it with microwave, then put it in diningtable.
OK.
> think: First I need to find an egg. An egg is more likely to appear in fridge (1), countertop (1-3), diningtable (1), stoveburner (1-4), toaster (1), garbagecan (1), cabinet (1-10). I can check one by one, starting with fridge 1.
OK.
> open fridge 1
You open the fridge 1. The fridge 1 is open. In it, you see a lettuce 2, a mug 2, and a potato 3.
> go to countertop 1
On the countertop 1, you see a bread 1, a fork 1, and a saltshaker 1.
> go to countertop 2
On the countertop 2, you see nothing.
> go to countertop 3
On the countertop 3, you see a bowl 1, a butterknife 1, a egg 2, a kettle 2, a plate 1, a sink 1, and a spatula 2.
> think: Now I find an egg (2). Next, I need to take it.
OK.
> take egg 2 from countertop 3
You pick up the egg 2 from the countertop 3.
> think: Now I take an egg (2). Next, I need go to a microwave (1) and heat it.
OK.
> go to microwave 1
The microwave 1 is closed.
> heat egg 2 with microwave 1
You heat the egg 2 using the microwave 1.
> think: Now I heat an egg (2). Next, I need to put it in/on diningtable 1.
OK.
> go to diningtable 1
On the diningtable 1, you see a apple 2, a bread 3, a egg 1, a kettle 1, a knife 1, a mug 1, a papertowelroll 1, a peppershaker 2, a potato 1, a soapbottle 1, and a spatula 1.
> put egg 2 in/on diningtable 1
You put the egg 2 in/on the diningtable 1.

Then you would write: The trajectory is about finding an egg, heating it with a microwave, and placing it on the dining table after checking various locations like the fridge and countertops.

Trajectory:
'''
import shutil
import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma 
from langchain.docstore.document import Document
from utils import llm_response
#需要根据具体任务对addmemorye和retrievememory进行修改，实现功能就是存入成功的问题解决轨迹，索引是任务的描述，llm生成
class MEMORY_VOYAGE():
    def __init__(self, llms_type):
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', 'voyage/')
        #self.skills = {}
        #self.retrieval_top_k = 1
        # 删除旧的向量数据库目录
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path,
        )
    def __call__(self, current_situation: str=''):
        if 'success.' in current_situation:
            self.addMemory(current_situation.replace('success.', ''))
        else:
            return self.retriveMemory(current_situation)
        
    def retriveMemory(self, query_scenario):
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]     
        print(task_name)   
        if self.scenario_memory._collection.count() == 0:
            print("The memory vector database is empty. Cannot perform search.")
            return '' 
        similarity_results = self.scenario_memory.similarity_search_with_score(task_name, k=1)
        fewshot_results = []
        for idx in range(0, len(similarity_results)):
            fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
        return  '\n'.join(fewshot_results)

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
        sce_descrip = task_name.group(1)
        prompt = voyage_prompt + task_trajectory
        task_description = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        print(task_description)
        doc = Document(
            page_content=task_description,
            metadata={"task_description": task_description,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])


if __name__ == "__main__":
    memory = MEMORY_VOYAGE(['gpt-3.5-turbo-0125'])
    string = 'Search:12345success.Your task is to:   dad aa dada d.>'
    memory(string)
