import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from langchain.docstore.document import Document
import shutil
from utils import llm_response
"""
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
"""

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

class MEMORY_GENERATIVE():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = None
        db_path = os.path.join(
            './db', 'generative6/') if db_path is None else db_path
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
        # task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2] 
        task_name = query_scenario       
        print(task_name)
        if self.scenario_memory._collection.count() == 0:
            print("The memory vector database is empty. Cannot perform search.")
            return ''  # 返回空，表示没有检索到任何记忆
        similarity_results = self.scenario_memory.similarity_search_with_score(
            task_name, k=3)
        fewshot_results = []
        important_scores = []
        for idx in range(0, len(similarity_results)):
            fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            prompt = f'''You will be given a travel plan similar to the one you are currently required to draw up.   Then you will be given a ongoing task.    Do not summarize these two cases, but rather think about how much the travel plan case inspired the task in progress, on a scale of 1-10 according to degree.  
Travel plan Case:
{similarity_results[idx][0].metadata['task_trajectory']}
Ongoning task:
{query_scenario}
Your output format should be the following format:
Score: '''
            response = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
            match = re.search(r'\d+', response)  # 查找第一个匹配的数字
            if match:
                important_scores.append(int(match.group()))  # 返回匹配到的数字
            else:
                important_scores.append(0)
        max_scores = max(important_scores)
        idx= important_scores.index(max_scores)
        output = str({'task_name':similarity_results[idx][0].metadata['task_name'],'task_trajectory':similarity_results[idx][0].metadata['task_trajectory']})
        print(output)
        return output

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r'The query is: (.*?).The generated plan is', current_situation)
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

class MEMORY_TP():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = None
        db_path = os.path.join(
            './db', 'tp6/') if db_path is None else db_path
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
        # task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]
        task_name = query_scenario        
        print(task_name)
        if self.scenario_memory._collection.count() == 0:
            print("The memory vector database is empty. Cannot perform search.")
            return ''  # 返回空，表示没有检索到任何记忆
        similarity_results = self.scenario_memory.similarity_search_with_score(
            task_name, k=1)
        few_experience_results = []
        # task_description = 'You are in the' + query_scenario.rsplit('You are in the', 1)[1]
        task_description = task_name
        for idx in range(0, len(similarity_results)):
            # fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            prompt = f"""You will be given a travel plan case which you used to made. Then you will be given a ongoing task. \
                Do not summarize these two cases, but rather use the travel plan case to think about the strategy and path you took to attempt to complete the task in the ongoning task. \
                Devise a concise, new plan of action that accounts for your task with reference to specific actions that you should have taken. You will need this later to solve the task. Give your plan after "Plan".
Travel plan Case:
User query: {similarity_results[idx][0].metadata['task_name']}
Travel plan:
{similarity_results[idx][0].metadata['task_trajectory']}
Ongoning task:
{task_description}
Plan:
"""
            few_experience_results.append({'task_name':task_description,'task_trajectory':llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)}) 
        return str(few_experience_results)

    def addMemory(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r'The query is: (.*?).The generated plan is', current_situation)
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

class MEMORY_VOYAGE():
    def __init__(
        self,
        llms_type,
    ):
        self.llm = ChatOpenAI(
            model_name=llms_type[0],
            temperature=0.1,
            request_timeout=120,
        )
        ckpt_dir="ckpt6",
        self.skills = {}
        self.retrieval_top_k = 1
        self.ckpt_dir = ckpt_dir
        # if os.path.exists(f"{ckpt_dir}/skill/vectordb"):
        #     shutil.rmtree(f"{ckpt_dir}/skill/vectordb")  # 删除现有的库
        self.vectordb = Chroma(
            collection_name="skill_vectordb",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=f"{ckpt_dir}/skill/vectordb",
        )
        # assert self.vectordb._collection.count() == len(self.skills), (
        #     f"Skill Manager's vectordb is not synced with skills.json.\n"
        #     f"There are {self.vectordb._collection.count()} skills in vectordb but {len(self.skills)} skills in skills.json.\n"
        #     f"Did you set resume=False when initializing the manager?\n"
        #     f"You may need to manually delete the vectordb directory for running from scratch."
        # )

    def __call__(self, current_situation: str=''):
        if 'The generated plan is:' in current_situation:
            return self.add_new_skill(current_situation)
        else:
            self.retrieve_skills(current_situation)

    def add_new_skill(self, current_situation):
        task_trajectory = current_situation
        task_name = re.search(r"The query is: (.*?).The generated plan is", current_situation)
        if task_name is not None:
            task_name = task_name.group(1)
            skill_description = self.generate_skill_description(task_trajectory, task_name)
            self.vectordb.add_texts(
                texts=[skill_description],
                ids=[task_name],
                metadatas=[{"name": task_name}],
            )
            self.skills[task_name] = {
                "trajectory": task_trajectory,
                "description": skill_description,
            }
            assert self.vectordb._collection.count() == len(
                self.skills
            ), "vectordb is not synced with skills.json"

    def generate_skill_description(self, task_trajectory, task_name):
        messages = [
            SystemMessage(content='''You are a helpful assistant that writes a description of the task resolution trajectory.

1) Try to summarize the function in no more than 6 sentences.
2) Your response should be a single line of text.

For example, if the trajectory is:

Instruction:  
i am looking for flower fairy giel with pink wing elves pillow cover for living room, and price lower than 50.00 dollars 
[Search] 

Action: search[flower fairy giel pink wing elves pillow cover living room]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B09631NVQT] 
Dachshund Dog Best Friend Forever Pillow Cover Home Decorative Linen Pillow Cases Hidden Zipper 18" X 18" Cushion Covers Dachshund Gifts for Dog Lovers Sofa Couch Car Living Room 
$15.79 
[B0967D7RZN] 
UYTI Fairy Girl with Wing Elves Flying Butterflies Decorative Square Square Zippered Cushion Throw Case Pillow Case Cover 18X18 In, One Size 
$14.98 
[B08169JG35] 
JWH Pink 3D Flower Pillow Aesthetic Valentine Day Pillow Covers Round Shaped Decorative Pillowcase Gifts Cushion Covers Farmhouse Bed Living Room Sofa Couch Decor Shams with Pillow Insert 12 Inch 
$25.01 

Action: think[B0967D7RZN is flower fairy giel with pink wing elves pillow cover for living room and it is less than 50 dollars.]
Observation: OK.

Action: click[B0967D7RZN]
Observation: 
[Back to Search] 
[< Prev] 
color [bts][demon slayer][eiffel tower bike butterfly][fairy girl with wing elves flying butterflies decorative square][ian somerhalder damon salvatore the vampire diaries][mushroom boudoir][papel de parede para celular anime][sonic the hedgehog1][supernatural]
UYTI Fairy Girl with Wing Elves Flying Butterflies Decorative Square Square Zippered Cushion Throw Case Pillow Case Cover 18X18 In, One Size 
Price: $14.98 
Rating: N.A. 
[Description] 
[Features] 
[Reviews] 
[Buy Now] 

Action: think[The item is good to buy.]
Observation: OK.

Action: click[Buy Now]
Observation: Your score (min 0.0, max 1.0): 1.0

Then you would write:

The trajectory is about the complete process of buying flower fairy giel with pink wing elves pillow cover for living room online.
'''),
            HumanMessage(
                content=task_trajectory
            ),
        ]
        skill_description = self.llm.invoke(messages).content
        return skill_description

    def retrieve_skills(self, query):
        k = min(self.vectordb._collection.count(), self.retrieval_top_k)
        if k == 0:
            return []
        docs_and_scores = self.vectordb.similarity_search_with_score(query, k=k)
        skills = []
        for doc, _ in docs_and_scores:
            skills.append({'task_name':doc.metadata["name"],'task_trajectory':self.skills[doc.metadata["name"]]["trajectory"]})
        print(skills)
        return str(skills)

