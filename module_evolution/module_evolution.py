import argparse
import json
import os
import backoff
import openai

from prompt_reasoning import get_init_archive_reasoning, get_prompt_reasoning
from prompt_planning import get_init_archive_planning, get_prompt_planning
from prompt_memory import get_init_archive_memory, get_prompt_memory
from prompt_tooluse import get_init_archive_tooluse, get_prompt_tooluse
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

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


def search(args):
    archive_reasoning = get_init_archive_reasoning()
    archive_planning = get_init_archive_planning()
    archive_memory = get_init_archive_memory()
    archive_tooluse = get_init_archive_tooluse()
    system_prompt, prompt = get_prompt_reasoning(archive_reasoning)
    msg_list_reasoning = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    system_prompt, prompt = get_prompt_planning(archive_planning)
    msg_list_planning = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    system_prompt, prompt = get_prompt_memory(archive_memory)
    msg_list_memory = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    system_prompt, prompt = get_prompt_tooluse(archive_tooluse)
    msg_list_tooluse = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    try: 
        next_solution_reasoning = get_json_response_from_gpt_reflect(msg_list_reasoning, args.model)
        next_solution_planning = get_json_response_from_gpt_reflect(msg_list_planning, args.model)
        next_solution_memory = get_json_response_from_gpt_reflect(msg_list_memory, args.model)
        next_solution_tooluse = get_json_response_from_gpt_reflect(msg_list_tooluse, args.model)
        with open('output_reasoning.jsonl', 'a') as jsonl_file:
                jsonl_file.write(json.dumps(next_solution_reasoning) + '\n')
        for key, value in next_solution_reasoning.items():
            print(f"{key}: {value}")
        with open('output_planning.jsonl', 'a') as jsonl_file:
                jsonl_file.write(json.dumps(next_solution_planning) + '\n')
        for key, value in next_solution_planning.items():
            print(f"{key}: {value}")
        with open('output_memory.jsonl', 'a') as jsonl_file:
                jsonl_file.write(json.dumps(next_solution_memory) + '\n')
        for key, value in next_solution_memory.items():
            print(f"{key}: {value}")
        with open('output_tooluse.jsonl', 'a') as jsonl_file:
                jsonl_file.write(json.dumps(next_solution_tooluse) + '\n')
        for key, value in next_solution_tooluse.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print("During LLM generate new solution:")
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',type=str,default='gpt-4o')
    args = parser.parse_args()
    search(args)

