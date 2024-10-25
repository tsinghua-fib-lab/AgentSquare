import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
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

class MemoryDILU():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', 'dilu/')
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )

    def __call__(self, current_situation: str=''):
        if 'success.' in current_situation:
            self.addMemory(current_situation.replace('success.', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        query_scenario = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]        
        if self.scenario_memory._collection.count() == 0:
            return ''
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
        doc = Document(
            page_content=sce_descrip,
            metadata={"task_name": sce_descrip,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

class MemoryGenerative():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', 'generative/')
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )

    def __call__(self, current_situation: str=''):
        if 'success.' in current_situation:
            self.addMemory(current_situation.replace('success.', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]
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
        task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
        sce_descrip = task_name.group(1)
        doc = Document(
            page_content=sce_descrip,
            metadata={"task_name": sce_descrip,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])
        
class MemoryTP():
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', 'tp/')
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )

    def __call__(self, current_situation: str=''):
        if 'success.' in current_situation:
            self.addMemory(current_situation.replace('success.', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]
        if self.scenario_memory._collection.count() == 0:
            return ''
        similarity_results = self.scenario_memory.similarity_search_with_score(
            task_name, k=1)
        few_experience_results = []
        task_description = 'You are in the' + query_scenario.rsplit('You are in the', 1)[1]
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
        task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
        sce_descrip = task_name.group(1)
        doc = Document(
            page_content=sce_descrip,
            metadata={"task_name": sce_descrip,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

class MemoryVoyager():
    def __init__(self, llms_type):
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', 'voyage/')
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
        if self.scenario_memory._collection.count() == 0:
            return '' 
        similarity_results = self.scenario_memory.similarity_search_with_score(task_name, k=1)
        fewshot_results = []
        for idx in range(0, len(similarity_results)):
            fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
        return  '\n'.join(fewshot_results)

    def addMemory(self, current_situation):
        voyager_prompt = '''You are a helpful assistant that writes a description of the task resolution trajectory.

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
        task_trajectory = current_situation
        task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
        sce_descrip = task_name.group(1)
        prompt = voyager_prompt + task_trajectory
        task_description = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        doc = Document(
            page_content=task_description,
            metadata={"task_description": task_description,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

