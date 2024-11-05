import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os
import re
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
from utils_llm import get_chat, get_completion, get_price
import subprocess

def main(iterations):
    #任务名称+描述
    task_description = 'ScienceWorld:An experimental environment for scientific experiments, including workshop and kitchen scenes, you need to complete some scientific experiments according to the requirements of each task and strictly use the executable commands of the environment.' 

    #待补充
    planning_candidate = {'None':'Do not use planning module',
                          'IO':'Input the task description to a LLM and directly output the sub-tasks',
                          'DEPS':'Input a task description in a LLM and output sub-goals. It is commonly used for embodied intelligence tasks',
                          'HUGGINGGPT':'Input a task description into a LLM and output as few sub-tasks as possible. It is often used for image processing tasks and focuses on the correlation between sub-tasks',
                          'OPENAGI':'Input a task description in a LLM and output a to-do list. It is often used to solve tasks using various tools'}
    #待补充
    reasoning_candidate = {'IO':'Input the problem description to a LLM and directly output the answer',
                           'CoT':'A reasoning method prompting LLMs to think step-by-step for eliciting multi-step reasoning behavior',
                           'TOT':'A reasoning method prompting LLMs to perform deliberate decision making by considering multiple different reasoning paths and self-evaluating choices to decide the next course of action, as well as looking ahead or backtracking when necessary to make global choices',
                           'self-refine':'A reasoning method for improving initial outputs from LLMs through iterative feedback and refinement',
                           'CoT_SC': 'Combine multiple answers from these Chain-of-Thought (CoT) agents to produce a more accurate final answer through ensembling.',
                           'STEPBACK': 'Let LLM first think about the principles involved in solving this task which could be helpful.',
                           'DILU': 'Added a system prompt to act like an expert on something'
                           }
  
    #待补充
    tooluse_candidate = {'None':'Do not use tool use module'
                         
                        }
    #待补充
    memory_candidate = {'None':'Do not use memory module',
                        'Dilu':'Retrieve past experiences based on task descrition',
                        'voyager':'Extract and summarize past resolution trajectories, and retrieve past experiences based on this',
                        'Generative Agents':'Extract and summarize past resolution trajectories, and retrieve the summarized experience'}

    #初始化已测试的case，根据目前具体测试情况修改
    tested_case = [{'planning':'IO', 'reasoning':'COT', 'tooluse':'None', 'memory':'None', 'succuss_rate':0.0, 'progress_rate':0.49, 'grounding_acc':0.34},
                    {'planning':'IO', 'reasoning':'IO', 'tooluse':'None', 'memory':'None', 'succuss_rate':0.0, 'progress_rate':0.04, 'grounding_acc':0.33}]

    for i in range(iterations):
        #目前未考虑communication模块
        prompt = 'You are an AI agent expert. Now you are required to design a LLM-based agent to solve the task of ' \
        + task_description + 'The agent is composed of four fundamental modules: planning, reasoning, tool use and memory. \
        For each module you are required to choose one from the follwing provided candidates. \
        Planning module candidates and descriptions: ' + str(planning_candidate) + ' Reasoning module candidates and descriptions: ' + str(reasoning_candidate) + ' Tool use module candidates and descriptions: ' + str(tooluse_candidate) + ' Memory module candidates and descriptions: ' + str(memory_candidate) \
        + 'The performance of some existing module combinations: ' + str(tested_case) +'. ' \
        + 'Where, success_rate represents the completion rate of all tasks, progress_rate represents the average completion progress of all tasks, and grounding_acc represents the percentage of valid actions(Agents commonly commit two types of errors: grounding errors, where the generated action cannot be executed, and planning errors, where the action is correct but does not contribute to progress.)'\
        + 'You are expected to give a new module combination to improve the performance on the task by considering (1) the matching degree between the module description and task description (2) performance of existing module combinations on the task. \
        Your answer should follow the format:' +str({'planning': '<your choice>', 'reasoning': '<your choice>', 'tooluse': '<your choice>', 'memory': '<your choice>'})

        # print(prompts)
        #os.environ['OPENAI_API_KEY'] = ''
        #print(prompt)
        model = 'gpt-3.5-turbo-instruct'
        response = get_completion(prompt=prompt, model=model, temperature=0.1)
        agent = eval(response)
        #print(response)
        planning = agent['planning']
        reasoning = agent['reasoning']
        tooluse = agent['tooluse']
        memory = agent['memory']
        planning = 'io'
        reasoning = 'io'
        tooluse = 'None'
        memory = 'None'
        #task_type = 'Wikipedia-based question-answer pairs'
        #feedback = ''
        #flag = 0
        #执行模块组合agent
        llms_type = ['gpt-3.5-turbo-0125']
        
        # result = subprocess.run([
        #     'bash', 'run.sh', 
        #     '--planning', planning, 
        #     '--reasoning', reasoning,
        #     '--memory', memory,
        #     '--tooluse', tooluse,
        #     '--model', ','.join(llms_type),
        #     ], text=True)
        
        process = subprocess.Popen([
            'bash', 'run.sh', 
            '--planning', planning, 
            '--reasoning', reasoning,
            '--memory', memory,
            '--tooluse', tooluse,
            '--model', ','.join(llms_type),
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 捕获标准输出和标准错误
        stdout_lines = []
        stderr_lines = []

        # 实时输出子进程的标准输出
        for line in process.stdout:
            print(line, end='')  # 输出到控制台
            stdout_lines.append(line)  # 捕获到变量
            if "The performance of the current module combination is" in line:
                Performance_line = line
        output_lines = ''.join(stdout_lines)
        print(output_lines)


        matches = re.search(r"success_rate:\s*([\d.]+),\s*progress_rate:\s*([\d.]+),\s*grounding_acc:\s*([\d.]+)", Performance_line)
        success_rate = float(matches.group(1))
        progress_rate = float(matches.group(2))
        grounding_acc = float(matches.group(3))
        #result = run_webshop(planning=planning, reasoning=reasoning, tooluse=tooluse, memory=memory, llms_type=llms_type)
        #更新case列表
        #agent.setdefault('performance', result)
        tested_case.append({'planning':planning, 'reasoning':reasoning, 'tooluse':'None', 'memory':'None', 'success_rate':success_rate, 'progress_rate':progress_rate, 'grounding_acc':grounding_acc})
        print (tested_case)
        # # 清空文件内容
        # with open('../results/gpt-3.5-turbo-0125/all_results.txt', 'w') as file:
        #     pass  # 不写入任何内容，文件将被清空

    
    #print(tested_case)


if __name__ == "__main__":
    iterations = 1
    main(iterations)

