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
            if 'The correct trajectory is' in current_situation:
                self.addMemory(current_situation)
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

#下面是各模块的一些具体例子,thought是该模块的特性和大致描述，name是名字, module type是模块类型，code是IO标准化后的代码

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
            if 'The correct trajectory is' in current_situation:
                self.addMemory(current_situation)
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = query_scenario
            # Based on the task name to retrieve the relevant task solving trajectory
            if self.scenario_memory._collection.count() == 0:
                return '' 
            similarity_results = self.scenario_memory.similarity_search_with_score(
                task_name, k=3)
            fewshot_results = []
            for idx in range(0, len(similarity_results)):
                fewshot_results.append(str(similarity_results[idx][0].metadata))
            return "\nHere is a similar task and the correct handling trajectory in this case: " + ', '.join(fewshot_results)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory
            task_trajectory = current_situation
            task_name = re.search(r'Task : (.*?) \nThe correct trajectory is', current_situation)
            if task_name is not None:
                sce_descrip = task_name.group(1)
                doc = Document(
                    page_content=sce_descrip,
                    metadata={"task_name": sce_descrip,
                            'task_trajectory': task_trajectory}
                )
                id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "52%"
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
            if 'The correct trajectory is' in current_situation:
                self.addMemory(current_situation)
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = query_scenario
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
            output = str({'task_name':similarity_results[idx][0].metadata['task_name'],'task_trajectory':similarity_results[idx][0].metadata['task_trajectory']})
            return "\nHere is a similar task and the correct handling trajectory in this case: " + ', '.join(output)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory
            task_trajectory = current_situation
            task_name = re.search(r'Task : (.*?) \nThe correct trajectory is', current_situation)
            sce_descrip = task_name.group(1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_name": sce_descrip,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "56%"
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
            if 'The correct trajectory is' in current_situation:
                self.addMemory(current_situation)
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = query_scenario
            # Based on the task name to retrieve the relevant task solving trajectory    
            if self.scenario_memory._collection.count() == 0:
                print("The memory vector database is empty. Cannot perform search.")
                return ''
            # Retrieve a trajectory and output guidance to heuristically assist the LLM in completing the current task
            similarity_results = self.scenario_memory.similarity_search_with_score(
                task_name, k=1)
            few_experience_results = []
            for idx in range(0, len(similarity_results)):
                prompt = f'''You will be given a successful case where you successfully complete the task. Then you will be given a ongoing task. Do not summarize these two cases, but rather use the successful case to think about the strategy and path you took to attempt to complete the task in the ongoning task. Devise a concise, new plan of action that accounts for your task with reference to specific actions that you should have taken. You will need this later to solve the task. Give your plan after "Plan".
    Success Case:
    {similarity_results[idx][0].metadata['task_trajectory']}
    Ongoning task:
    {query_scenario}
    Plan:
    '''
                few_experience_results.append(llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)) 
            return 'Plan from successful attempt in similar task:\n' + '\n'.join(few_experience_results)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory
            task_trajectory = current_situation
            task_name = re.search(r'Task : (.*?) \nThe correct trajectory is', current_situation)
            sce_descrip = task_name.group(1)
            doc = Document(
                page_content=sce_descrip,
                metadata={"task_name": sce_descrip,
                        'task_trajectory': task_trajectory}
            )
            id = self.scenario_memory.add_documents([doc])
    """,
    "performance": "40%"
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
            if 'The correct trajectory is' in current_situation:
                self.addMemory(current_situation)
            else:
                return self.retriveMemory(current_situation)
        def retriveMemory(self, query_scenario):
            # Task name
            task_name = query_scenario     
            # Based on the task name to retrieve the relevant task solving trajectory
            if self.scenario_memory._collection.count() == 0:
                print("The memory vector database is empty. Cannot perform search.")
                return '' 
            similarity_results = self.scenario_memory.similarity_search_with_score(task_name, k=1)
            fewshot_results = []
            for idx in range(0, len(similarity_results)):
                fewshot_results.append(similarity_results[idx][0].metadata['task_trajectory'])
            return  "\nHere is a similar task and the correct handling trajectory in this case: " + ', '.join(fewshot_results)
        def addMemory(self, current_situation):
            # Store the task resolution trajectory, and summarize the task resolutiong trajectory  as the index
            task_trajectory = current_situation
            task_name = re.search(r'Task : (.*?) \nThe correct trajectory is', current_situation)
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
    "performance": "54%"
}

system_prompt = """You are a helpful assistant. Make sure to return in a WELL-FORMED JSON object."""

base = """# Overview
You are an expert machine learning researcher testing various LLM agents. Your objective is to design memory modules such as prompts and control flows within these agents to solve complex tasks. The agents have four modules including planning (decomposing a large task into sub-tasks), reasoning (addressing a sub-task), tool use (selecting appropriate external tools for task solving) and memory (read and write experience, observations). \
Your aim is to design an agent with optimal memory module performing well on scienceworld (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ).

# Task Overview:
ScienceWorld is a complex interactive text environment that poses a significant challenge to agents' scientific commonsense. This environment requires agents to navigate through 8 distinct functional rooms (e.g., workshop, kitchen) and utilize the tools to complete tasks such as 'measure the melting point of the orange juice'.
To solve this task, you need to first decompose the task using the planning module. Reasoning and memory modules are then used to solve each subtask. This requires strong command following, as well as common sense reasoning.

# A task solving trajectory from scienceworld:
Task Description: Your task is to boil water. For compounds without a boiling point, combusting the substance is also acceptable. First, focus on the substance. Then, take actions that will cause it to change its state of matter.\n\nACTION: look around\nOBSERVATION: This room is called the hallway. In it, you see: \n\ta picture\n\ta substance called air\n\tthe agent\nYou also see:\n\tA door to the green house (that is open)\n\tA door to the living room (that is open)\n\tA door to the art studio (that is open)\n\tA door to the kitchen (that is open)\n\tA door to the bedroom (that is open)\n\tA door to the workshop (that is open)\n\nACTION: open door to kitchen\nOBSERVATION: The door is already open.\n\nACTION: go to kitchen\nOBSERVATION: You move to the kitchen.\n\nACTION: look around\nOBSERVATION: This room is called the kitchen. In it, you see: \n\ta substance called soap\n\ta painting\n\ta thermometer, currently reading a temperature of 10 degrees celsius\n\ta counter. On the counter is: a bowl (containing a banana, a potato, a red apple, an orange), a drawer.\n\ta sink, which is turned off. In the sink is: nothing.\n\ta table. On the table is: a glass cup (containing nothing).\n\ta chair. On the chair is: nothing.\n\ta freezer. The freezer door is closed. \n\ta lighter\n\ta stopwatch, which is deactivated. \n\ta fridge. The fridge door is closed. \n\ta substance called air\n\ta cupboard. The cupboard door is closed. \n\ta oven, which is turned off. The oven door is closed. \n\ta glass jar (containing a substance called sodium chloride)\n\tthe agent\n\ta stove, which is turned off. On the stove is: nothing.\nYou also see:\n\tA door to the outside (that is open)\n\tA door to the bathroom (that is open)\n\tA door to the hallway (that is open)\n\nACTION: pick up thermometer\nOBSERVATION: You move the thermometer to the inventory.\n\nACTION: open cupboard\nOBSERVATION: The cupboard is now open.\n\nACTION: pick up metal pot\nOBSERVATION: You move the metal pot to the inventory.\n\nACTION: move metal pot to sink\nOBSERVATION: You move the metal pot to the sink.\n\nACTION: activate sink\nOBSERVATION: The sink is now activated.\n\nACTION: deactivate sink\nOBSERVATION: The sink is now deactivated.\n\nACTION: pick up metal pot\nOBSERVATION: You move the metal pot to the inventory.\n\nACTION: focus on substance in metal pot\nOBSERVATION: You focus on the water.\n\nACTION: pick up metal pot\nOBSERVATION: You move the metal pot to the inventory.\n\nACTION: move metal pot to stove\nOBSERVATION: You move the metal pot to the stove.\n\nACTION: activate stove\nOBSERVATION: The stove is now activated.\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 13 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 20 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 28 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 38 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 48 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 58 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 68 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 78 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 88 degrees celsius\n\nACTION: examine substance in metal pot\nOBSERVATION: a substance called water\n\nACTION: use thermometer in inventory on substance in metal pot\nOBSERVATION: the thermometer measures a temperature of 98 degrees celsius\n\nACTION: examine steam\nOBSERVATION: a substance called steam\n\nACTION: use thermometer in inventory on steam\nOBSERVATION: the thermometer measures a temperature of 107 degrees celsius\n\nACTION: wait1\nOBSERVATION: You decide to wait for 1 iterations.\n
# Memory module utility code:
```python
import shutil
import os
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma 
from langchain.docstore.document import Document
from utils import llm_response
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
        if 'The correct trajectory is' in current_situation:
            self.addMemory(current_situation)
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

The "generation" number indicates the sequential order of attempts made in designing the architecture. Each generation represents a distinct iteration or version, reflecting the evolution and refinement of the design.

# Output Instruction and Example:
The first key should be ("thought"), and it should capture your thought process for designing the next function. In the "thought" section, first reason about what should be the next memory module to try, then describe your memory module. 
The second key ("name") corresponds to the name of your next agent architecture.
Finally, the last key ("code") corresponds to the memory module in Python code that you would like to try. You must write a COMPLETE CODE in "code": Your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

Here is an example of the output format for the next agent architecture:

 [Memory_example]

You must strictly follow the exact input/output interface used above. Also, it could be helpful to set the LLM's role and temperature to further control the LLM's response.   DON'T try to use some function that doesn't exist.

# Your task
You are deeply familiar with prompting techniques and the agent works from the literature. Your goal is to maximize the specified performance metrics on the given task by proposing interestingly new memory module including prompts.
Observe the discovered memory modules carefully and think about what insights, lessons, or stepping stones can be learned from them.
You should mainly focus on the difference in the reading and writing of memory modules.
THINK OUTSIDE THE BOX.

"""

Reflexion_prompt = f""""[EXAMPLE]Carefully review the proposed new architecture and reflect on the following points:"

1. **Interestingness**: Assess whether your proposed architecture is interesting or innovative compared to existing methods in the archive. If you determine that the proposed architecture is not interesting, suggest a new architecture that addresses these shortcomings. 
- Make sure to check the difference between the proposed architecture and previous attempts.
- Compare the proposal and the architectures in the archive CAREFULLY, including their actual differences in the implementation.
- Decide whether the current architecture is innovative.
- USE CRITICAL THINKING!

2. **Implementation Mistakes**: Identify any mistakes you may have made in the implementation. Review the code carefully, debug any issues you find, and provide a corrected version.

3. **Improvement**: Based on the proposed architecture, suggest improvements in the detailed implementation that could increase its performance or effectiveness. In this step, focus on refining and optimizing the existing implementation without altering the overall design framework, except if you want to propose a different architecture if the current is not interesting.
- Observe carefully about whether the implementation is actually doing what it is supposed to do.
- Check if there is redundant code or unnecessary steps in the implementation. Replace them with effective implementation.
- Try to avoid the implementation being too similar to the previous agent.

And then, you need to improve or revise the implementation, or implement the new proposed architecture based on the reflection.

Your response should be organized as follows:

"reflection": Provide your thoughts on the interestingness of the architecture, identify any mistakes in the implementation, and suggest improvements.

"thought": Revise your previous proposal or propose a new architecture if necessary, using the same format as the example response.

"name": Provide a name for the revised or new architecture. (Don't put words like "new" or "improved" in the name.)

"code": Provide the corrected code or an improved implementation. Make sure you actually implement your fix and improvement in this code.
"""

def get_prompt_memory(current_archive, adaptive=False):
    archive_str = ",\n".join([json.dumps(sol) for sol in current_archive])
    archive_str = f"[{archive_str}]"
    prompt = base.replace("[ARCHIVE]", archive_str)
    prompt = prompt .replace("[Memory_example]", json.dumps(Memory_example))

    return system_prompt, prompt


def get_init_archive_memory():  #初始agent代码：Module-level搜索到的最好组合
    return [memory_dilu, memory_generative, memory_voyage, memory_TP]

#搜索过程中如果创造的新代码有问题，调用反思让其重写，这里可以根据具体实施过程中容易出现的bug加一些典型错误例子供其参考
def get_reflexion_prompt(prev_example):
    prev_example_str = "Here is the previous agent you tried:\n" + json.dumps(prev_example) + "\n\n"
    r1 = Reflexion_prompt.replace("[EXAMPLE]", prev_example_str) if prev_example else Reflexion_prompt.replace("[EXAMPLE]", "")
    return r1
# You need to pay special attention to the requirements mentioned in the "Task detail description" to ensure that the output of the task is formatted.