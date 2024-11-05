import argparse
import copy
import json
import os
from collections import namedtuple

import backoff
import numpy as np
import openai
from tqdm import tqdm

from alfworld_prompt_reasoning import get_init_archive_reasoning, get_prompt_reasoning
from alfworld_prompt_planning import get_init_archive_planning, get_prompt_planning
from alfworld_prompt_memory import get_init_archive_memory, get_prompt_memory


client = openai.OpenAI()

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def get_json_response_from_gpt(
        msg,
        model,
        system_message,
        temperature=0.5
):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": msg},
        ],
        temperature=temperature, stop=None, response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    json_dict = json.loads(content)
    #估算成本
    # cost = response.usage.completion_tokens / 1000000 * 15 + response.usage.prompt_tokens / 1000000 * 5
    assert not json_dict is None
    return json_dict


@backoff.on_exception(backoff.expo, openai.RateLimitError)
def get_json_response_from_gpt_reflect(
        msg_list,
        model,
        temperature=0.8
):
    response = client.chat.completions.create(
        model=model,
        messages=msg_list,
        temperature=temperature, stop=None, response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    json_dict = json.loads(content)
    assert not json_dict is None
    return json_dict


#把根据四个模块组合agent进行性能测试的主程序文件复制过来
class Agent():
    '''
    TBD
    '''

def search(args):
    file_path = os.path.join(args.save_dir, f"{args.expr_name}_run_archive.json")
    #若已有搜索结果，可在已有的代码库上开始搜索
    # if os.path.exists(file_path):
    #     with open(file_path, 'r') as json_file:
    #         archive = json.load(json_file)
    #     if "generation" in archive[-1] and isinstance(archive[-1]['generation'], int):
    #         start = archive[-1]['generation']
    #     else:
    #         start = 0
    # else:
    #     archive = get_init_archive()
    #     start = 0

    #代码库为空，从Module-level得到的最好组合开始搜索 
    archive_reasoning = get_init_archive_reasoning()
    archive_planning = get_init_archive_planning()
    archive_memory = get_init_archive_memory()
    start = 0

    for solution in archive_reasoning:
        if 'performance' in list(solution.keys()):
            continue
    for solution in archive_planning:
        if 'performance' in list(solution.keys()):
            continue
    for solution in archive_memory:
        if 'performance' in list(solution.keys()):
            continue
        #需要evaluate一下初始的agent性能

    for n in range(start, args.n_generation):
        print(f"============Generation {n + 1}=================")
        system_prompt, prompt = get_prompt_reasoning(archive_reasoning)
        msg_list_reasoning = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        print(msg_list_reasoning)
        system_prompt, prompt = get_prompt_planning(archive_planning)
        msg_list_planning = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        print(msg_list_planning)
        system_prompt, prompt = get_prompt_memory(archive_memory)
        msg_list_memory = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        print(msg_list_memory)
        try: #这里分别memory reasoning planning
            # next_solution_reasoning = get_json_response_from_gpt_reflect(msg_list_reasoning, args.model) #调用LLM写新代码
            # next_solution_planning = get_json_response_from_gpt_reflect(msg_list_planning, args.model) #调用LLM写新代码
            next_solution_memory = get_json_response_from_gpt_reflect(msg_list_memory, args.model)
            # with open('output.jsonl', 'a') as jsonl_file:
            #      jsonl_file.write(json.dumps(next_solution_reasoning) + '\n')
            # for key, value in next_solution_reasoning.items():
            #     print(f"{key}: {value}")
            # with open('output_planning.jsonl', 'a') as jsonl_file:
            #      jsonl_file.write(json.dumps(next_solution_planning) + '\n')
            # for key, value in next_solution_planning.items():
            #     print(f"{key}: {value}")
            with open('output_memory.jsonl', 'a') as jsonl_file:
                 jsonl_file.write(json.dumps(next_solution_memory) + '\n')
            for key, value in next_solution_memory.items():
                print(f"{key}: {value}")
            
        ##如果写的代码经常出错可以加入下面的反思环节
            # Reflexion_prompt_1 = get_reflexion_prompt(archive[-1] if n > 0 else None)
            # msg_list.append({"role": "assistant", "content": str(next_solution)})
            # msg_list.append({"role": "user", "content": Reflexion_prompt_1})
            # next_solution = get_json_response_from_gpt_reflect(msg_list, args.model)
        except Exception as e:
            print("During LLM generate new solution:")
            print(e)
            continue
        prin
        # prin下的部分还没有改
        for _ in range(args.debug_max):
            try:
                acc = evaluate()  #（TBD,补充根据实际任务进行性能评估的代码）

            except Exception as e: #若evaluation时有bug，进行反思重写
                print("During evaluation:")
                print(e)
                msg_list.append({"role": "assistant", "content": str(next_solution)})
                msg_list.append({"role": "user", "content": f"Error during evaluation:\n{e}\nCarefully consider where you went wrong in your latest implementation. Using insights from previous attempts, try to debug the current code to implement the same thought. Repeat your previous thought in 'thought', and put your thinking for debugging in 'debug_thought'"})
                try:
                    next_solution = get_json_response_from_gpt_reflect(msg_list, args.model)
                except Exception as e:
                    print("During LLM generate new solution:")
                    print(e)
                    continue
                continue

        next_solution['performance'] = acc
        next_solution['generation'] = n + 1

        if 'debug_thought' in next_solution:
            del next_solution['debug_thought']
        if 'reflection' in next_solution:
            del next_solution['reflection']
        archive_reasoning.append(next_solution)

        # save results
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as json_file:
            json.dump(archive_reasoning, json_file, indent=4)


def evaluate():
    '''
    (TBD)
    '''
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='results/')
    parser.add_argument('--expr_name', type=str, default='webshop_gpt3.5_results')
    parser.add_argument('--n_generation', type=int, default=1) #迭代次数/新程序数量
    parser.add_argument('--debug_max', type=int, default=1) #最大debug次数/反思重写尝试次数
    parser.add_argument('--model',type=str,default='gpt-4o')

    args = parser.parse_args()
    # search
    search(args)

    # evaluate
    evaluate()  #根据实际参数修改，TBD
