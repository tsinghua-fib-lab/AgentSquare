import os
import sys 
import time
import requests
import argparse
from bs4 import BeautifulSoup
from bs4.element import Comment
from utils import get_price
from plan_prompt import plan_prompt
WEBSHOP_URL = "http://101.6.69.111:3000"
ACTION_TO_TEMPLATE = {
    'Description': 'description_page.html',
    'Features': 'features_page.html',
    'Reviews': 'review_page.html',
    'Attributes': 'attributes_page.html',
}

def clean_str(p):
  return p.encode().decode("unicode-escape").encode("latin1").decode("utf-8")


def tag_visible(element):
    ignore = {'style', 'script', 'head', 'title', 'meta', '[document]'}
    return (
        element.parent.name not in ignore and not isinstance(element, Comment)
    )


def webshop_text(session, page_type, query_string='', page_num=1, asin='', options={}, subpage='', **kwargs):
    if page_type == 'init':
      url = (
          f'{WEBSHOP_URL}/{session}'
      )
    if page_type == 'search':
      url = (
          f'{WEBSHOP_URL}/search_results/{session}/'
          f'{query_string}/{page_num}'
      )
    elif page_type == 'item':
      url = (
          f'{WEBSHOP_URL}/item_page/{session}/'
          f'{asin}/{query_string}/{page_num}/{options}'
      )
    elif page_type == 'item_sub':
      url = (
          f'{WEBSHOP_URL}/item_sub_page/{session}/'
          f'{asin}/{query_string}/{page_num}/{subpage}/{options}'
      )
    elif page_type == 'end':
      url = (
          f'{WEBSHOP_URL}/done/{session}/'
          f'{asin}/{options}'
      )
    # print(url)
    html = requests.get(url).text
    html_obj = BeautifulSoup(html, 'html.parser')
    texts = html_obj.find_all(string=True)
    visible_texts = list(filter(tag_visible, texts))
    #print(visible_texts)
    #if page_type == 'search':
        #prin
    # visible_texts = [str(text).strip().strip('\\n') for text in visible_texts]
    # if page_type == 'end': import pdb; pdb.set_trace()
    if False:
        # For `simple` mode, return just [SEP] separators
        return ' [SEP] '.join(t.strip() for t in visible_texts if t != '\n')
    else:
        # Otherwise, return an observation with tags mapped to specific, unique separators
        observation = ''
        option_type = ''
        options = {}
        asins = []
        cnt = 0
        prod_cnt = 0
        just_prod = 0
        for t in visible_texts:
            if t == '\n': continue
            if t.replace('\n', '').replace('\\n', '').replace(' ', '') == '': continue
            # if t.startswith('Instruction:') and page_type != 'init': continue
            # print(t.parent.name, t)
            if t.parent.name == 'button':  # button
                processed_t = f'\n[{t}] '
            elif t.parent.name == 'label':  # options
                if f"'{t}'" in url:
                    processed_t = f'[[{t}]]'
                    # observation = f'You have clicked {t}.\n' + observation
                else:
                    processed_t = f'[{t}]'
                options[str(t)] = option_type
                # options[option_type] = options.get(option_type, []) + [str(t)]
            elif t.parent.get('class') == ["product-link"]: # product asins
                processed_t = f'\n[{t}] '
                if prod_cnt >= 3:
                  processed_t = ''
                prod_cnt += 1
                asins.append(str(t))
                just_prod = 0
            else: # regular, unclickable text
                processed_t =  '\n' + str(t) + ' '
                if cnt < 2 and page_type != 'init': processed_t = ''
                if just_prod <= 2 and prod_cnt >= 4: processed_t = ''
                option_type = str(t)
                cnt += 1
            just_prod += 1
            observation += processed_t
        info = {}
        if options:
          info['option_types'] = options
        if asins:
          info['asins'] = asins
        if 'Your score (min 0.0, max 1.0)' in visible_texts:
          idx = visible_texts.index('Your score (min 0.0, max 1.0)')
          info['reward'] = float(visible_texts[idx + 1])
          observation = 'Your score (min 0.0, max 1.0): ' + (visible_texts[idx + 1])
        return clean_str(observation), info

class webshopEnv:
  def __init__(self):
    self.sessions = {}
  
  def step(self, session, action):
    done = False
    observation_ = None
    
    if action == 'reset':
      self.sessions[session] = {'session': session, 'page_type': 'init'}
    elif action.startswith('think['):
      observation = 'OK.'
    elif action.startswith('search['):
      assert self.sessions[session]['page_type'] == 'init'
      query = action[7:-1]
      self.sessions[session] = {'session': session, 'page_type': 'search',
                                'query_string': query, 'page_num': 1}
    elif action.startswith('click['):
      button = action[6:-1]

      if button == 'Buy Now':
        assert self.sessions[session]['page_type'] == 'item'
        self.sessions[session]['page_type'] = 'end'
        done = True
      elif button == 'Back to Search':
        assert self.sessions[session]['page_type'] in ['search', 'item_sub', 'item']
        self.sessions[session] = {'session': session, 'page_type': 'init'}
      elif button == 'Next >':
        assert False # ad hoc page limitation
        assert self.sessions[session]['page_type'] == 'search'
        self.sessions[session]['page_num'] += 1
      elif button == '< Prev':
        assert self.sessions[session]['page_type'] in ['search', 'item_sub', 'item']
        if self.sessions[session]['page_type'] == 'search':
          assert False
          self.sessions[session]['page_num'] -= 1
        elif self.sessions[session]['page_type'] == 'item_sub':
          self.sessions[session]['page_type'] = 'item'
        elif self.sessions[session]['page_type'] == 'item':
          self.sessions[session]['page_type'] = 'search'
          self.sessions[session]['options'] = {}
      elif button in ACTION_TO_TEMPLATE:
        assert self.sessions[session]['page_type'] == 'item'
        self.sessions[session]['page_type'] = 'item_sub'
        self.sessions[session]['subpage'] = button
      else:
        if self.sessions[session]['page_type'] == 'search':
          assert button in self.sessions[session].get('asins', [])  # must be asins
          self.sessions[session]['page_type'] = 'item'
          self.sessions[session]['asin'] = button
        elif self.sessions[session]['page_type'] == 'item':
          assert 'option_types' in self.sessions[session]
          assert button in self.sessions[session]['option_types'], (button, self.sessions[session]['option_types'])  # must be options
          option_type = self.sessions[session]['option_types'][button]
          if not 'options' in self.sessions[session]:
            self.sessions[session]['options'] = {}
          self.sessions[session]['options'][option_type] = button
          observation_ = f'You have clicked {button}.'
    else:
      assert False
    observation, info = webshop_text(**self.sessions[session])
    if observation_:
      observation = observation_
    self.sessions[session].update(info)
    reward = info.get('reward', 0.0)
    return observation, reward, done
env = webshopEnv()

# trivial search & item, choose option
prompt1 = """Webshop 
Instruction:  
i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
[Search]  

Action: search[3 ounce bright citrus deodorant sensitive skin]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B078GWRC1J] 
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B078GTKVXY] 
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B08KBVJ4XN] 
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar & Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack) 
$15.95  

Action: think[B078GWRC1J and B078GTKVXY are bright citrus deodorant less then 50 dollars. I can check B078GWRC1J first.]
Observation: OK.

Action: click[B078GWRC1J]
Observation: 
[Back to Search] 
[< Prev] 
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
Price: $10.99 
Rating: N.A. 
[Description] 
[Features] 
[Reviews] 
[Buy Now]  

Action: think[For 3 ounce bottle of bright citrus deodorant for sensitive skin, the item has options 'bright citrus' and '3 ounce (pack of 1)' and seems good to buy.]
Observation: OK.

Action: click[bright citrus]
Observation: You have clicked bright citrus. 

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1). 

Action: click[Buy Now]
"""

def webshop_run(idx, prompt, agent, to_print=True):
  action = 'reset'
  init_prompt = prompt
  prompt = ''
  if agent.planning is None:
    for i in range(15):
      #time.sleep(0.5)
      try:
        res = env.step(idx, action)
        observation = res[0]
      except AssertionError:
        observation = 'Invalid action!'
  
      if action.startswith('think'):
        observation = 'OK.'

      if to_print:
        print(f'Action: {action}\nObservation: {observation}\n')
      
        sys.stdout.flush()
      if i:
        prompt += f' {action}\nObservation: {observation}\n\nAction:'
      else:
        prompt += f'{observation}\n\nAction:'
    
      if res[2]: 
        if res[1] == 1:
           if agent.memory is not None:
              agent.memory(prompt + 'success')
        return res[1]
      task_description = init_prompt + prompt[-(18000-len(init_prompt)):]
      action = agent.reasoning(task_description, '', '').strip()    
      #action = llm(init_prompt + prompt[-(6400-len(init_prompt)):], stop=['\n']).lstrip(' ').strip()
  else:
    res = env.step(idx, action)
    init_prompt = plan_prompt
    #print(idx, action)
    observation = res[0]
    task_description = observation.split("Instruction:")[1].split("[Search]")[0].strip()
    task_type = 'online shopping'
    sub_tasks = agent.planning(task_type, task_description, '')
    print(sub_tasks)
    for sub_task_id in range(len(sub_tasks)):
      init_prompt = ''.join(plan_prompt[0:(sub_task_id+1)])
      #print(init_prompt)
      for i in range(10):
        if sub_task_id and i == 0:
          prompt += f" {action}\nObservation: {observation}\nReasoning instruction: {sub_tasks[sub_task_id]['reasoning instruction']}\n\nAction:"
        elif i > 0:
           prompt += f" {action}\nObservation: {observation}\n\nAction:"
        else:
          prompt += f"{observation}\nReasoning instruction: {sub_tasks[sub_task_id]['reasoning instruction']}\n\nAction:"
        task_description = init_prompt + prompt[-(18000-len(init_prompt)):]
        action = agent.reasoning(task_description, '', '').strip()  
        try:
          res = env.step(idx, action)
          observation = res[0]
        except AssertionError:
          observation = 'Invalid action!'
    
        if action.startswith('think'):
          observation = 'OK.'

        if to_print:
          print(f'Action: {action}\nObservation: {observation}\n')
        
          sys.stdout.flush()
        if res[2]: 
          if res[1] == 1:
            if agent.memory is not None:
                prompt += f" {action}\n"
                agent.memory(prompt + 'success')
          return res[1]
        if ('Page 1' in observation or '< Prev' in observation) and (sub_task_id != (len(sub_tasks) - 1)):
           break
  return 0

def run_episodes(prompt, agent, n=50):
  rs = []
  cnt = 0
  for i in range(0, n):
    print('-----------------')
    print(i)
    try:
      r = webshop_run(f'fixed_{i}', prompt, agent, to_print=True)
    except AssertionError:
      r = 0
      cnt += 1
    rs.append(r)
    if (i+1) % 1 == 0:
      r, sr, fr = sum(rs) / len(rs), len([_ for _ in rs if _ == 1]) / len(rs), cnt / len(rs)
      print(i+1, r, sr, fr)
      completion_tokens, prompt_tokens, _ = get_price()
      print(f'completion_tokens:{completion_tokens}, prompt_tokens:{prompt_tokens}, price={completion_tokens*1.5/1000000+prompt_tokens*0.5/1000000}')
      print('-------------')
  r, sr, fr = sum(rs) / len(rs), len([_ for _ in rs if _ == 1]) / n, cnt / n
  print(r, sr, fr)
  return r




from AGENT import AGENT
from PLANNING_IO import PLANNING_IO
from PLANNING_HUGGINGGPT import PLANNING_HUGGINGGPT
from PLANNING_OPENAGI import PLANNING_OPENAGI
from PLANNING_VOYAGE import PLANNING_VOYAGE
from PLANNING_DEPS import PLANNING_DEPS
from REASONING_IO import REASONING_IO
from REASONING_COT import REASONING_COT
from REASONING_TOT import REASONING_TOT
from REASONING_DILU import REASONING_DILU
from REASONING_SELFREFINE import REASONING_SELFREFINE
from REASONING_COT_SC import REASONING_COT_SC
from REASONING_STEPBACK import REASONING_STEPBACK
from REASONING_HYBRID_TOT_SC_SELFREFINE import REASONING_HYBRID_TOT_SC_SELFREFINE
from MEMORY_DILU import MEMORY_DILU
from MEMORY_VOYAGE import MEMORY_VOYAGE
from MEMORY_TP import MEMORY_TP
from MEMORY_GENERATIVE import MEMORY_GENERATIVE
def run_webshop(planning=None, reasoning=None, tooluse=None, memory=None, llms_type=['gpt=3.5-turbo-instruct']):
    planning_map = {
        'io': PLANNING_IO,
        'hugginggpt': PLANNING_HUGGINGGPT,
        'openagi': PLANNING_OPENAGI,
        'voyage': PLANNING_VOYAGE,
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
        'htss': REASONING_HYBRID_TOT_SC_SELFREFINE,
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
    feedback = ''
    WebshopSolver = AGENT("WebshopSolver", '', memory_func, reasoning_func, tooluse_func, planning_func, llms_type)
    res1 = run_episodes(prompt1, WebshopSolver, 10)
    return res1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ALFWorld with specified modules.')
    parser.add_argument('--planning', type=str, default='none', help='Specify planning module')
    parser.add_argument('--reasoning', type=str, default='io', help='Specify reasoning module')
    parser.add_argument('--tooluse', type=str, default='none', help='tooluse is not required in ALFworld')
    parser.add_argument('--memory', type=str, default='none', help='Specify memory module')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0125', help='Specify the LLM model type')
    args = parser.parse_args()
    run_webshop(
        planning=args.planning,
        reasoning=args.reasoning,
        tooluse=args.tooluse,
        memory=args.memory,
        llms_type=[args.model]
    )
