import argparse
import json
import os
import backoff
import requests
from openai import OpenAI

from prompt_reasoning import get_init_archive_reasoning, get_prompt_reasoning
from prompt_planning import get_init_archive_planning, get_prompt_planning
from prompt_memory import get_init_archive_memory, get_prompt_memory
from prompt_tooluse import get_init_archive_tooluse, get_prompt_tooluse

@backoff.on_exception(backoff.expo, Exception, max_tries=10)
def get_json_response_from_gpt_reflect(
        msg_list: list[dict[str, str]],
        model: str = 'gpt-4o-mini',
        temperature: float = 0.8
) -> dict:

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=msg_list,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    
    content = response.choices[0].message.content
    json_dict = json.loads(content)
    assert json_dict is not None
    return json_dict

def evolution(current_agent: dict[str, str], 
             planning_archive: list[dict[str, str]], 
             reasoning_archive: list[dict[str, str]], 
             tooluse_archive: list[dict[str, str]], 
             memory_archive: list[dict[str, str]]) -> tuple[list[tuple[str, str, str, str]], dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    """
    Generate new agents through module mutation
    
    Args:
        current_agent: Current agent configuration tuple (planning, reasoning, tooluse, memory)
        planning_archive: Planning module archive
        reasoning_archive: Reasoning module archive
        tooluse_archive: Tool use module archive
        memory_archive: Memory module archive

    Returns:
        evolution_agents: List of mutated new agents
        next_solution_reasoning: New reasoning module
        next_solution_planning: New planning module
        next_solution_memory: New memory module
        next_solution_tooluse: New tool use module
    """
    evolution_agents = []
    
    # Remove items with name "None" from each archive
    planning_modules = []
    planning_last_feedback = None
    for item in planning_archive:
        if item.get('name', '').lower() != 'none':
            item_copy = {k: v for k, v in item.items() if k != 'feedback'}
            planning_modules.append(item_copy)
            if 'feedback' in item and item['feedback'] != '':
                planning_last_feedback = item['feedback']
    
    memory_modules = []
    memory_last_feedback = None
    for item in memory_archive:
        if item.get('name', '').lower() != 'none':
            item_copy = {k: v for k, v in item.items() if k != 'feedback'}
            memory_modules.append(item_copy)
            if 'feedback' in item and item['feedback'] != '':
                memory_last_feedback = item['feedback']
    
    tooluse_modules = []
    tooluse_last_feedback = None
    for item in tooluse_archive:
        if item.get('name', '').lower() != 'none':
            item_copy = {k: v for k, v in item.items() if k != 'feedback'}
            tooluse_modules.append(item_copy)
            if 'feedback' in item and item['feedback'] != '':
                tooluse_last_feedback = item['feedback']
    
    reasoning_modules = []
    reasoning_last_feedback = None
    for item in reasoning_archive:
        if item.get('name', '').lower() != 'none':
            item_copy = {k: v for k, v in item.items() if k != 'feedback'}
            reasoning_modules.append(item_copy)
            if 'feedback' in item and item['feedback'] != '':
                reasoning_last_feedback = item['feedback']
    # Get prompts for each module
    system_prompt, prompt = get_prompt_reasoning(reasoning_modules, reasoning_last_feedback)
    msg_list_reasoning = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    
    system_prompt, prompt = get_prompt_planning(planning_modules, planning_last_feedback)
    msg_list_planning = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    
    system_prompt, prompt = get_prompt_memory(memory_modules, memory_last_feedback)
    msg_list_memory = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    
    system_prompt, prompt = get_prompt_tooluse(tooluse_modules, tooluse_last_feedback)
    msg_list_tooluse = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    try:
        # Generate new module variants
        def ensure_keys_exist(response: dict, keys: list[str]) -> bool:
            """Check if the generated result contains all specified keys"""
            return all(key in response for key in keys)

        required_keys = ["name", "thought", "module type", "code"]

        next_solution_reasoning = get_json_response_from_gpt_reflect(msg_list_reasoning)
        while not ensure_keys_exist(next_solution_reasoning, required_keys):
            next_solution_reasoning = get_json_response_from_gpt_reflect(msg_list_reasoning)

        next_solution_planning = get_json_response_from_gpt_reflect(msg_list_planning)
        while not ensure_keys_exist(next_solution_planning, required_keys):
            next_solution_planning = get_json_response_from_gpt_reflect(msg_list_planning)

        next_solution_memory = get_json_response_from_gpt_reflect(msg_list_memory)
        while not ensure_keys_exist(next_solution_memory, required_keys):
            next_solution_memory = get_json_response_from_gpt_reflect(msg_list_memory)

        next_solution_tooluse = get_json_response_from_gpt_reflect(msg_list_tooluse)
        while not ensure_keys_exist(next_solution_tooluse, required_keys):
            next_solution_tooluse = get_json_response_from_gpt_reflect(msg_list_tooluse)
        # Check and fix escape characters in code
        if 'code' in next_solution_reasoning:
            next_solution_reasoning['code'] = next_solution_reasoning['code'].replace("'\n'", "'\\n'").replace(":\n'", ":\\n'")
            
        if 'code' in next_solution_planning:
            next_solution_planning['code'] = next_solution_planning['code'].replace("'\n'", "'\\n'").replace(":\n'", ":\\n'")
            
        if 'code' in next_solution_memory:
            next_solution_memory['code'] = next_solution_memory['code'].replace("'\n'", "'\\n'").replace(":\n'", ":\\n'")
            
        if 'code' in next_solution_tooluse:
            next_solution_tooluse['code'] = next_solution_tooluse['code'].replace("'\n'", "'\\n'").replace(":\n'", ":\\n'")

        # Save generated new modules
        with open('output_reasoning.jsonl', 'a') as jsonl_file:
            jsonl_file.write(json.dumps(next_solution_reasoning) + '\n')
        with open('output_planning.jsonl', 'a') as jsonl_file:
            jsonl_file.write(json.dumps(next_solution_planning) + '\n')
        with open('output_memory.jsonl', 'a') as jsonl_file:
            jsonl_file.write(json.dumps(next_solution_memory) + '\n')
        with open('output_tooluse.jsonl', 'a') as jsonl_file:
            jsonl_file.write(json.dumps(next_solution_tooluse) + '\n')
        # Create 4 new agents, each replacing one module
        agent1 = {
            'planning': next_solution_planning["name"],
            'reasoning': current_agent['reasoning'],
            'tooluse': current_agent['tooluse'],
            'memory': current_agent['memory']
        }
        agent2 = {
            'planning': current_agent['planning'], 
            'reasoning': next_solution_reasoning["name"],
            'tooluse': current_agent['tooluse'],
            'memory': current_agent['memory']
        }
        agent3 = {
            'planning': current_agent['planning'],
            'reasoning': current_agent['reasoning'],
            'tooluse': next_solution_tooluse["name"],
            'memory': current_agent['memory']
        }
        agent4 = {
            'planning': current_agent['planning'],
            'reasoning': current_agent['reasoning'], 
            'tooluse': current_agent['tooluse'],
            'memory': next_solution_memory["name"]
        }
        
        evolution_agents.extend([agent1, agent2, agent3, agent4])

    except Exception as e:
        print("During LLM generate new solution:")
        print(e)
        
    return evolution_agents, next_solution_planning, next_solution_reasoning, next_solution_memory, next_solution_tooluse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',type=str,default='gpt-4')
    args = parser.parse_args()
    
    # Initialize archives
    planning_archive = get_init_archive_planning()
    reasoning_archive = get_init_archive_reasoning()
    tooluse_archive = get_init_archive_tooluse()
    memory_archive = get_init_archive_memory()
    
    # Initial agent
    initial_agent = ('None', 'IO', 'None', 'None')
    
    # Execute module mutation
    evolution_agents, next_solution_planning, next_solution_reasoning, next_solution_memory, next_solution_tooluse = evolution(initial_agent, planning_archive, reasoning_archive, tooluse_archive, memory_archive)
