voyage_prompt = '''You are a helpful assistant that writes a description of the task resolution trajectory.

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
import shutil
import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma 
from langchain.docstore.document import Document
from utils import llm_response
class MEMORY_VOYAGE():
    def __init__(self, llms_type):
        global flag
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', f'voyage/')
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
        task_trajectory = current_situation
        task_name = re.search(r'Instruction:\s+(.*?)\s+\[Search\]', current_situation)
        sce_descrip = task_name.group(1)
        prompt = voyage_prompt + task_trajectory
        task_description = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        doc = Document(
            page_content=task_description,
            metadata={"task_description": task_description,
                      'task_trajectory': task_trajectory}
        )
        id = self.scenario_memory.add_documents([doc])

