import json

Memory_example = {
    "thought": "**Insights:**\nYour insights on what should be the next memory module for agents.\n**Overall Idea:**\nyour memory module description.\n**Implementation:**\ndescribe the implementation",
    "module type": "memory",
    "name": "Name of your proposed memory module",
    "code": """
    class [Name of your proposed memory module]():
        # Initialization of the class and database, do not modify this part
        def __init__(self, llms_type) -> None:
            self.llm_type = llms_type[0]  
            self.embedding = OpenAIEmbeddings()
            db_path = os.path.join('./db', 'memory/')
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            self.scenario_memory = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
        # Decide whether to retrieve or add the memory, do not modify this part
        def __call__(self, current_situation: str=''):
            if 'success.' in current_situation:
                self.addMemory(current_situation.replace('success.', ''))
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            '''
            Fill in your code here.
            '''
        def addMemory(self, current_situation):
            '''
            Fill in your code here.
            '''
"""
}

memory_dilu = {
    "thought":"Store the task resolution trajectory. Based on the task name to retrieve the relevant task solving trajectory",
    "name": "dilu",
    "module type": "memory",
    "code": """
    class MEMORY_DILU():
        # Initialization of the class and database, do not modify this part
        def __init__(self, llms_type) -> None:
            self.llm_type = llms_type[0]  
            self.embedding = OpenAIEmbeddings()
            db_path = os.path.join('./db', 'memory/')
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            self.scenario_memory = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
        # Decide whether to retrieve or add the memory, do not modify this part
        def __call__(self, current_situation: str=''):
            if 'success.' in current_situation:
                self.addMemory(current_situation.replace('success.', ''))
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]
            # Based on the task name to retrieve the relevant task solving trajectory
            if self.scenario_memory._collection.count() == 0:
                return '' 
            similarity_results = self.scenario_memory.similarity_search_with_score(
                task_name, k=1)
            fewshot_results = []
            for idx in range(0, len(similarity_results)):
                fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            return '\n'.join(fewshot_results)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory
            task_trajectory = current_situation
            task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
            sce_descrip = task_name.group(1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_name": sce_descrip,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "50%"
}

memory_generative = {
    "thought":"Store the task resolution trajectories. Retrieve relevant task-solving trajectories based on the task name, and select the one that the LLM considers most important",
    "name": "generative",
    "module type": "memory",
    "code": """
    class MEMORY_GENERATIVE():
        # Initialization of the class and database, do not modify this part
        def __init__(self, llms_type)
            self.llm_type = llms_type[0]  
            self.embedding = OpenAIEmbeddings()
            db_path = os.path.join('./db', 'memory/')
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            self.scenario_memory = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
        # Decide whether to retrieve or add the memory, do not modify this part            
        def __call__(self, current_situation: str=''):
            if 'success.' in current_situation:
                self.addMemory(current_situation.replace('success.', ''))
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]
            # Based on the task name to retrieve the relevant task solving trajectories
            if self.scenario_memory._collection.count() == 0:
                print("The memory vector database is empty. Cannot perform search.")
                return ''
            # Retrieve three trajectories and select the one that the LLM considers most important
            similarity_results = self.scenario_memory.similarity_search_with_score(
                task_name, k=3)
            fewshot_results = []
            importance_scores = []
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
                    importance_scores.append(int(match.group()))
                else:
                    importance_scores.append(0)
            max_scores = max(importance_scores)
            idx= importance_scores.index(max_scores)
            return similarity_results[idx][0].metadata['task_trajectory']
        def addMemory(self, current_situation):
            # Store the task resolution trajectory
            task_trajectory = current_situation
            task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
            sce_descrip = task_name.group(1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_name": sce_descrip,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "55%"
}

memory_TP = {
    "thought":"Store the task resolution trajectories. Retrieve relevant task-solving trajectories based on the task name, and output guidance to heuristically assist the LLM in completing the current task",
    "name": "tp",
    "module type": "memory",
    "code": """
    class MEMORY_TP():
        # Initialization of the class and database, do not modify this part
        def __init__(self, llms_type)
            self.llm_type = llms_type[0]  
            self.embedding = OpenAIEmbeddings()
            db_path = os.path.join('./db', 'memory/')
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            self.scenario_memory = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
        # Decide whether to retrieve or add the memory, do not modify this part
        def __call__(self, current_situation: str=''):
            if 'success.' in current_situation:
                self.addMemory(current_situation.replace('success.', ''))
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]    
            # Based on the task name to retrieve the relevant task solving trajectory    
            if self.scenario_memory._collection.count() == 0:
                print("The memory vector database is empty. Cannot perform search.")
                return ''
            # Retrieve a trajectory and output guidance to heuristically assist the LLM in completing the current task
            similarity_results = self.scenario_memory.similarity_search_with_score(
                task_name, k=1)
            few_experience_results = []
            task_description = 'You are in the' + query_scenario.rsplit('You are in the', 1)[1]
            for idx in range(0, len(similarity_results)):
                prompt = f'''You will be given a successful case where you successfully complete the task. Then you will be given a ongoing task. Do not summarize these two cases, but rather use the successful case to think about the strategy and path you took to attempt to complete the task in the ongoning task. Devise a concise, new plan of action that accounts for your task with reference to specific actions that you should have taken. You will need this later to solve the task. Give your plan after "Plan".
    Success Case:
    {similarity_results[idx][0].metadata['task_trajectory']}
    Ongoning task:
    {task_description}
    Plan:
    '''
                few_experience_results.append(llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)) 
            return 'Plan from successful attempt in similar task:\n' + '\n'.join(few_experience_results)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory
            task_trajectory = current_situation
            task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
            sce_descrip = task_name.group(1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_name": sce_descrip,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "30%"
}

memory_voyage = {
    "thought": "Store the task resolution trajectory, and summarize the task resolutiong trajectory. Based on the task summary to retrieve relevant the task resolution trajectory",
    "name": "voyage",
    "module type": "memory",
    "code": """
    class MEMORY_VOYAGE():
        # Initialization of the class and database, do not modify this part
        def __init__(self, llms_type):
            self.llm_type = llms_type[0]  
            self.embedding = OpenAIEmbeddings()
            db_path = os.path.join('./db', 'memory/')
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            self.scenario_memory = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path,
            )
        # Decide whether to retrieve or add the memory, do not modify this part
        def __call__(self, current_situation: str=''):
            if 'success.' in current_situation:
                self.addMemory(current_situation.replace('success.', ''))
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', query_scenario)[2]     
            # Based on the task name to retrieve the relevant task solving trajectory
            if self.scenario_memory._collection.count() == 0:
                print("The memory vector database is empty. Cannot perform search.")
                return '' 
            similarity_results = self.scenario_memory.similarity_search_with_score(task_name, k=1)
            fewshot_results = []
            for idx in range(0, len(similarity_results)):
                fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            return  '\n'.join(fewshot_results)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory, and summarize the task resolutiong trajectory  as the index
            task_trajectory = current_situation
            task_name = re.search(r'Your task is to:\s*(.*?)\s*>', current_situation)
            sce_descrip = task_name.group(1)
            # voyage_prompt is defined outside the class
            prompt = voyage_prompt + task_trajectory
            task_description = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_description": task_description,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "45%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview
You are an expert machine learning researcher testing various LLM agents. Your objective is to design memory modules such as prompts and control flows within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations). \
Your aim is to design an agent with optimal memory module performing well on ALFworld (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ).

# Task Overview:
ALFworld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).
To solve this task, you need to first decompose the task using the planning module. Reasoning and memory modules are then used to solve each subtask.

# A task solving trajectory from Alfworld:
You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.\nYour task is to: put a clean lettuce in diningtable.\n> think: To solve the task, I need to find and take a lettuce, then clean it with sinkbasin, then put it in diningtable. \nOK.\n> think: First I need to find a lettuce. A lettuce is more likely to appear in fridge (1), diningtable (1), sinkbasin (1), stoveburner (1-3), cabinet (1-13). I can check one by one, starting with fridge 1.\nOK.\n> go to fridge 1\nThe fridge 1 is closed.\n> open fridge 1\nYou open the fridge 1. The fridge 1 is open. In it, you see a cup 3, a egg 2, a potato 3, and a potato 2.\n> go to diningtable 1\nOn the diningtable 1, you see a apple 1, a bread 1, a butterknife 2, a cup 2, a fork 2, a knife 2, a knife 1, a ladle 1, a lettuce 1, a mug 2, a mug 1, a pan 2, a peppershaker 1, a spatula 3, a tomato 2, and a tomato 1.\n> think: Now I find a lettuce (1). Next, I need to take it.\nOK.\n> take lettuce 1 from diningtable 1\nYou pick up the lettuce 1 from the diningtable 1.\n> think: Now I take a lettuce (1). Next, I need to go to sinkbasin (1) and clean it.\nOK.\n> go to sinkbasin 1\nOn the sinkbasin 1, you see a apple 2, a ladle 2, a spoon 1, and a tomato 3.\n> clean lettuce 1 with sinkbasin 1\nYou clean the lettuce 1 using the sinkbasin 1.\n> think: Now I clean a lettuce (1). Next, I need to put it in/on diningtable 1.\nOK.\n> go to diningtable 1\nOn the diningtable 1, you see a apple 1, a bread 1, a butterknife 2, a cup 2, a fork 2, a knife 2, a knife 1, a ladle 1, a mug 2, a mug 1, a pan 2, a peppershaker 1, a spatula 3, a tomato 2, and a tomato 1.\n> put lettuce 1 in/on diningtable 1\nYou put the lettuce 1 in/on the diningtable 1.\n
# Memory module utility code:
```python
import shutil
import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma 
from langchain.docstore.document import Document
from utils import llm_response
class MEMORY():
    # Initialization of the class and database, do not modify this part
    def __init__(self, llms_type) -> None:
        self.llm_type = llms_type[0]  
        self.embedding = OpenAIEmbeddings()
        db_path = os.path.join('./db', 'memory/')
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )
    # Decide whether to retrieve or add the memory, do not modify this part
    def __call__(self, current_situation: str=''):
        if 'success.' in current_situation:
            self.addMemory(current_situation.replace('success.', ''))
        else:
            return self.retriveMemory(current_situation)
    def retriveMemory(self, query_scenario):
        '''
        Fill in your code here.
        '''
    def addMemory(self, current_situation):
        '''
        Fill in your code here.
        '''
# Memory module detail description:
The memory module stores or retrieves the incoming content and guides the current task based on the successful experience of the previous task.
```

# Discovered architecture archive
Here is the archive of the discovered memory module architectures:

[ARCHIVE]

The performance represents the completion rate of the task. 

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next memory module to try, then describe your memory module. 
The second key ("name") corresponds to the name of your next agent architecture.
Finally, the last key ("code") corresponds to the memory module in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next agent architecture:

 [Memory_example]

You must strictly follow the exact input/output interface used above. Also, it could be helpful to set the LLM's role and temperature to further control the LLM's response. DON'T try to use some function that doesn't exist.

# Your task
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new memory module including prompts.
Observe the discovered memory modules carefully and think about what insights, lessons, or stepping stones can be learned from them.
You should mainly focus on the difference in the reading and writing of memory modules.
THINK OUTSIDE THE BOX.

"""

def get_prompt_memory(current_archive):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Memory_example]", json.dumps(Memory_example))

    return system_prompt, prompt


def get_init_archive_memory():  
    return [memory_dilu, memory_generative, memory_voyage, memory_TP]
