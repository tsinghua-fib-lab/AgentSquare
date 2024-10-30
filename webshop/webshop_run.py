import os
import sys 
import time
import requests
import argparse
from bs4 import BeautifulSoup
from bs4.element import Comment
from utils import get_price
from plan_prompt import plan_prompt
from workflow import workflow
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

    class WEBSHOP():
        def __init__(self, env, idx, solver, prompt, plan_prompt, to_print=True): 
            self.init_prompt = prompt
            self.prompt = ''
            self.idx = idx
            
            # if solver.planning is None:
            #     self.task_description = self.init_prompt + prompt
            # else:
            #     self.task_description = ob
            # self.prompt = prompt
            # self.ob = ob
            self.task_type = 'online_shopping'
            # self.reason_exp = reason_exp
            #self.init_prompt = init_prompt
            self.max_step_number = 15
            self.max_step_number_plan = 10
            self.last_action = ''
            self.memory_pool = []
            self.env = env
            self.reason_exp = plan_prompt
            self.prompt_cache = ''
            if solver.planning is None:
                self.step(['reset'])
            else:
                self.observation, _, _ = self.step(['reset'])
                self.task_description = self.observation.split("Instruction:")[1].split("[Search]")[0].strip()
            self.tool_instruction = ''
            self.feedback_previous_tools = ''
            
        
        def step(self, action):
            try:
                self.res= self.env.step(self.idx, action[0].strip())
                observation = self.res[0]
            except AssertionError:
                observation = 'Invalid action!'
            if action[0].startswith('think'):
                observation = 'OK.'
            if action[0] == 'reset':
                self.prompt += f'{observation}\n\nAction:'
            # elif action == 'reset' and self.solver.planning is not None:
            #     pass
            else:
                self.prompt += f' {action[0]}\nObservation: {observation}\n\nAction:'
                self.prompt = self.prompt[-14000:]
                
            self.task_description = self.init_prompt + self.prompt[-(18000-len(self.init_prompt)):]
            # if res[1] == 1:
            #     pass
            # else:
            #     res[1] = 0
            # 返回处理后的值
            self.observation = observation
            return observation, self.res[1], self.res[2]
        
        def prompt_reset(self):
            self.prompt_cache += self.prompt
            self.prompt = ''

        def prompt_exp_update(self, sub_task_id):
            self.prompt_exp = ''.join(self.reason_exp[0:(sub_task_id+1)])
            return self.prompt_exp

        def memory_update(self):
            return self.prompt + 'success'
        
        def memory_cache(self, sub_tasks, sub_task_id):
            self.memory_pool = [(self.init_prompt_cache + self.prompt[:self.prompt.rfind("Observation")] + 'success')]
            # self.memory_pool.append((self.ob.split(':')[0] + ': ' + self.last_action + '. ' + sub_tasks[sub_task_id]['reasoning instruction'] + '.\n>' + self.prompt)[:-1] + 'success.')
            # return self.memory_pool
        
        def init_prompt_update(self, sub_tasks, sub_task_id):
            if sub_task_id :
                self.init_prompt_cache = self.prompt_cache[:self.prompt_cache.rfind("Observation")] + f"Observation: {self.observation}\nReasoning instruction: {sub_tasks[sub_task_id]['reasoning instruction']}\n\nAction:"
            else:
                self.init_prompt_cache = f"{self.observation}\nReasoning instruction: {sub_tasks[sub_task_id]['reasoning instruction']}\n\nAction:"
            return self.init_prompt_cache
        
        def flag(self, action, sub_tasks, sub_task_id):
            if ('Page 1' in self.observation or '< Prev' in self.observation) and (sub_task_id != (len(sub_tasks) - 1)):
                return True
            else:
                return False
            
    # 使用封装的 CustomEnv
    webshop = WEBSHOP(env, idx, agent, prompt, plan_prompt, to_print=to_print)

    return workflow(agent, webshop)

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




from agent import AGENT
from module_map import ModuleMap
def run_webshop(planning=None, reasoning=None, tooluse=None, memory=None, llms_type=['gpt=3.5-turbo-instruct']):
    planning_module, reasoning_module, tooluse_module, memory_module = ModuleMap(planning, reasoning, tooluse, memory)
    WebshopSolver = AGENT("WebshopSolver", '', memory_module, reasoning_module, tooluse_module, planning_module, llms_type)
    res1 = run_episodes(prompt1, WebshopSolver, 500)
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
