import re
import os
import json
import logging
import pathlib
import backoff
import requests
import argparse
import traceback
import pandas as pd
from tasks import get_task_iterator, Task, ToolType, ActionMode
from tqdm import tqdm
from utils import get_price

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--action_mode", type=str, default="text_as_action")
parser.add_argument("--output_dir", type=str, default="outputs")
parser.add_argument("--task_regex_filter", type=str, default=None)
parser.add_argument("--n_tasks", type=int, default=None)
parser.add_argument("--n_turns_limit", type=int, default=10)
parser.add_argument("--dry_run", action="store_true")
parser.add_argument("--planning", required=True, help="planning module")
parser.add_argument("--reasoning", required=True, help="reasoning module")
parser.add_argument("--memory", required=True, help="memory module")
parser.add_argument("--tooluse", required=True, help="tooluse module")
parser.add_argument("--task_name", required=True, help="task_name")

args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
def postprocess_fn(generation: str) -> str:
    generation = generation.lstrip()
    # Regex pattern to find "Answer:" or "Action:"
    pattern_answer_action = r"(Answer:|Action:)"
    matches_answer_action = list(re.finditer(pattern_answer_action, generation))

    # If no matches or only one match of Answer/Action, return the original string
    if len(matches_answer_action) <= 1:
        return generation

    # Get the index of the start of the second match of Answer/Action
    second_match_start = matches_answer_action[1].start()

    # Trim the string to end before the second match of Answer/Action
    trimmed_generation = generation[:second_match_start].strip()

    # Find the index of the end of the first "Action:"
    first_action_end_index = trimmed_generation.find("Action:") + len("Action:")
    # Check for the next occurrence of "End Action" after the first "Action:"
    end_action_index = trimmed_generation.find("End Action", first_action_end_index)
    # Determine where to trim the string
    if end_action_index != -1:
        # Trim the string to the determined index
        trimmed_generation = trimmed_generation[:end_action_index+len("End Action")].strip()

    # Check for the next occurrence of "Thought:" after the first "Action:"
    next_thought_index = trimmed_generation.find("Thought:", first_action_end_index)
    if next_thought_index != -1:
        trimmed_generation = trimmed_generation[:next_thought_index].strip()
    
    return trimmed_generation

ACTION_MODES = [
    ActionMode.TEXT_AS_ACTION,
    ActionMode.JSON_AS_ACTION,
    ActionMode.CODE_AS_ACTION
]

def run_task(task_name: str, task: Task, action_mode: ActionMode, M3toolSolver, n_limit: int = 10):
    task: Task
    print("========================================")
    print(task_name, action_mode)
    cur_prompt, tool_description = task.get_prompt(action_mode)
    # print prompt in yellow
    print("Prompt:")
    print("\033[93m" + cur_prompt + "\033[0m")
    messages = [
        {
            "role": "user",
            "content": cur_prompt
        },
    ]
    is_correct = False
    n_turns = 0
    end_reason = "limit"

    if M3toolSolver.planning is None:
        feedback_of_previous_tools = ''
        while not is_correct and n_turns < n_limit:
            task_description = tool_description + feedback_of_previous_tools + "Based on the results of the tool use.\nPlease ONLY output the answer (e.g., single number), without any other text.\nYour output should be of the following format\n'Answer: Your answer here'"
            #print(args.task_name)
            generation = M3toolSolver.tooluse(args.task_name, tool_description, feedback_of_previous_tools).strip()
            #####feedback_of_previous_tools = feedback_of_previous_tools + generation + '\n'
            #print(generation)
            #print(feedback_of_previous_tools)
            #####answer_generation = M3toolSolver.reasoning(task_description, '', '')
            #####answer_generation = postprocess_fn(answer_generation)
            generation = postprocess_fn(generation)
            feedback_of_previous_tools = feedback_of_previous_tools + generation + '\n'
            print(task_description)
            answer_generation = M3toolSolver.reasoning(task_description, '', '')
            answer_generation = postprocess_fn(answer_generation)
            #tool_description = tool_description + 'The last round of instructions' + generation
            # Parse the generation
            parsed = task.parse_generation(generation)
            content_type = parsed["type"]
            content = parsed["content"]
            if "extra_info" in parsed and parsed["extra_info"] is not None:
                extra_info = parsed["extra_info"]
            else:
                extra_info = ""
            if content_type == "action":
                
                execution_result = task.execute_action(content, action_mode)

                content = str(execution_result)
 
                if extra_info != "":
                    content += "\n*Extra reminder: " + extra_info
                messages.append({
                    "role": "user",
                    "content": content
                })
                #tool_description += content
                feedback_of_previous_tools = feedback_of_previous_tools + content + '\n'
                '''
                if task.is_single_tool_task:  # Check correctness for single tool tasks
                    is_correct = task.check_answer(execution_result)
                    if is_correct:
                        print("Correct for single tool task!")
                        break
                '''
            else:
                messages.append({
                    "role": "user",
                    "content": content
                })
            parsed = task.parse_generation(answer_generation)
            answer_content = parsed["content"]
            is_correct = task.check_answer(answer_content)
            # Print last message in blue
            n_turns += 1
            print("\033[94m" + messages[-1]["content"] + "\033[0m")
    else:
        task_type = args.task_regex_filter
        task_description = tool_description
        sub_tasks = M3toolSolver.planning(task_type, task_description, '')
        history = ''
        print(sub_tasks)
        for sub_task_step in range(len(sub_tasks)):
            generation = M3toolSolver.tooluse(args.task_name, sub_tasks[sub_task_step]['tool instruction'], history).strip()
            generation = postprocess_fn(generation)
            parsed = task.parse_generation(generation)
            content = parsed["content"]
            execution_result = str(task.execute_action(content, action_mode))
            history = history + generation+ '\n' + execution_result + '\n'
            if sub_task_step != len(sub_tasks) - 1:
                task_description = sub_tasks[sub_task_step]['reasoning instruction'] + history + "Based on the results of the tool use.\nPlease ONLY output the answer (e.g., single number), without any other text.\nYour output should be of the following format\n'Answer: Your answer here'"
            else:
                task_description = tool_description + history + "Based on the results of the tool use.\nPlease ONLY output the answer (e.g., single number), without any other text.\nYour output should be of the following format\n'Answer: Your answer here'"
            reasoning_result = M3toolSolver.reasoning(task_description, '', '')
            history += reasoning_result
            answer_generation = postprocess_fn( reasoning_result )
            parsed = task.parse_generation(answer_generation)
            answer_content = parsed["content"]
            is_correct = task.check_answer(answer_content)
            if is_correct:
                break
        # Print last message in blue
        print("\033[94m" + messages[-1]["content"] + "\033[0m")
    
    if is_correct:
        end_reason = "correct"

    return {
        "task_name": task_name,
        "is_single_tool_task": task.is_single_tool_task,
        "action_mode": action_mode.value,
        "prompt": cur_prompt,
        "messages": messages,
        "expected_output": task.expected_output,
        "is_correct": is_correct,
        "n_turns": n_turns,
        "end_reason": end_reason,
    }


def run_tools(action_mode: ActionMode, fout, outputs, M3toolSolver):
    # Filter out tasks that have been run
    finished_task_names = set([output["task_name"] for output in outputs])
    print(f"Found {len(finished_task_names)=}")
    correct = 0
    total = 0
    # for task_name, task in tqdm(task_to_run):
    for i, task in enumerate(get_task_iterator()):
        task: Task
        task_name = task.name

        # Skip tasks that does not match the regex
        if args.task_regex_filter is not None \
            and re.search(args.task_regex_filter, task_name) is None:
            continue

        # Skip when max number of tasks is reached
        if args.n_tasks is not None and i >= args.n_tasks:
            break

        if task_name in finished_task_names:
            # skip tasks that have been run
            continue
        task.reset()
        cur_output = run_task(task_name, task, action_mode, M3toolSolver, args.n_turns_limit)
        total += 1
        if cur_output['is_correct']:
            correct += 1
        fout.write(json.dumps(cur_output) + "\n")
        task.free_resource()
    return correct, total
from AGENT import AGENT
from REASONING_COT_SC import REASONING_COT_SC
from TOOLUSE_ANYTOOL import TOOLUSE_ANYTOOL
from TOOLUSE_IO import TOOLUSE_IO
from TOOLUSE_TOOLBENCH import TOOLUSE_TOOLBENCH
from TOOLUSE_TOOLFORMER import TOOLUSE_TOOLFORMER
from TOOLUSE_TOOLBENCHFORMER import TOOLUSE_TOOLBENCHFORMER
def agent_build(planning=None, reasoning=None, tooluse=None, memory=None, llms_type=['gpt=3.5-turbo-instruct']):
    planning_map = {
        'none': None
    }
    reasoning_map = {
        'cot=sc': REASONING_COT_SC,
    }
    tooluse_map = {
        'anytool': TOOLUSE_ANYTOOL,
        'toolbench': TOOLUSE_TOOLBENCH,
        'toolformer': TOOLUSE_TOOLFORMER,
        'toolbenchformer': TOOLUSE_TOOLBENCHFORMER,
        'io': TOOLUSE_IO,
        'none': None
    }
    memory_map = {
        'none': None
    }
    if planning.lower() in planning_map:
        planning_func = planning_map[planning.lower()]
    else:
        raise KeyError("没有找到对应的规划功能")
    if reasoning.lower() in reasoning_map:
        reasoning_func = reasoning_map[reasoning.lower()]
    else:
        raise KeyError("没有找到对应的推理功能")
    if tooluse.lower() in tooluse_map:
        tooluse_func = tooluse_map[tooluse.lower()]
    else:
        raise KeyError("没有找到对应的工具调用功能")
    if memory.lower() in memory_map:
        memory_func = memory_map[memory.lower()]
    else:
        raise KeyError("没有找到对应的记忆功能")
    feedback = ''
    M3toolSolver = AGENT("PddlSolver", '', memory_func, reasoning_func, tooluse_func, planning_func, llms_type)
    return M3toolSolver
def run_m3tool():
    M3toolSolver = agent_build(planning=args.planning, reasoning=args.reasoning, tooluse=args.tooluse, memory=args.memory, llms_type=args.model.split(','))
    
    output_dir = f"{args.output_dir}/{args.model.split(',')[0]}"
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    action_mode = args.action_mode
    assert action_mode in [action_mode.value for action_mode in ACTION_MODES]
    action_mode = ActionMode[action_mode.upper()]
    print(f"Running {action_mode=}")

    output_filepath = f"{output_dir}/{action_mode.value}_09302030.json"
    outputs = []
    if pathlib.Path(output_filepath).exists():
        with open(output_filepath, "r") as f:
            outputs = [json.loads(line) for line in f.readlines()]

    fout = open(output_filepath, "a")

    correct, total = run_tools(action_mode, fout, outputs, M3toolSolver)
    fout.close()
    completion_tokens, prompt_tokens, price = get_price()
    return correct, total, price
