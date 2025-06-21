# from utils import llm_response
import inspect
import json
from typing import Dict, List, TypedDict
from modules_predictor.planning_modules import *
from modules_predictor.reasoning_modules import *
from modules_predictor.tooluse_modules import *
from modules_predictor.memory_modules import *
from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)
import sys
import os
import requests
from openai import OpenAI
from typing import Optional, List
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
completion_tokens = prompt_tokens = 0
Model = Literal["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-instruct", "gpt-4o"]

# Define types
class ModuleInfo(TypedDict):
    thought: str
    name: str
    module_type: str
    code: str
    performance: float

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion(prompt: str, model: Model, temperature: float = 0.0, max_tokens: int = 500, stop_strs: Optional[List[str]] = None, n = 1) -> str:
    global completion_tokens, prompt_tokens

# @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_chat(prompt: str, model: Model, temperature: float = 0.0, max_tokens: int = 500, stop_strs: Optional[List[str]] = None, messages = None, n = 1) -> str:
    global completion_tokens, prompt_tokens
    assert model != "text-davinci-003"
    if messages is None:
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stop=stop_strs,
        n=n,
        temperature=temperature,
        response_format={"type": "json_object"}
    )

    completion_tokens += response.usage.completion_tokens
    prompt_tokens += response.usage.prompt_tokens
    if n > 1:
        responses = [choice.message.content.replace('>', '').strip() for choice in response.choices]
        return responses
    return response.choices[0].message.content.replace('>', '').strip()


def llm_response(prompt, model: Model, temperature: float = 0.0, max_tokens: int = 500, stop_strs: Optional[List[str]] = None, n=1) -> str:
    if isinstance(prompt, str):
        if model == 'gpt-3.5-turbo-instruct':
            comtent = get_completion(prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens, stop_strs=stop_strs, n=n)
        else:
            comtent = get_chat(prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens, stop_strs=stop_strs, n=n)
    else:
        messages = prompt
        prompt = prompt[1]['content']
        if model == 'gpt-3.5-turbo-instruct':
            comtent = get_completion(prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens, stop_strs=stop_strs, n=n)
        else:
            comtent = get_chat(prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens, stop_strs=stop_strs, messages=messages, n=n)
    return comtent

def get_class_code(class_name):
    source_code = inspect.getsource(class_name)
    
    code_str = source_code.replace('\r\n', '\n').replace('\r', '\n')
    
    return code_str

def get_module_code(module_dict):
    prompt_answer = "ALFworld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).\n"
    
    # Planning module
    planning = module_dict['planning'].lower()
    prompt_answer += f"Planning module: {planning.capitalize()}\n"
    if planning != 'none':
        planning_class = eval(f"Planning{planning.upper()}")
        prompt_answer += get_class_code(planning_class) + "\n"
        
    # Reasoning module  
    reasoning = module_dict['reasoning'].lower()
    prompt_answer += f"Reasoning module: {reasoning.capitalize()}\n"

    reasoning_class = eval(f"Reasoning{reasoning.upper()}")
    prompt_answer += get_class_code(reasoning_class) + "\n"
    
    # Tooluse module
    tooluse = module_dict['tooluse'].lower()
    prompt_answer += f"Tooluse module: {tooluse.capitalize()}\n"
    if tooluse != 'none':
        tooluse_class = eval(f"Tooluse{tooluse.upper()}")
        prompt_answer += get_class_code(tooluse_class) + "\n"
        
    # Memory module
    memory = module_dict['memory'].lower() 
    prompt_answer += f"Memory module: {memory.capitalize()}\n"
    if memory != 'none':
        memory_class = eval(f"Memory{memory.upper()}")
        prompt_answer += get_class_code(memory_class)
        
    return {
        "prompt_answer": prompt_answer,
        "label": float(module_dict['performance'])
    }

def predict_performance(candidates: Dict[str, Dict[str, str]], archives: Dict[str, List[ModuleInfo]], agents: List[dict[str, str]]):
    # Read alfworld_results.json file
    with open('alfworld_results.json', 'r') as f:
        alfworld_results = json.load(f)

    # Iterate through results to generate golden_case
    golden_case = []
    golden_case_list = []
    for result in alfworld_results:
        if result['performance'] == {}:
            continue
        case = {
            'planning': result['config']['planning'],
            'reasoning': result['config']['reasoning'], 
            'tooluse': result['config']['tooluse'],
            'memory': result['config']['memory'],
            'performance': result['performance']
        }
        golden_case.append(get_module_code(case))
        golden_case_list.append(case)
        
    # Randomly split into training and test sets
    import random
    random.seed(42)
    combined = list(zip(golden_case, golden_case_list))
    random.shuffle(combined)
    golden_case[:], golden_case_list[:] = zip(*combined)
    train_split = int(len(golden_case) * 0.8)
    train_data = golden_case[:train_split][:85]
    for item in train_data:
        item['performance'] = item.pop('label')


    task_description = "ALFworld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).\n"
    
    # Based on the provided agents, get corresponding modules from archives, similar to get_module_code to compose respective agents, and finally form a batch
    batch = []
    for agent in agents:
        agent_code = task_description
        planning = agent['planning']
        planning_code = next(module['code'] for module in archives['planning'] if module['name'].lower() == planning.lower())
        agent_code += f"Planning module: {planning}\n"
        agent_code += planning_code + "\n"
        reasoning = agent['reasoning']
        reasoning_code = next(module['code'] for module in archives['reasoning'] if module['name'].lower() == reasoning.lower())
        agent_code += f"Reasoning module: {reasoning}\n"
        agent_code += reasoning_code + "\n"
        tooluse = agent['tooluse']
        tooluse_code = next(module['code'] for module in archives['tooluse'] if module['name'].lower() == tooluse.lower())
        agent_code += f"Tooluse module: {tooluse}\n"
        agent_code += tooluse_code + "\n"
        memory = agent['memory']
        memory_code = next(module['code'] for module in archives['memory'] if module['name'].lower() == memory.lower())
        agent_code += f"Memory module: {memory}\n"
        agent_code += memory_code
        batch.append(agent_code)
    
    prompt = f"""You are a performance estimator. Now you need to estimate the performance of a LLM-based agent solving an ALFworld task (sequential decision making tasks with steps including finding hidden objects, moving objects and manipulating objects with other objects ). The agent is composed of four fundamental modules: planning, reasoning, tool use and memory. Planning module candidates and descriptions: {candidates['planning']}, Reasoning module candidates and descriptions: {candidates['reasoning']}, Tool use module candidates and descriptions: {candidates['tooluse']}, Memory module candidates and descriptions: {candidates['memory']}. The performance of some existing module combinations: {train_data}. The module combination you need to predict: {batch}. You're going to have to predict each of the {len(batch)} combinations I've given you. Be sure to give exact predictions. Your output should be of the following json format:
    {{'predictions':[{{'planning':'deps', 'reasoning':'io', 'tooluse':'None', 'memory':'dilu', 'performance': ''}},
    {{'planning':'openagi', 'reasoning':'CoT', 'tooluse':'None', 'memory':'generative', 'performance': ''}}]}}"""

    response = llm_response(prompt=prompt, model='gpt-4o', temperature=0.0)
    print(response)
    result = eval(response)['predictions']
    # Check if the result length matches the batch length, fill with 0 if not matching
    if len(result) < len(batch):
        print(f"Warning: Number of prediction results ({len(result)}) is less than batch size ({len(batch)}), will be filled with 0")
        # Fill in missing prediction results
        while len(result) < len(batch):
            result.append({
                'planning': 'None',
                'reasoning': 'None', 
                'tooluse': 'None',
                'memory': 'None',
                'performance': 0.0
            })
    return [pred['performance'] for pred in result]
