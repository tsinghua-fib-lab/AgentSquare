
prompt = '''You are a helpful assistant that writes a description of the task resolution trajectory.

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
'''

import os
import re
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from langchain_chroma import Chroma 
import shutil
#需要根据具体任务对addmemorye和retrievememory进行修改，实现功能就是存入成功的问题解决轨迹，索引是任务的描述，llm生成
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
            SystemMessage(content=prompt),
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

