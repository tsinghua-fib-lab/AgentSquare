import os
import sys
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

from tenacity import (
    retry,
    stop_after_attempt, # type: ignore
    wait_random_exponential, # type: ignore
)

from typing import Optional, List
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

completion_tokens = prompt_tokens = 0
Model = Literal["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-instruct", "gpt-4o"]

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion(prompt: str, model: Model, temperature: float = 0.0, max_tokens: int = 500, stop_strs: Optional[List[str]] = None, n = 1) -> str:
    global completion_tokens, prompt_tokens
    response = client.completions.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        n=n,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=stop_strs,
    )
    completion_tokens += response.usage.completion_tokens
    prompt_tokens += response.usage.prompt_tokens
    if n > 1:
        responses = [choice.text.replace('>', '').strip() for choice in response.choices]
        return responses
    return response.choices[0].text.replace('>', '').strip()

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
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
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        stop=stop_strs,
        n=n,
        temperature=temperature,
    )
    completion_tokens += response.usage.completion_tokens
    prompt_tokens += response.usage.prompt_tokens
    if n > 1:
        responses = [choice.message.content.replace('>', '').strip() for choice in response.choices]
        return responses
    #print(response)
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

def get_price():
    global completion_tokens, prompt_tokens
    return completion_tokens, prompt_tokens, completion_tokens*60/1000000+prompt_tokens*30/1000000
