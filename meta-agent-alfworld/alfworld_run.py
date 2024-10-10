import os
from openai import OpenAI
import time
import argparse
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
from utils import get_price

import yaml
import alfworld
import alfworld.agents.environment
with open('base_config.yaml') as reader:
    config = yaml.safe_load(reader)
    
split = "eval_out_of_distribution"

env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)

env = env.init_env(batch_size=1)

def process_ob(ob):
    if ob.startswith('You arrive at loc '):
        ob = ob[ob.find('. ')+2:]    
    return ob

import json
folder = './prompts/'
prompt_file = 'alfworld_3prompts.json'
with open(folder + prompt_file, 'r') as f:
    d = json.load(f)
folder = './prompts/'
prompt_file = 'alfworld_reasoning_prompt1.json'
with open(folder + prompt_file, 'r') as f:
    exp = json.load(f)

import sys

def alfworld_run(prompt_exp, AlfworldSolver, v, reason_exp, to_print=True, ob=''):
    init_prompt = prompt_exp + ob + '\n>'
    prompt = ''
    if to_print:
        print(ob)
        sys.stdout.flush()
    if AlfworldSolver.planning is None:
        for i in range(1, 50):
            task_description = init_prompt + prompt
            action = AlfworldSolver.reasoning(task_description, '', '').replace('>', '').strip()   
            observation, reward, done, info = env.step([action])
            observation, reward, done = process_ob(observation[0]), info['won'][0], done[0]
            if action.startswith('think:'):
                observation = 'OK.'
            if to_print:
                print(f'Act {i}: {action}\nObs {i}: {observation}')
                sys.stdout.flush()
            prompt += f' {action}\n{observation}\n>'
            if done:
                if reward:
                    print((ob+ '\n>' + prompt)[:-1])
                    if AlfworldSolver.memory is not None:
                        AlfworldSolver.memory((ob+ '\n>' + prompt)[:-1] + 'success.')
                return reward
    else:
        task_description = ob
        task_type = v
        sub_tasks = AlfworldSolver.planning(task_type=task_type, task_description=task_description, feedback='')
        i = 0
        print(task_type)
        print(sub_tasks)
        last_action = ''
        memory_pooi = []
        for sub_task_id in range(len(sub_tasks)):
            prompt = ''
            prompt_exp = ''

            for _ in range(20):
                values = list(reason_exp.values())
                try:
                    prompt_exp = values[sub_task_id]
                except IndexError:
                    return 0
                env_info = ob.split(':')[0] + ': '
                init_prompt = prompt_exp + env_info + 'Last step: ' + last_action + '. ' + 'Current task: ' + sub_tasks[sub_task_id]['reasoning instruction'] + '.\n>'
                task_description = init_prompt + prompt
                action = AlfworldSolver.reasoning(task_description, '', '').strip()   
                action = action.replace('>', '').strip()
                time.sleep(0.5)
                observation, reward, done, info = env.step([action.split(', end')[0].replace('.', '')])
                observation, reward, done = process_ob(observation[0]), info['won'][0], done[0]
                if action.startswith('think:'):
                    observation = 'OK.'             
                if to_print:
                    print(f'Act {i}: {action}\nObs {i}: {observation}')
                    sys.stdout.flush()
                prompt += f' {action}\n{observation}\n>'
                i += 1
                if done:
                    if reward:
                        if AlfworldSolver.memory is not None:
                            for memory_cache in memory_pooi:
                                AlfworldSolver.memory(memory_cache + 'success.')
                            AlfworldSolver.memory((env_info + last_action + '. ' + sub_tasks[sub_task_id]['reasoning instruction'] + '.\n>' + prompt)[:-1] + 'success.')
                    return reward
                
                if 'end' in action or ' complete' in action:
                    memory_pooi.append((env_info + last_action + '. ' + sub_tasks[sub_task_id]['reasoning instruction'] + '.\n>' + prompt)[:-1])
                    last_action = action
                    break
    return 0
def run_episodes(AlfworldSolver):
    prefixes = {
        'pick_and_place': 'put',
        'pick_clean_then_place': 'clean',
        'pick_heat_then_place': 'heat',
        'pick_cool_then_place': 'cool',
        'look_at_obj': 'examine',
        'pick_two_obj': 'puttwo'
    }
    cnts = [0] * 6
    rs = [0] * 6

    for _ in range(134):
        ob, info = env.reset()
        ob = '\n'.join(ob[0].split('\n\n')[1:])
        name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        print(name)
        for i, (k, v) in enumerate(prefixes.items()):
            if name.startswith(k):
                prompt = d[f'react_{v}_2'] + d[f'react_{v}_0'] + '\nHere is the task.\n'
                print(k, v)
                reason_exp = exp[v]
                r = alfworld_run(prompt, AlfworldSolver, v, reason_exp, ob=ob)
                rs[i] += r
                cnts[i] += 1
                break
        print(_+1, 'r', r, 'rs', rs, 'cnts', cnts, 'sum(rs)/sum(cnts)', sum(rs) / sum(cnts))
        completion_tokens, prompt_tokens, _ = get_price()
        print(f'completion_tokens:{completion_tokens}, prompt_tokens:{prompt_tokens}, price={completion_tokens*15/1000000+prompt_tokens*5/1000000}')
        print('------------\n')
    return sum(rs) / sum(cnts)


from AGENT import AGENT
from PLANNING_IO import PLANNING_IO
from PLANNING_HUGGINGGPT import PLANNING_HUGGINGGPT
from PLANNING_OPENAGI import PLANNING_OPENAGI
from PLANNING_VOYAGE import PLANNING_VOYAGE
from PLANNING_DEPS import PLANNING_DEPS
from PLANNING_TD import TemporalDependencyPlanner
from REASONING_IO import REASONING_IO
from REASONING_COT import REASONING_COT
from REASONING_TOT import REASONING_TOT
from REASONING_DILU import REASONING_DILU
from REASONING_SELFREFINE import REASONING_SELFREFINE
from REASONING_COT_SC import REASONING_COT_SC
from REASONING_STEPBACK import REASONING_STEPBACK
from MEMORY_DILU import MEMORY_DILU
from MEMORY_VOYAGE import MEMORY_VOYAGE
from MEMORY_TP import MEMORY_TP
from MEMORY_GENERATIVE import MEMORY_GENERATIVE
def run_alfworld(planning=None, reasoning=None, tooluse=None, memory=None, llms_type=['gpt=3.5-turbo-instruct']):
    planning_map = {
        'io': PLANNING_IO,
        'hugginggpt': PLANNING_HUGGINGGPT,
        'openagi': PLANNING_OPENAGI,
        'voyage': PLANNING_VOYAGE,
        'td': TemporalDependencyPlanner,
        'deps': PLANNING_DEPS,
        'none': None
    }
    reasoning_map = {
        'io': REASONING_IO,
        'cot': REASONING_COT,
        'cot-sc': REASONING_COT_SC,
        'tot': REASONING_TOT,
        'self-refine': REASONING_SELFREFINE,
        'dilu': REASONING_DILU,
        'stepback': REASONING_STEPBACK,
    }
    tooluse_map = {
        'none': None,
    }
    memory_map = {
        'none': None,
        'dilu': MEMORY_DILU,
        'voyage': MEMORY_VOYAGE, 
        'tp': MEMORY_TP,
        'generative': MEMORY_GENERATIVE,
    }
    if planning.lower() in planning_map:
        planning_func = planning_map[planning.lower()]
    else:
        raise KeyError("No corresponding planning module was found")
    if reasoning.lower() in reasoning_map:
        reasoning_func = reasoning_map[reasoning.lower()]
    else:
        raise KeyError("No corresponding reasoning module was found")
    if tooluse.lower() in tooluse_map:
        tooluse_func = tooluse_map[tooluse.lower()]
    else:
        raise KeyError("No corresponding tooluse module was found")
    if memory.lower() in memory_map:
        memory_func = memory_map[memory.lower()]
    else:
        raise KeyError("No corresponding memory module was found")
    AlfworldSolver = AGENT("AlfworldSolver", '', memory_func, reasoning_func, tooluse_func, planning_func, llms_type)
    res1 = run_episodes(AlfworldSolver)
    return res1
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ALFWorld with specified modules.')
    parser.add_argument('--planning', type=str, default='none', help='Specify planning module')
    parser.add_argument('--reasoning', type=str, default='io', help='Specify reasoning module')
    parser.add_argument('--tooluse', type=str, default='none', help='tooluse is not required in ALFworld')
    parser.add_argument('--memory', type=str, default='none', help='Specify memory module')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0125', help='Specify the LLM model type')
    args = parser.parse_args()
    run_alfworld(
        planning=args.planning,
        reasoning=args.reasoning,
        tooluse=args.tooluse,
        memory=args.memory,
        llms_type=[args.model]
    )
