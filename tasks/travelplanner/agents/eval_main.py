import re, string, os, sys
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "tools/planner")))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../tools/planner")))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import importlib
from typing import List, Dict, Any
import tiktoken
from pandas import DataFrame
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from prompts import zeroshot_react_agent_prompt
from utils.func import load_line_json_data, save_file
import sys
import json
import openai
import time
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from langchain_google_genai import ChatGoogleGenerativeAI
import argparse
from datasets import load_dataset
from datasets import load_from_disk
import os
import shutil

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']


pd.options.display.max_info_columns = 200

os.environ['TIKTOKEN_CACHE_DIR'] = './tmp'

actionMapping = {"FlightSearch":"flights","AttractionSearch":"attractions","GoogleDistanceMatrix":"googleDistanceMatrix","AccommodationSearch":"accommodation","RestaurantSearch":"restaurants","Planner":"planner","NotebookWrite":"notebook","CitySearch":"cities"}

class CityError(Exception):
    pass

class DateError(Exception):
    pass

def catch_openai_api_error():
    error = sys.exc_info()[0]
    if error == openai.error.APIConnectionError:
        print("APIConnectionError")
    elif error == openai.error.RateLimitError:
        print("RateLimitError")
        time.sleep(60)
    elif error == openai.error.APIError:
        print("APIError")
    elif error == openai.error.AuthenticationError:
        print("AuthenticationError")
    else:
        print("API error:", error)

class ReactAgent:
    def __init__(self,
                 args,
                 mode: str = 'zero_shot',
                 tools: List[str] = None,
                 max_steps: int = 30,
                 max_retries: int = 3,
                 illegal_early_stop_patience: int = 3,
                 react_llm_name = 'gpt-3.5-turbo-1106',
                 planner_llm_name = 'gpt-3.5-turbo-1106',
                #  logs_path = '../logs/',
                 city_file_path = '../database/background/citySet.txt',
                 travelplannerSolver = None

                 ) -> None: 
        

        self.answer = ''
        self.max_steps = max_steps
        self.mode = mode

        self.react_name = react_llm_name
        self.planner_name = planner_llm_name

        if self.mode == 'zero_shot':
            self.agent_prompt = zeroshot_react_agent_prompt

        self.json_log = []

        self.current_observation = ''
        self.current_data = None
        self.travelplannerSolver = travelplannerSolver

        if 'gpt-3.5' in react_llm_name:
            stop_list = ['\n']
            self.max_token_length = 15000
            self.llm = ChatOpenAI(temperature=1,
                     max_tokens=256,
                     model_name=react_llm_name,
                     openai_api_key=OPENAI_API_KEY,
                     model_kwargs={"stop": stop_list})
            
        elif 'gpt-4' in react_llm_name:
            stop_list = ['\n']
            self.max_token_length = 30000
            self.llm = ChatOpenAI(temperature=0,
                     max_tokens=256,
                     model_name=react_llm_name,
                     openai_api_key=OPENAI_API_KEY,
                     model_kwargs={"stop": stop_list})
            
        elif react_llm_name in ['mistral-7B-32K']:
            stop_list = ['\n']
            self.max_token_length = 30000
            self.llm = ChatOpenAI(temperature=0,
                     max_tokens=256,
                     openai_api_key="EMPTY", 
                     openai_api_base="http://localhost:8301/v1", 
                     model_name="gpt-3.5-turbo",
                     model_kwargs={"stop": stop_list})
            
        elif react_llm_name in ['mixtral']:
            stop_list = ['\n']
            self.max_token_length = 30000
            self.llm = ChatOpenAI(temperature=0,
                     max_tokens=256,
                     openai_api_key="EMPTY", 
                     openai_api_base="http://localhost:8501/v1", 
                     model_name="gpt-3.5-turbo",
                     model_kwargs={"stop": stop_list})
            
        elif react_llm_name in ['ChatGLM3-6B-32K']:
            stop_list = ['\n']
            self.max_token_length = 30000
            self.llm = ChatOpenAI(
                     temperature=0,
                     max_tokens=256,
                     openai_api_key="EMPTY", 
                     openai_api_base="http://localhost:8501/v1", 
                     model_name="gpt-3.5-turbo",
                     model_kwargs={"stop": stop_list})
        
        elif react_llm_name in ['gemini']:
            self.llm = ChatGoogleGenerativeAI(temperature=0,model="gemini-pro",google_api_key=GOOGLE_API_KEY)
            self.max_token_length = 30000


        self.illegal_early_stop_patience = illegal_early_stop_patience

        self.tools = self.load_tools(tools, planner_model_name=planner_llm_name,travelplannerSolver=self.travelplannerSolver)
        self.max_retries = max_retries
        self.retry_record = {key: 0 for key in self.tools}
        self.retry_record['invalidAction'] = 0

        # print(self.retry_record)

        self.last_actions = []

        # self.log_path = logs_path + datetime.now().strftime('%Y%m%d%H%M%S') + '.out'
        # self.log_file = open(self.log_path, 'a+')

        # print("logs will be stored in " + self.log_path)

        self.city_set = self.load_city(city_set_path=city_file_path)

        self.enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

        self.__reset_agent()

    def run(self, query, reset=True) -> None:

        self.query = query
        
        if reset:
            self.__reset_agent()

        while not self.is_halted() and not self.is_finished():
            self.step()

        return self.answer, self.scratchpad, self.json_log

    def step(self) -> None:

        if self.travelplannerSolver.planning == None:
            self.json_log.append({"step": self.step_n, "thought":"",
                                      "action": "", "observation": "", "state":""})
            self.scratchpad += f'\nThought {self.step_n}:'
            # self.scratchpad += ' ' + self.prompt_agent()
            thought = self.travelplannerSolver.reasoning(self._build_agent_prompt(), '', '')
            self.scratchpad += ' ' + thought

            print(self.scratchpad.split('\n')[-1])
            self.json_log[-1]['thought'] = self.scratchpad.split('\n')[-1].replace(f'\nThought {self.step_n}:',"")
            # self.log_file.write(self.scratchpad.split('\n')[-1] + '\n')


            # Act
            self.scratchpad += f'\nAction {self.step_n}:'
            action = normalize_action_string(self.travelplannerSolver.tooluse(self.query + '\nThe current task is: ' + thought,'',''))

            if action == None or action == '' or action == '\n':
                self.scratchpad += " Your action is filtered due to content. Please make sure your action does not start with ['\\n', 'Thought', 'Action', 'Observation'] and assume all the actions are permitted in this environment and take the action again."
            else:
                self.scratchpad += ' ' + action


            if len(self.last_actions) > 0 and self.last_actions[-1] != action:
                self.last_actions.clear()

            # refresh last_action list
            self.last_actions.append(action)

            self.json_log[-1]['action'] = self.scratchpad.split('\n')[-1].replace(f'\nAction {self.step_n}:',"")


            # examine if the same action has been repeated 3 times consecutively
            if len(self.last_actions) == 3:
                print("The same action has been repeated 3 times consecutively. So we stop here.")
                # self.log_file.write("The same action has been repeated 3 times consecutively. So we stop here.")
                self.json_log[-1]['state'] = 'same action 3 times repeated'
                self.finished = True
                return


            # action_type, action_arg = parse_action(action)
            print(self.scratchpad.split('\n')[-1])
            # self.log_file.write(self.scratchpad.split('\n')[-1]+'\n')

            # Observe
            self.scratchpad += f'\nObservation {self.step_n}: '

            if action == None or action == '' or action == '\n':
                action_type = None 
                action_arg = None
                self.scratchpad += "No feedback from the environment due to the null action. Please make sure your action does not start with [Thought, Action, Observation]."
            
            else:
                action_type, action_arg = parse_action(action)
                
                if action_type != "Planner":
                    if action_type in actionMapping:
                        pending_action = actionMapping[action_type]
                    elif action_type not in actionMapping:
                        pending_action = 'invalidAction'
                    
                    if pending_action in self.retry_record:
                        if self.retry_record[pending_action] + 1 > self.max_retries:
                            action_type = 'Planner'
                            print(f"{pending_action} early stop due to {self.max_retries} max retries.")
                            # self.log_file.write(f"{pending_action} early stop due to {self.max_retries} max retries.")
                            self.json_log[-1]['state'] = f"{pending_action} early stop due to {self.max_retries} max retries."
                            self.finished = True
                            return
                        
                    elif pending_action not in self.retry_record:
                        if self.retry_record['invalidAction'] + 1 > self.max_retries:
                            action_type = 'Planner'
                            print(f"invalidAction Early stop due to {self.max_retries} max retries.")
                            # self.log_file.write(f"invalidAction early stop due to {self.max_retries} max retries.")
                            self.json_log[-1]['state'] = f"invalidAction early stop due to {self.max_retries} max retries."
                            self.finished = True
                            return

                if action_type == 'FlightSearch':
                    try:
                        if validate_date_format(action_arg.split(', ')[2]) and validate_city_format(action_arg.split(', ')[0],self.city_set ) and validate_city_format(action_arg.split(', ')[1],self.city_set):
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            self.current_data = self.tools['flights'].run(action_arg.split(', ')[0], action_arg.split(', ')[1], action_arg.split(', ')[2])
                            self.current_observation = str(to_string(self.current_data))
                            self.scratchpad += self.current_observation 
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'

                    except DateError:
                        self.retry_record['flights'] += 1
                        self.current_observation = f"'{action_arg.split(', ')[2]}' is not in the format YYYY-MM-DD"
                        self.scratchpad += f"'{action_arg.split(', ')[2]}' is not in the format YYYY-MM-DD"
                        self.json_log[-1]['state'] = f'Illegal args. DateError'

                    except ValueError as e:
                        self.retry_record['flights'] += 1
                        self.current_observation = str(e)
                        self.scratchpad += str(e)
                        self.json_log[-1]['state'] = f'Illegal args. City Error'

                    except Exception as e:
                        print(e)
                        self.retry_record['flights'] += 1
                        self.current_observation = f'Illegal Flight Search. Please try again.'
                        self.scratchpad += f'Illegal Flight Search. Please try again.'
                        self.json_log[-1]['state'] = f'Illegal args. Other Error'

                elif action_type == 'AttractionSearch':

                    try:
                        if validate_city_format(action_arg, self.city_set):
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip().strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            self.current_data = self.tools['attractions'].run(action_arg)
                            self.current_observation = to_string(self.current_data).strip('\n').strip()
                            self.scratchpad += self.current_observation
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'
                    except ValueError as e:
                        self.retry_record['attractions'] += 1
                        self.current_observation = str(e)
                        self.scratchpad += str(e)
                        self.json_log[-1]['state'] = f'Illegal args. City Error'
                    except Exception as e:
                        print(e)
                        self.retry_record['attractions'] += 1
                        self.current_observation = f'Illegal Attraction Search. Please try again.'
                        self.scratchpad += f'Illegal Attraction Search. Please try again.'
                        self.json_log[-1]['state'] = f'Illegal args. Other Error'

                elif action_type == 'AccommodationSearch':

                    try:
                        if validate_city_format(action_arg, self.city_set):
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip().strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            self.current_data = self.tools['accommodations'].run(action_arg)
                            self.current_observation = to_string(self.current_data).strip('\n').strip()
                            self.scratchpad += self.current_observation
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'
                    except ValueError as e :
                        self.retry_record['accommodations'] += 1
                        self.current_observation = str(e)
                        self.scratchpad += str(e)
                        self.json_log[-1]['state'] = f'Illegal args. City Error'
                    except Exception as e:
                        print(e)
                        self.retry_record['accommodations'] += 1
                        self.current_observation = f'Illegal Accommodation Search. Please try again.'
                        self.scratchpad += f'Illegal Accommodation Search. Please try again.'
                        self.json_log[-1]['state'] = f'Illegal args. Other Error'

                elif action_type == 'RestaurantSearch':

                    try:
                        if validate_city_format(action_arg, self.city_set):
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip().strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            self.current_data = self.tools['restaurants'].run(action_arg)
                            self.current_observation = to_string(self.current_data).strip()
                            self.scratchpad += self.current_observation
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'

                    except ValueError as e:
                        self.retry_record['restaurants'] += 1
                        self.current_observation = str(e)
                        self.scratchpad += str(e)
                        self.json_log[-1]['state'] = f'Illegal args. City Error'

                    except Exception as e:
                        print(e)
                        self.retry_record['restaurants'] += 1
                        self.current_observation = f'Illegal Restaurant Search. Please try again.'
                        self.scratchpad += f'Illegal Restaurant Search. Please try again.'
                        self.json_log = f'Illegal args. Other Error'
                        
                elif action_type == "CitySearch":
                    try:
                        self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                        # self.current_data = self.tools['cities'].run(action_arg)
                        self.current_observation = to_string(self.tools['cities'].run(action_arg)).strip()
                        self.scratchpad += self.current_observation
                        self.__reset_record()
                        self.json_log[-1]['state'] = f'Successful'

                    except ValueError as e:
                        self.retry_record['cities'] += 1
                        self.current_observation = str(e)
                        self.scratchpad += str(e)
                        self.json_log[-1]['state'] = f'Illegal args. State Error'

                    except Exception as e:
                        print(e)
                        self.retry_record['cities'] += 1
                        self.current_observation = f'Illegal City Search. Please try again.'
                        self.scratchpad += f'Illegal City Search. Please try again.'
                        self.json_log = f'Illegal args. Other Error'


                elif action_type == 'GoogleDistanceMatrix':

                    try:
                        self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                        self.current_data = self.tools['googleDistanceMatrix'].run(action_arg.split(', ')[0],action_arg.split(', ')[1],action_arg.split(', ')[2])
                        self.current_observation =  to_string(self.current_data)
                        self.scratchpad += self.current_observation 
                        self.__reset_record()
                        self.json_log[-1]['state'] = f'Successful'

                    except Exception as e:
                        print(e)
                        self.retry_record['googleDistanceMatrix'] += 1
                        self.current_observation = f'Illegal GoogleDistanceMatrix. Please try again.'
                        self.scratchpad += f'Illegal GoogleDistanceMatrix. Please try again.'
                        self.json_log[-1]['state'] = f'Illegal args. Other Error'
                
                
                elif action_type == 'NotebookWrite':
                    try:
                        self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                        self.current_observation = str(self.tools['notebook'].write(self.current_data, action_arg))
                        self.scratchpad  +=  self.current_observation
                        self.__reset_record()
                        self.json_log[-1]['state'] = f'Successful'

                    except Exception as e:
                        print(e)
                        self.retry_record['notebook'] += 1
                        self.current_observation = f'{e}'
                        self.scratchpad += f'{e}'
                        self.json_log[-1]['state'] = f'Illegal args. Other Error'
                

                elif action_type == "Planner":
                    # try:

                        self.current_observation = str(self.tools['planner'].run(str(self.tools['notebook'].list_all()),action_arg))
                        self.scratchpad  +=  self.current_observation
                        self.answer = self.current_observation
                        self.__reset_record()
                        self.json_log[-1]['state'] = f'Successful'

                else:
                    self.retry_record['invalidAction'] += 1
                    self.current_observation = 'Invalid Action. Valid Actions are  FlightSearch[Departure City, Destination City, Date] / ' \
                                    'AccommodationSearch[City] /  RestaurantSearch[City] / NotebookWrite[Short Description] / AttractionSearch[City] / CitySearch[State] / GoogleDistanceMatrix[Origin, Destination, Mode] and Planner[Query].'
                    self.scratchpad += self.current_observation
                    self.json_log[-1]['state'] = f'invalidAction'

            if action == None or action == '' or action == '\n':
                print(f'Observation {self.step_n}: ' + "No feedback from the environment due to the null action.")
                # write(f'Observation {self.step_n}: ' + "Your action is filtered due to content. Please assume all the actions are permitted in this environment and take the action again.")
                self.json_log[-1]['observation'] = "No feedback from the environment due to the null action."
            else:
                print(f'Observation {self.step_n}: ' + self.current_observation+'\n')
                # rite(f'Observation {self.step_n}: ' + self.current_observation+'\n')
                self.json_log[-1]['observation'] = self.current_observation

            self.step_n += 1

            # 

            if action_type and action_type == 'Planner' and self.retry_record['planner']==0:
                
                self.finished = True
                self.answer = self.current_observation
                self.step_n += 1
                return
            
        else:
            sub_tasks = self.travelplannerSolver.planning(task_type='Travel planning', task_description=self._build_agent_prompt(), feedback='')
            print("-"*50 + 'Subtasks are below' + '-'*47)
            print("There are "+str(len(sub_tasks))+" sub_tasks")
            print(sub_tasks)
            for sub_task_id in range(len(sub_tasks)):
                self.json_log.append({"step": self.step_n, "thought":"",
                                      "action": "", "observation": "", "state":""})
                self.scratchpad += '\n' + f'Subtask {sub_task_id + 1}:' + sub_tasks[sub_task_id]['description']
                print("-"*50 + "The current sub_task is" + "-"*47)
                print(self.scratchpad.split('\n')[-1])
                self.scratchpad += f'\nThought {self.step_n}:' 
                # self.scratchpad += ' ' + self.prompt_agent()
                thought = self.travelplannerSolver.reasoning(self._build_agent_prompt(), '', '')
                self.scratchpad += ' ' + thought
                print("-"*100)
                print(self.scratchpad.split('\n')[-1])
                print("-"*100)
                self.json_log[-1]['thought'] = self.scratchpad.split('\n')[-1].replace(f'\nThought {self.step_n}:',"")
                # self.log_file.write(self.scratchpad.split('\n')[-1] + '\n')

                # Act
                self.scratchpad += f'\nAction {self.step_n}:'
                action = normalize_action_string(self.travelplannerSolver.tooluse(self.query + '\nThe current task is: ' + thought, sub_tasks[sub_task_id]['tool use instruction'],''))
                # action = self.prompt_agent()

                if action == None or action == '' or action == '\n':
                    self.scratchpad += " Your action is filtered due to content. Please make sure your action does not start with ['\\n', 'Thought', 'Action', 'Observation'] and assume all the actions are permitted in this environment and take the action again."
                else:
                    self.scratchpad += ' ' + action


                if len(self.last_actions) > 0 and self.last_actions[-1] != action:
                    self.last_actions.clear()

                # refresh last_action list
                self.last_actions.append(action)

                self.json_log[-1]['action'] = self.scratchpad.split('\n')[-1].replace(f'\nAction {self.step_n}:',"")


                # examine if the same action has been repeated 3 times consecutively
                if len(self.last_actions) == 3:
                    print("The same action has been repeated 3 times consecutively. So we stop here.")
                    # self.log_file.write("The same action has been repeated 3 times consecutively. So we stop here.")
                    self.json_log[-1]['state'] = 'same action 3 times repeated'
                    self.finished = True
                    return


                # action_type, action_arg = parse_action(action)
                print("-"*100)
                print(self.scratchpad.split('\n')[-1])
                print("-"*100)
                # self.log_file.write(self.scratchpad.split('\n')[-1]+'\n')

                # Observe
                self.scratchpad += f'\nObservation {self.step_n}: '

                if action == None or action == '' or action == '\n':
                    action_type = None 
                    action_arg = None
                    self.scratchpad += "No feedback from the environment due to the null action. Please make sure your action does not start with [Thought, Action, Observation]."
                
                else:
                    action_type, action_arg = parse_action(action)
                    
                    if action_type != "Planner":
                        if action_type in actionMapping:
                            pending_action = actionMapping[action_type]
                        elif action_type not in actionMapping:
                            pending_action = 'invalidAction'
                        
                        if pending_action in self.retry_record:
                            if self.retry_record[pending_action] + 1 > self.max_retries:
                                action_type = 'Planner'
                                print(f"{pending_action} early stop due to {self.max_retries} max retries.")
                                # self.log_file.write(f"{pending_action} early stop due to {self.max_retries} max retries.")
                                self.json_log[-1]['state'] = f"{pending_action} early stop due to {self.max_retries} max retries."
                                self.finished = True
                                return
                            
                        elif pending_action not in self.retry_record:
                            if self.retry_record['invalidAction'] + 1 > self.max_retries:
                                action_type = 'Planner'
                                print(f"invalidAction Early stop due to {self.max_retries} max retries.")
                                # self.log_file.write(f"invalidAction early stop due to {self.max_retries} max retries.")
                                self.json_log[-1]['state'] = f"invalidAction early stop due to {self.max_retries} max retries."
                                self.finished = True
                                return

                    if action_type == 'FlightSearch':
                        try:
                            if validate_date_format(action_arg.split(', ')[2]) and validate_city_format(action_arg.split(', ')[0],self.city_set ) and validate_city_format(action_arg.split(', ')[1],self.city_set):
                                self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                                self.current_data = self.tools['flights'].run(action_arg.split(', ')[0], action_arg.split(', ')[1], action_arg.split(', ')[2])
                                self.current_observation = str(to_string(self.current_data))
                                self.scratchpad += self.current_observation 
                                self.__reset_record()
                                self.json_log[-1]['state'] = f'Successful'

                        except DateError:
                            self.retry_record['flights'] += 1
                            self.current_observation = f"'{action_arg.split(', ')[2]}' is not in the format YYYY-MM-DD"
                            self.scratchpad += f"'{action_arg.split(', ')[2]}' is not in the format YYYY-MM-DD"
                            self.json_log[-1]['state'] = f'Illegal args. DateError'

                        except ValueError as e:
                            self.retry_record['flights'] += 1
                            self.current_observation = str(e)
                            self.scratchpad += str(e)
                            self.json_log[-1]['state'] = f'Illegal args. City Error'

                        except Exception as e:
                            print(e)
                            self.retry_record['flights'] += 1
                            self.current_observation = f'Illegal Flight Search. Please try again.'
                            self.scratchpad += f'Illegal Flight Search. Please try again.'
                            self.json_log[-1]['state'] = f'Illegal args. Other Error'

                    elif action_type == 'AttractionSearch':

                        try:
                            if validate_city_format(action_arg, self.city_set):
                                self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip().strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                                self.current_data = self.tools['attractions'].run(action_arg)
                                self.current_observation = to_string(self.current_data).strip('\n').strip()
                                self.scratchpad += self.current_observation
                                self.__reset_record()
                                self.json_log[-1]['state'] = f'Successful'
                        except ValueError as e:
                            self.retry_record['attractions'] += 1
                            self.current_observation = str(e)
                            self.scratchpad += str(e)
                            self.json_log[-1]['state'] = f'Illegal args. City Error'
                        except Exception as e:
                            print(e)
                            self.retry_record['attractions'] += 1
                            self.current_observation = f'Illegal Attraction Search. Please try again.'
                            self.scratchpad += f'Illegal Attraction Search. Please try again.'
                            self.json_log[-1]['state'] = f'Illegal args. Other Error'

                    elif action_type == 'AccommodationSearch':

                        try:
                            if validate_city_format(action_arg, self.city_set):
                                self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip().strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                                self.current_data = self.tools['accommodations'].run(action_arg)
                                self.current_observation = to_string(self.current_data).strip('\n').strip()
                                self.scratchpad += self.current_observation
                                self.__reset_record()
                                self.json_log[-1]['state'] = f'Successful'
                        except ValueError as e :
                            self.retry_record['accommodations'] += 1
                            self.current_observation = str(e)
                            self.scratchpad += str(e)
                            self.json_log[-1]['state'] = f'Illegal args. City Error'
                        except Exception as e:
                            print(e)
                            self.retry_record['accommodations'] += 1
                            self.current_observation = f'Illegal Accommodation Search. Please try again.'
                            self.scratchpad += f'Illegal Accommodation Search. Please try again.'
                            self.json_log[-1]['state'] = f'Illegal args. Other Error'

                    elif action_type == 'RestaurantSearch':

                        try:
                            if validate_city_format(action_arg, self.city_set):
                                self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip().strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                                self.current_data = self.tools['restaurants'].run(action_arg)
                                self.current_observation = to_string(self.current_data).strip()
                                self.scratchpad += self.current_observation
                                self.__reset_record()
                                self.json_log[-1]['state'] = f'Successful'

                        except ValueError as e:
                            self.retry_record['restaurants'] += 1
                            self.current_observation = str(e)
                            self.scratchpad += str(e)
                            self.json_log[-1]['state'] = f'Illegal args. City Error'

                        except Exception as e:
                            print(e)
                            self.retry_record['restaurants'] += 1
                            self.current_observation = f'Illegal Restaurant Search. Please try again.'
                            self.scratchpad += f'Illegal Restaurant Search. Please try again.'
                            self.json_log = f'Illegal args. Other Error'
                            
                    elif action_type == "CitySearch":
                        try:
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            # self.current_data = self.tools['cities'].run(action_arg)
                            self.current_observation = to_string(self.tools['cities'].run(action_arg)).strip()
                            self.scratchpad += self.current_observation
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'

                        except ValueError as e:
                            self.retry_record['cities'] += 1
                            self.current_observation = str(e)
                            self.scratchpad += str(e)
                            self.json_log[-1]['state'] = f'Illegal args. State Error'

                        except Exception as e:
                            print(e)
                            self.retry_record['cities'] += 1
                            self.current_observation = f'Illegal City Search. Please try again.'
                            self.scratchpad += f'Illegal City Search. Please try again.'
                            self.json_log = f'Illegal args. Other Error'


                    elif action_type == 'GoogleDistanceMatrix':

                        try:
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            self.current_data = self.tools['googleDistanceMatrix'].run(action_arg.split(', ')[0],action_arg.split(', ')[1],action_arg.split(', ')[2])
                            self.current_observation =  to_string(self.current_data)
                            self.scratchpad += self.current_observation 
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'

                        except Exception as e:
                            print(e)
                            self.retry_record['googleDistanceMatrix'] += 1
                            self.current_observation = f'Illegal GoogleDistanceMatrix. Please try again.'
                            self.scratchpad += f'Illegal GoogleDistanceMatrix. Please try again.'
                            self.json_log[-1]['state'] = f'Illegal args. Other Error'
                    
                    
                    elif action_type == 'NotebookWrite':
                        try:
                            self.scratchpad = self.scratchpad.replace(to_string(self.current_data).strip(),'Masked due to limited length. Make sure the data has been written in Notebook.')
                            self.current_observation = str(self.tools['notebook'].write(self.current_data, action_arg))
                            self.scratchpad  +=  self.current_observation
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'

                        except Exception as e:
                            print(e)
                            self.retry_record['notebook'] += 1
                            self.current_observation = f'{e}'
                            self.scratchpad += f'{e}'
                            self.json_log[-1]['state'] = f'Illegal args. Other Error'
                    

                    elif action_type == "Planner":
                        # try:

                            self.current_observation = str(self.tools['planner'].run(str(self.tools['notebook'].list_all()),action_arg))
                            self.scratchpad  +=  self.current_observation
                            self.answer = self.current_observation
                            self.__reset_record()
                            self.json_log[-1]['state'] = f'Successful'

                    else:
                        self.retry_record['invalidAction'] += 1
                        self.current_observation = 'Invalid Action. Valid Actions are  FlightSearch[Departure City, Destination City, Date] / ' \
                                        'AccommodationSearch[City] /  RestaurantSearch[City] / NotebookWrite[Short Description] / AttractionSearch[City] / CitySearch[State] / GoogleDistanceMatrix[Origin, Destination, Mode] and Planner[Query].'
                        self.scratchpad += self.current_observation
                        self.json_log[-1]['state'] = f'invalidAction'

                if action == None or action == '' or action == '\n':
                    print(f'Observation {self.step_n}: ' + "No feedback from the environment due to the null action.")
                    # write(f'Observation {self.step_n}: ' + "Your action is filtered due to content. Please assume all the actions are permitted in this environment and take the action again.")
                    self.json_log[-1]['observation'] = "No feedback from the environment due to the null action."
                else:
                    print(f'Observation {self.step_n}: ' + self.current_observation+'\n')
                    # rite(f'Observation {self.step_n}: ' + self.current_observation+'\n')
                    self.json_log[-1]['observation'] = self.current_observation

                self.step_n += 1
                
                if action_type and action_type == 'Planner' and self.retry_record['planner']==0:
                    
                    self.finished = True
                    self.answer = self.current_observation
                    self.step_n += 1
                    return
                
                if sub_task_id + 1 == len(sub_tasks) and action_type != "Planner":
                    self.current_observation = str(self.tools['planner'].run(str(self.tools['notebook'].list_all()),action_arg))
                    self.answer = self.current_observation
                    self.finished = True


                    

# 通过query和scratchpad得到request
    def prompt_agent(self) -> str:
        while True:
            try:
                # print(self._build_agent_prompt())
                if self.react_name == 'gemini':
                    request = format_step(self.llm.invoke(self._build_agent_prompt(),stop=['\n']).content)
                else:
                    request = format_step(self.llm([HumanMessage(content=self._build_agent_prompt())]).content)
                # print(request)
                return request
            except:
                catch_openai_api_error()
                print(self._build_agent_prompt())
                print(len(self.enc.encode(self._build_agent_prompt())))
                time.sleep(5)

    def _build_agent_prompt(self) -> str:
        if self.mode == "zero_shot":
            return self.agent_prompt.format(
                query=self.query,
                scratchpad=self.scratchpad)

    def is_finished(self) -> bool:
        return self.finished

    def is_halted(self) -> bool:
        return ((self.step_n > self.max_steps) or (
                    len(self.enc.encode(self._build_agent_prompt())) > self.max_token_length)) and not self.finished

# 将变量初始化
    def __reset_agent(self) -> None:
        self.step_n = 1
        self.finished = False
        self.answer = ''
        self.scratchpad: str = ''
        self.__reset_record()
        self.json_log = []
        self.current_observation = ''
        self.current_data = None
        self.last_actions = []

        if 'notebook' in self.tools:
            self.tools['notebook'].reset()
    
    def __reset_record(self) -> None:
        self.retry_record = {key: 0 for key in self.retry_record}
        self.retry_record['invalidAction'] = 0


    def load_tools(self, tools: List[str], planner_model_name=None,travelplannerSolver = None) -> Dict[str, Any]:
        tools_map = {}
        for tool_name in tools:
            module = importlib.import_module("tools.{}.apis".format(tool_name))
            
            # Avoid instantiating the planner tool twice 
            if tool_name == 'planner' and planner_model_name is not None:
                tools_map[tool_name] = getattr(module, tool_name[0].upper()+tool_name[1:])(model_name=planner_model_name,travelplannerSolver=travelplannerSolver)
            else:
                tools_map[tool_name] = getattr(module, tool_name[0].upper()+tool_name[1:])()
        return tools_map

    def load_city(self, city_set_path: str) -> List[str]:
        city_set = []
        lines = open(city_set_path, 'r').read().strip().split('\n')
        for unit in lines:
            city_set.append(unit)
        return city_set

### String Stuff ###
gpt2_enc = tiktoken.encoding_for_model("text-davinci-003")


def parse_action(string):
    string = string.strip()  # 去掉前后的空格
    pattern = r'^(\w+)\[(.+)\]$'
    match = re.match(pattern, string)

    try:
        if match:
            action_type = match.group(1)
            action_arg = match.group(2)
            return action_type, action_arg
        else:
            return None, None
        
    except:
        return None, None

# 去除文本中多余的换行符和前后空白
def format_step(step: str) -> str:
    return step.strip('\n').strip().replace('\n', '')



def truncate_scratchpad(scratchpad: str, n_tokens: int = 1600, tokenizer=gpt2_enc) -> str:
    lines = scratchpad.split('\n')
    observations = filter(lambda x: x.startswith('Observation'), lines)
    observations_by_tokens = sorted(observations, key=lambda x: len(tokenizer.encode(x)))
    while len(gpt2_enc.encode('\n'.join(lines))) > n_tokens:
        largest_observation = observations_by_tokens.pop(-1)
        ind = lines.index(largest_observation)
        lines[ind] = largest_observation.split(':')[0] + ': [truncated wikipedia excerpt]'
    return '\n'.join(lines)


def normalize_answer(s):
    def remove_articles(text):
        return re.sub(r"\b(a|an|the|usd)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def EM(answer, key) -> bool:
    return normalize_answer(str(answer)) == normalize_answer(str(key))


def remove_observation_lines(text, step_n):
    pattern = re.compile(rf'^Observation {step_n}.*', re.MULTILINE)
    return pattern.sub('', text)

def validate_date_format(date_str: str) -> bool:
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    
    if not re.match(pattern, date_str):
        raise DateError
    return True

def validate_city_format(city_str: str, city_set: list) -> bool:
    if city_str not in city_set:
        raise ValueError(f"{city_str} is not valid city in {str(city_set)}.")
    return True

def parse_args_string(s: str) -> dict:
    # Split the string by commas
    segments = s.split(",")
    
    # Initialize an empty dictionary to store the results
    result = {}
    
    for segment in segments:
        # Check for various operators
        if "contains" in segment:
            if "~contains" in segment:
                key, value = segment.split("~contains")
                operator = "~contains"
            else:
                key, value = segment.split("contains")
                operator = "contains"
        elif "<=" in segment:
            key, value = segment.split("<=")
            operator = "<="
        elif ">=" in segment:
            key, value = segment.split(">=")
            operator = ">="
        elif "=" in segment:
            key, value = segment.split("=")
            operator = "="
        else:
            continue  # If no recognized operator is found, skip to the next segment
                
        # Strip spaces and single quotes
        key = key.strip()
        value = value.strip().strip("'")
        
        # Store the result with the operator included
        result[key] = (operator, value)
        
    return result

def to_string(data) -> str:
    if data is not None:
        if type(data) == DataFrame:
            return data.to_string(index=False)
        else:
            return str(data)
    else:
        return str(None)

def normalize_action_string(input_string: str) -> str:
    # 定义正则表达式模式，匹配 action_type 和 action_arg
    pattern = r"(?i)(action\s*\d*:|action\s*:)?\s*([a-zA-Z]+)\[([^\]]+)\]"
    
    # 使用正则表达式提取 action_type 和 action_arg
    match = re.search(pattern, input_string.strip())
    if match:
        action_type = match.group(2)  # 获取第二个匹配组（即 action_type）
        action_arg = match.group(3)   # 获取第三个匹配组（即 action_arg）
        # 返回格式化后的字符串
        return f"{action_type}[{action_arg}]"
    return input_string  # 如果不匹配，返回原始字符串

def find_missing_files(directory, total_files = 30):
    # 存储缺失的文件序号
    missing_files = []
    
    # 遍历所有可能的文件序号
    for i in range(151,181):
        # 构建文件名
        file_name = f"generated_plan_{i}.json"
        # 检查文件是否存在
        if not os.path.exists(os.path.join(directory, file_name)):
            missing_files.append(i)
    print(f"总共缺失{len(missing_files)}个文件\n"+f"缺失的文件序号: {missing_files}")
    return missing_files

import numpy as np
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import torch.optim as optim
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


from utils_llm import get_chat, get_completion, get_price, llm_response
from AGENT import AGENT
from planning_modules import *
from reasoning_modules import *
from tooluse_modules import *
from memory_modules import *

def agent_build(planning=None, reasoning=None, tooluse=None, memory=None, llms_type=['gpt=3.5-turbo-instruct']):
    planning_map = {
        'io': PLANNING_IO,
        'none': None,
        'deps': PLANNING_DEPS,
        'hugginggpt': PLANNING_HUGGINGGPT,
        'openagi': PLANNING_OPENAGI,
        'voyage': PLANNING_VOYAGE,
    }
    reasoning_map = {
        'cot': REASONING_COT,
        'none': None,
        'io': REASONING_IO,
        'tot': REASONING_TOT,
        'self-refine': REASONING_SELFREFINE,
        'cot_sc': REASONING_COT_SC,
        'dilu': REASONING_DILU,
        'stepback': REASONING_STEPBACK,
    }
    tooluse_map = {
        'none': None,
        'io': TOOLUSE_IO,
        'anytool': TOOLUSE_ANYTOOL,
        'toolbench': TOOLUSE_TOOLBENCH,
        'toolformer':TOOLUSE_TOOLFORMER,
    }
    memory_map = {
        'none': None,
        'dilu': MEMORY_DILU,
        'voyage': MEMORY_VOYAGE,
        'generative': MEMORY_GENERATIVE,
        'tp': MEMORY_TP,
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
    travelplannerSolver = AGENT("travelplannerSolver", '', memory_func, reasoning_func, tooluse_func, planning_func, llms_type)
    return travelplannerSolver


#------------------------------------------------- module level search -------------------------------------------
#任务名称+描述
def run_travel():
    price_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--SET_TYPE", type=str, default="validation")
    parser.add_argument("--MODEL_NAME", type=str, default="gpt-3.5-turbo-0125")
    parser.add_argument("--OUTPUT_DIR", type=str, default="./")
    parser.add_argument("--STRATEGY", type=str, default="direct")
    parser.add_argument("--MODE", type=str, default="two-stage")
    parser.add_argument("--TMP_DIR", type=str, default="./")
    parser.add_argument("--SUBMISSION_DIR", type=str, default="./")
    parser.add_argument("--EVALUATION_FILE_PATH", type=str, default="./")
    parser.add_argument("--planning", required=True, default='', help="specify the place to store the resuls")
    parser.add_argument("--reasoning", required=True, default='', help="specify the project name for wandb")
    parser.add_argument("--tooluse", required=True, default='', help="specify the baseline loggings for wandb baseline comparison visualization")
    parser.add_argument("--memory", required=True, default='', help="specify the maximum number of steps used to finish the problems")
    parser.add_argument("--OPENAI_API_KEY", type=str, default="sk-4iQVFio5D3ef906N4hC-K9AbCX887_U5kU1S4fcqT5T3BlbkFJJa2AtlZUKv3STlHEoVqhHdX7MMvYU1OYHXw09gBG0A")
    parser.add_argument("--GOOGLE_API_KEY", required=False, default='1', help="specify the maximum number of steps used to finish the problems")

    # parser.add_argument("--model", required=True ,help="specify the models, available models are stated in the configuration file")
    args = parser.parse_args()
    planning = args.planning
    reasoning = args.reasoning
    tooluse = args.tooluse
    memory = args.memory
    llms_type = ['gpt-3.5-turbo-0125']
    print("*" * 100)
    print(f"--Planning module: {planning}  --Reasoning module: {reasoning}   --Tooluse module: {tooluse}   --Memory module: {memory}")
    print("*" * 100)
    tools_list = ["notebook","flights","attractions","accommodations","restaurants","googleDistanceMatrix","planner","cities"]
    # model_name = ['gpt-3.5-turbo-1106','gpt-4-1106-preview','gemini','mistral-7B-32K','mixtral','ChatGLM3-6B-32K'][2]
    print(f"Current OUTPUT_DIR is {args.OUTPUT_DIR}")
    if args.SET_TYPE == 'validation':
        query_data_list = load_from_disk("C:\\Users\\kyzhao\\Desktop\\Study\\LLMAgent\\TravelPlanner\\agents\\dataset")['validation']
        # query_data_list  = load_dataset('osunlp/TravelPlanner','validation')
        # query_data_list.save_to_disk('C:\\Users\\kyzhao\\Desktop\\Study\\LLMAgent\\TravelPlanner\\agents\\dataset')
        # query_data_list = query_data_list['validation']
    elif args.SET_TYPE == 'train':
        query_data_list = load_from_disk("C:\\Users\\kyzhao\\Desktop\\Study\\LLMAgent\\TravelPlanner\\agents\\dataset_train")['train']
        
    elif args.SET_TYPE == 'test':
        # query_data_list = load_dataset('csv', data_files='test.csv')
        query_data_list  = load_dataset('osunlp/TravelPlanner','test')['test']
    # else:
    #     raise ValueError(f"Invalid set_type: {args.set_type}")

    # if query_data_list is None:
    #     raise ValueError("Failed to load data. Please check the dataset path and format.")
    # numbers = [i for i in range(161,167)]
    # numbers = [i for i in range(1,len(query_data_list)+1)]
    travelplannerSolver = agent_build(planning=planning, reasoning=reasoning, tooluse=tooluse, memory=memory, llms_type=[args.MODEL_NAME])
    agent = ReactAgent(None, tools=tools_list,max_steps=30,react_llm_name=args.MODEL_NAME,planner_llm_name=args.MODEL_NAME,travelplannerSolver=travelplannerSolver)
    max_retries = 3
    with get_openai_callback() as cb:
        validation_directory = os.path.join(f'{args.OUTPUT_DIR}/{args.SET_TYPE}')
        if not os.path.exists(validation_directory):
            os.makedirs(validation_directory)
        iteration = 0
        while len(os.listdir(validation_directory)) < 30 and iteration < 6:
            numbers = find_missing_files(validation_directory)
            # numbers = [i for i in range(111,141)]
            for number in tqdm(numbers[:]):
                retries = 0
                while retries < max_retries:
                    try :
                        query = query_data_list[number-1]['query']
                        # check if the directory exists
                        if not os.path.exists(os.path.join(f'{args.OUTPUT_DIR}/{args.SET_TYPE}')):
                            os.makedirs(os.path.join(f'{args.OUTPUT_DIR}/{args.SET_TYPE}'))
                        if not os.path.exists(os.path.join(f'{args.OUTPUT_DIR}/{args.SET_TYPE}/generated_plan_{number}.json')):
                            result =  [{}]
                        else:
                            result = json.load(open(os.path.join(f'{args.OUTPUT_DIR}/{args.SET_TYPE}/generated_plan_{number}.json')))

                        if isinstance(agent.travelplannerSolver.reasoning, REASONING_STEPBACK):
                            agent.travelplannerSolver.reasoning.principle = ''
                            print('stepback已初始化')
                            
                        while True:
                            planner_results, scratchpad, action_log  = agent.run(query)
                            if planner_results != None:
                                break
                        
                        if planner_results == 'Max Token Length Exceeded.':
                            result[-1][f'{args.MODEL_NAME}_two-stage_results_logs'] = scratchpad 
                            result[-1][f'{args.MODEL_NAME}_two-stage_results'] = 'Max Token Length Exceeded.'
                            action_log[-1]['state'] = 'Max Token Length of Planner Exceeded.'
                            result[-1][f'{args.MODEL_NAME}_two-stage_action_logs'] = action_log
                        else:
                            result[-1][f'{args.MODEL_NAME}_two-stage_results_logs'] = scratchpad 
                            result[-1][f'{args.MODEL_NAME}_two-stage_results'] = planner_results
                            result[-1][f'{args.MODEL_NAME}_two-stage_action_logs'] = action_log

                        # write to json file
                        with open(os.path.join(f'{args.OUTPUT_DIR}/{args.SET_TYPE}/generated_plan_{number}.json'), 'w') as f:
                            json.dump(result, f, indent=4)
                        # shutil.copy(f'{args.output_dir}/{args.set_type}/generated_plan_{number}.json', 'C:\\Users\\kyzhao\\Desktop\\Study\\LLMAgent\\TravelPlanner\\output_plan_copy\\output_plan5')
                        break

                    except Exception as e:
                        retries += 1
                        error_log_file_path = os.path.join("..","error_log.txt")
                        with open(error_log_file_path,"a") as log_file:
                            log_file.write(f"--Planning module: {planning}  --Reasoning module: {reasoning}   --Tooluse module: {tooluse}   --Memory module: {memory}\nTask {query} (index: {number}) failed with error: {str(e)}.Retry {retries}/{max_retries}.\n\n")
                        print(f"--Planning module: {planning}  --Reasoning module: {reasoning}   --Tooluse module: {tooluse}   --Memory module: {memory}\nTask {query} (index: {number}) failed, retrying... ({retries}/{max_retries}).")
                        if retries >= max_retries:
                            print(f"--Planning module: {planning}  --Reasoning module: {reasoning}   --Tooluse module: {tooluse}   --Memory module: {memory}\nTask {query} (index: {number}) failed after {max_retries} retries, skipping to the next task.")
            iteration += 1
    print(cb)
    completion_tokens, prompt_tokens, price = get_price()
    print(f'total_completion_tokens:{completion_tokens}\ntotal_prompt_tokens:{prompt_tokens}\ntotal_price={completion_tokens*1.5/1000000+prompt_tokens*0.5/1000000}')

    price_list.append(completion_tokens*1.5/1000000+prompt_tokens*0.5/1000000)
    print(price_list)

    print("-"*100)
    print(f"Current OUTPUT_DIR is {args.OUTPUT_DIR}")
    print(f"Current TMP_DIR is {args.TMP_DIR}")
    print(f"Current SUBMISSION_DIR is {args.SUBMISSION_DIR}")
    print(f"Current EVALUATION_FILE_PATH is {args.EVALUATION_FILE_PATH}")
    print("-"*100)

    env = os.environ.copy()
    env['TMP_DIR'] = args.TMP_DIR
    env['SUBMISSION_DIR'] = args.SUBMISSION_DIR
    env['EVALUATION_FILE_PATH'] = args.EVALUATION_FILE_PATH
    env['OUTPUT_DIR'] = args.OUTPUT_DIR
    env['SET_TYPE'] = args.SET_TYPE
    env['MODEL_NAME'] = args.MODEL_NAME
    env['STRATEGY'] = args.STRATEGY
    env['MODE'] = args.MODE
    env['OPENAI_API_KEY'] = "sk-4iQVFio5D3ef906N4hC-K9AbCX887_U5kU1S4fcqT5T3BlbkFJJa2AtlZUKv3STlHEoVqhHdX7MMvYU1OYHXw09gBG0A"

    result = subprocess.run(["C:\\Users\\kyzhao\\Desktop\\Study\\LLMAgent\\TravelPlanner\\agents\\run.bat"], env=env,capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    for line in result.stdout.split('\n'):
        if 'Delivery Rate' in line:
            Delivery_Rate = round(float(re.search(r'\d+\.\d+', line).group()), 3)
        if 'Commonsense Constraint Micro Pass Rate' in line:
            Commonsense_Constraint_Micro_Pass_Rate = round(float(re.search(r'\d+\.\d+', line).group()), 3)
        if 'Commonsense Constraint Macro Pass Rate' in line:
            Commonsense_Constraint_Macro_Pass_Rate = round(float(re.search(r'\d+\.\d+', line).group()), 3)
        if 'Hard Constraint Micro Pass Rate' in line:
            Hard_Constraint_Micro_Pass_Rate = round(float(re.search(r'\d+\.\d+', line).group()), 3)
        if 'Hard Constraint Macro Pass Rate' in line:
            Hard_Constraint_Macro_Pass_Rate = round(float(re.search(r'\d+\.\d+', line).group()), 3)
        if 'Final Pass Rate' in line:
            Final_Pass_Rate = round(float(re.search(r'\d+\.\d+', line).group()), 3)
    print({'planning':planning, 'reasoning':reasoning, 'tooluse':tooluse, 'memory':memory, 'Delivery Rate':Delivery_Rate,'Commensense Constraint Micro Pass Rate':Commonsense_Constraint_Micro_Pass_Rate, 'Commonsense Constraint Macro Pass Rate': Commonsense_Constraint_Macro_Pass_Rate, 'Hard Constraint Micro Pass Rate': Hard_Constraint_Micro_Pass_Rate, 'Hard Constraint Macro Pass Rate': Hard_Constraint_Macro_Pass_Rate, 'Final Pass Rate': Final_Pass_Rate})
    print("-*100")
    print(price_list)
    return Commonsense_Constraint_Micro_Pass_Rate