import os
import re
import ast
from utils import llm_response
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from tooluse_IO_pool import tooluse_IO_pool

class ToolUseBase():
    def __init__(self, llms_type):
        self.llm_type = llms_type[0]
    
    def format_prompt(self, tool_pool, task_description, tool_instruction, feedback_of_previous_tools):
        return f'''You have access to the following tools:
{tool_pool}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
{tool_instruction}
You must use the tools by outputting the tool name followed by its arguments, delimited by commas.
You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
You can only invoke one tool at a time.
You must begin your tool invocation with 'Action:' and end it with 'End Action'.
Your tool invocation format must follow the invocation format in the tool description.
{feedback_of_previous_tools}
'''

class ToolUseIO(ToolUseBase):
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        tool_pool = tooluse_IO_pool.get(task_description)
        prompt = self.format_prompt(tool_pool, task_description, tool_instruction, feedback_of_previous_tools)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1) 
        return string  

class ToolUseAnyTool(ToolUseBase):
    def __init__(self, llms_type):
        super().__init__(llms_type)
        self.dicts = {}
        self.tool_description = {}
        for name, tools in tooluse_IO_pool.items():
            pattern = r'\[\d+\] (\w+): (.+?)(?=\[\d+\]|\Z)'
            matches = re.findall(pattern, tools, re.DOTALL)
            self.tool_description[name] = {key: value.strip() for key, value in matches}
            category_prompt = f'''{self.tool_description[name]}
    You have a series of tools, you need to divide them into several categories, such as data calculation, trip booking and so on.
    All tools should be included in categories.
    your output format must be as follows:
    category 1 : {{'category name': 'category description', 'tool list': ['tool 1 name', 'tool 2 name']}}
    category 2 : {{'category name': 'category description', 'tool list': ['tool 1 name', 'tool 2 name']}}
    '''
            string = llm_response(prompt=category_prompt, model=self.llm_type, temperature=0.1)
            dict_strings = re.findall(r"\{[^{}]*\}", string)
            self.dicts[name] = [ast.literal_eval(ds) for ds in dict_strings]
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        prompt = f'''{self.dicts[task_description]}
You need to select the appropriate tool category from the list of available tools according to the task description to complete the task: 
{tool_instruction}
You can only invoke one category at a time.
Completed steps: {feedback_of_previous_tools}
You need to think about what tools do you need next.
Output category name directly.
Your output must be of the following format:
Category name: 
'''
        category_name = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1).split(':')[-1].strip()
        # Matching and retrieving tools
        matched_tools = {}
        for d in self.dicts[task_description]:
            if d.get('category name').lower().strip() == category_name.lower().strip():
                matched_tools = {tool: self.tool_description[task_description][tool] for tool in d['tool list']}
                break
        prompt = self.format_prompt(matched_tools, task_description, tool_instruction, feedback_of_previous_tools)
        return llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)

class ToolUseToolBench(ToolUseBase):
    def __init__(self, llms_type):
        super().__init__(llms_type)
        self.scenario_memory = {}
        
        for name, tools in tooluse_IO_pool.items():
            db_path = os.path.join('./db', f'api_pool{name}/') 
            self.embedding = OpenAIEmbeddings()       
            self.scenario_memory[name] = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
            
            api_pattern = re.compile(r"\[(\d+)\] ([^:]+): (.+?)(?=\[\d+\]|\Z)", re.DOTALL)
            api_matches = api_pattern.findall(tools)
            documents = [
                Document(
                    page_content=api_description.split('.')[0].strip() + '.',
                    metadata={
                        "name": api_name.strip(),
                        "description": f"[{api_id}] {api_name}: {api_description.strip()}"
                    }
                )
                for api_id, api_name, api_description in api_matches
            ]
            
            if self.scenario_memory[name]._collection.count() == 0:
                self.scenario_memory[name].add_documents(documents)

    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        similarity_results = self.scenario_memory[task_description].similarity_search_with_score(tool_instruction, k=4)
        tool_pool = [result[0].metadata['description'] for result in similarity_results]
        prompt = self.format_prompt(tool_pool, task_description, tool_instruction, feedback_of_previous_tools)
        string = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1)
        return string

class ToolUseToolBenchFormer(ToolUseBase):
    def __init__(self, llms_type):
        super().__init__(llms_type)
        self.scenario_memory = {}
        
        for name, tools in tooluse_IO_pool.items():
            db_path = os.path.join('./db', f'api_pool{name}/') 
            self.embedding = OpenAIEmbeddings()       
            self.scenario_memory[name] = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
            
            api_pattern = re.compile(r"\[(\d+)\] ([^:]+): (.+?)(?=\[\d+\]|\Z)", re.DOTALL)
            api_matches = api_pattern.findall(tools)
            documents = [
                Document(
                    page_content=api_description.split('.')[0].strip() + '.',
                    metadata={
                        "name": api_name.strip(),
                        "description": f"[{api_id}] {api_name}: {api_description.strip()}"
                    }
                )
                for api_id, api_name, api_description in api_matches
            ]
            
            if self.scenario_memory[name]._collection.count() == 0:
                self.scenario_memory[name].add_documents(documents)

    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        similarity_results = self.scenario_memory[task_description].similarity_search_with_score(tool_instruction, k=4)
        tool_pool = [result[0].metadata['description'] for result in similarity_results]
        
        prompt = self.format_prompt(tool_pool, task_description, tool_instruction, feedback_of_previous_tools)
        
        strings = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, n=3)
        
        return self.get_votes(tool_pool, tool_instruction, feedback_of_previous_tools, strings)

    def get_votes(self, tool_pool, tool_instruction, feedback_of_previous_tools, strings):
        prompt = f'''You have access to the following tools:
{tool_pool}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
{tool_instruction}
You must use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
You can only invoke one tool at a time.
You must begin your tool invocation with 'Action:' and end it with 'End Action'.
Your tool invocation format must follow the invocation format in the tool description.
{feedback_of_previous_tools}
------------
Given several answers, decide which answer is most promising. Output "The best answer is {{s}}", where s the integer id of the choice.
'''     
        for i, y in enumerate(strings, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=0.3, n=5)
        vote_results = [0] * len(strings)
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(len(strings)):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
        ids = list(range(len(strings)))
        select_id = sorted(ids, key=lambda x: vote_results[x], reverse=True)[0]
        return strings[select_id]

class ToolUseToolFormer(ToolUseBase):
    def __init__(self, llms_type):
        super().__init__(llms_type)
        
    def __call__(self, task_description, tool_instruction, feedback_of_previous_tools):
        tool_pool = tooluse_IO_pool.get(task_description)
        
        prompt = self.format_prompt(tool_pool, task_description, tool_instruction, feedback_of_previous_tools)
        
        strings = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, n=3)
        
        return self.get_votes(tool_pool, tool_instruction, feedback_of_previous_tools, strings)

    def get_votes(self, tool_pool, tool_instruction, feedback_of_previous_tools, strings):
        prompt = f'''You have access to the following tools:
{tool_pool}
You need to select the appropriate tool from the list of available tools according to the task description to complete the task:
{tool_instruction}
You must use the tools by outputing the tool name followed by its arguments, delimited by commas.
You can optionally express your thoughts using natural language before your action. For example, 'Thought: I want to use tool_name to do something. Action: <your action to call tool_name> End Action'.
You can only invoke one tool at a time.
You must begin your tool invocation with 'Action:' and end it with 'End Action'.
Your tool invocation format must follow the invocation format in the tool description.
{feedback_of_previous_tools}
------------
Given several answers, decide which answer is most promising. Output "The best answer is {{s}}", where s the integer id of the choice.
'''     
        for i, y in enumerate(strings, 1):
            prompt += f'Answer {i}:\n{y}\n'
        vote_outputs = llm_response(prompt=prompt, model=self.llm_type, temperature=0.3, n=5)
        vote_results = [0] * len(strings)
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(len(strings)):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
        ids = list(range(len(strings)))
        select_id = sorted(ids, key=lambda x: vote_results[x], reverse=True)[0]
        return strings[select_id]

