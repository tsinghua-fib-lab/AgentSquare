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
        global flag
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
        if 'success' in current_situation:
            self.addMemory(current_situation.replace('success', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario):
        query_scenario = re.findall(r'Instruction:\s+(.*?)\s+\[Search\]', query_scenario)[1]      
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
        task_name = re.search(r'Instruction:\s+(.*?)\s+\[Search\]', current_situation)
        sce_descrip = task_name.group(1)
        doc = Document(
            page_content=sce_descrip,
            metadata={"task_name": sce_descrip,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

class MemoryGenerative():
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
        
class MemoryTP():
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

class MemoryVoyager():
    def __init__(self, llms_type):
        global flag
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', f'voyager/')
        flag += 1
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path,
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
Webshop 
Instruction:  
i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
[Search]  

Action: search[3 ounce bright citrus deodorant sensitive skin]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B078GWRC1J] 
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B078GTKVXY] 
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B08KBVJ4XN] 
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar & Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack) 
$15.95  

Action: think[B078GWRC1J and B078GTKVXY are bright citrus deodorant less then 50 dollars. I can check B078GWRC1J first.]
Observation: OK.

Action: click[B078GWRC1J]
Observation: 
[Back to Search] 
[< Prev] 
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
Price: $10.99 
Rating: N.A. 
[Description] 
[Features] 
[Reviews] 
[Buy Now]  

Action: think[For 3 ounce bottle of bright citrus deodorant for sensitive skin, the item has options 'bright citrus' and '3 ounce (pack of 1)' and seems good to buy.]
Observation: OK.

Action: click[bright citrus]
Observation: You have clicked bright citrus. 

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1). 

Action: click[Buy Now]

Then you would write: The trajectory is about searching for a 3-ounce bright citrus deodorant for sensitive skin under $50, evaluating relevant options, selecting a suitable product, and finalizing the purchase.

Trajectory:
'''
        task_trajectory = current_situation
        task_name = re.search(r'Instruction:\s+(.*?)\s+\[Search\]', current_situation)
        sce_descrip = task_name.group(1)
        prompt = voyager_prompt + task_trajectory
        task_description = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        doc = Document(
            page_content=task_description,
            metadata={"task_description": task_description,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

