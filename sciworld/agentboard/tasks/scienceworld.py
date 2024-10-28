import os
import pdb
import json
import re
import time
from llm import load_llm
from agents import load_agent
import random
from environment import load_environment
import jsonlines
from common.registry import registry
from utils_llm import get_price
from REASONING_STEPBACK import REASONING_STEPBACK

from utils.logging.logger import TaskLogger
from utils.logging.agent_logger import AgentLogger
from workflow import workflow
logger = AgentLogger(__name__)

from .base_task import BaseTask


@registry.register_task("scienceworld")
class EvalScienceworld(BaseTask):
    def __init__(self,
                 llm_name="gpt",
                 llm_config=None,
                 agent_name="GPTAgent",
                 agent_config=None,
                 env_config=None,
                 run_config=None,
                 llm=None,
                 baseline_dir = None,
                 log_path = None,
                 scienceworldSolver = None
                 ):
        
        super().__init__()
        
        if llm is None:
            llm = load_llm(llm_name, llm_config)
        self.llm = llm
        init_prompt_path = agent_config.get("init_prompt_path", None)
        self.agent = load_agent(agent_name, agent_config, llm)
        self.simplefied = env_config.get("simplefied", False)
        seed = env_config.get("seed", 42)
        self.set_seed(seed)
        self.simplification_str = self.build_simplification_str()
        self.env_cfg = env_config
        
        # change the name max_episode to max_num_step for consistency
        self.max_num_steps = run_config.get("max_num_steps", 30)
        self.context_length = llm_config.get("context_length")

        self.baseline_dir = baseline_dir
        
        self.agentboard = TaskLogger(task_name="scienceworld", log_path=log_path, max_num_steps=self.max_num_steps, baseline_dir=self.baseline_dir)
        self.scienceworldSolver = scienceworldSolver

        if init_prompt_path is not None:    # load from file
            self.init_prompt_dict = json.load(open(init_prompt_path, 'r'))

        
    def build_simplification_str(self):

        simplifications = list()
        simplifications.append("selfWateringFlowerPots")
        simplifications.append("openContainers")
        simplifications.append("openDoors")
        simplifications.append("noElectricalAction")

        return ",".join(simplifications)

    def set_seed(self, seed):
        random.seed(seed)
    
    def get_action_string(input_string):
        actions = [
        "activate OBJ", "close OBJ", "deactivate OBJ", "dunk OBJ in OBJ", "eat OBJ",
        "flush OBJ", "focus on OBJ", "go OBJ", "inventory", "look around", "look at OBJ",
        "look in OBJ", "mix OBJ", "move OBJ to OBJ", "open OBJ", "pick up OBJ",
        "pour OBJ in OBJ", "put down OBJ", "read OBJ", "task", "use OBJ on OBJ",
        "wait", "wait1", "check valid actions"
        ]
        for action in actions:
            # 将动作中的 OBJ 替换为正则表达式的捕获组
            action_pattern = action.replace('OBJ', r'([^,]+)')
            pattern = rf'\b{action_pattern}\b'
            
            match = re.fullmatch(pattern, input_string.strip())
            if match:
                # 提取动作和参数
                matched_action = action
                params = match.groups()
                # 替换动作中的 OBJ 为实际的参数
                for param in params:
                    matched_action = matched_action.replace('OBJ', param, 1)
                return matched_action
        
        return "Unknown action"

    def evaluate_env(self, index, task_name, var, modified_goal):
        self.env.load(task_name, var, simplificationStr=self.simplification_str)
        initialObs, initialDict = self.env.reset()
        init_obs = initialObs + f"\n{self.env.inventory()}"
        self.agent.reset(goal=modified_goal, init_obs=init_obs)
        reward = 0.
        last_reward = 0.
       # print(init_obs)
        logger.info("Step {:02} - Observation: {}".format(0, init_obs))
        print("Step {:02} - Observation: {}".format(0, init_obs))
        grounding_acc_count = 0
        score_change_record = []
        isDone = False
        
        trajectory = []
        trajectory.append({"Goal":modified_goal, "id":0})
        trajectory.append({"Observation":init_obs, "id":0})  
        
        correct_trajectory = []
        #init prompt
        instruction = self.init_prompt_dict['instruction']
        examples = self.init_prompt_dict['examples']
        system_message = self.init_prompt_dict['system_msg']

        class SCIWORLD():
            def __init__(self, env, solver, agent):
                self.max_step_number = self.max_num_steps
                if solver.planning is None:
                    self.task_description = self.get_task_description()
                else:
                    self.task_description = modified_goal
                self.task_type = task_name
                self.max_step_number_plan = 6
                self.tool_instruction = ''
                self.feedback_previous_tools = ''
                self.solver = solver
                self.agent = agent
                self.correct_action = []
                self.memory = ''
                self.prompt = ''
                self.memory_pool = []
                self.env= env
                
            def get_task_description(self):
                input_prompt = ''
                input_prompt += instruction

                if len(examples) > 0:
                    input_prompt += "\nHere are examples:\n"
                # for example in examples:
                input_prompt += examples + "\n"
                
                input_prompt += "You should output action in the command pool to accomplish the goal: " + modified_goal + "\n" 
                
                input_prompt += "You should use the following command for help when your action cannot be understood: " + self.agent.check_actions + "\n"
                

                history = self.agent.memory
                task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])
                if self.solver.memory is not None:
                        memory = self.solver.memory(f"Task: {modified_goal} ")
                        if memory is not None:
                            task_description += memory

                task_description += "\nAction: "
                return task_description
            def step(self, action):
                action = self.agent.action_parser_for_special_llms(action[0])
                observation, reward, done, info = self.env.step(action)
                if reward > last_reward:
                    self.correct_action.append({"Action": action,"Observation": observation})
                    last_reward = reward
                self.agent.update(action=action,
                                state=observation)
                return observation, reward, done
            def memory_update(self):
                return f"Task : {modified_goal} \nThe correct trajectory is : {self.correct_action}"
            def prompt_reset():
                self.prompt = ''
            def prompt_exp_update(self, sub_task_id):
                return ''
            def init_prompt_update(self, sub_tasks, sub_task_id):
                input_prompt = ''
                input_prompt += instruction

                if len(examples) > 0:
                    input_prompt += "\nHere are examples:\n"
                input_prompt += examples + "\n"
                
                input_prompt += "The final task you should complete is : " + modified_goal + "\n"  
                input_prompt += "The current subtask you should select the action in the command pool to complete is :" + sub_tasks[sub_task_id]['reasoning instruction'] + "\n" 
                
                input_prompt += "You should use the following commands for help when your action cannot be understood: " + self.agent.check_actions + "\n"
                input_prompt += "If you think you've accomplished your goal, just output OK."

                history = self.agent.memory
                task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])
                if self.solver.memory is not None:
                    memory = self.solver.memory(f"Task: {modified_goal}")
                    if memory is not None:
                        task_description += memory

                task_description += "\nAction: "
                return task_description
            def memory_cache(self, sub_tasks, sub_task_id):
                self.memory_pool.append(f"Task : {modified_goal} \nThe correct trajectory is : {self.correct_action}")
            def flag(self, action, sub_tasks, sub_task_id):
                if 'OK' in action :
                    return True
                else:
                    return False

        sciworld = SCIWORLD(self.env, self.scienceworldSolver, self.agent)
        return workflow(sciworld, self.scienceworldSolver)

        if self.scienceworldSolver.planning is None:
            for i in range(self.max_num_steps):
                input_prompt = ''
                input_prompt += instruction

                if len(examples) > 0:
                    input_prompt += "\nHere are examples:\n"
                # for example in examples:
                input_prompt += examples + "\n"
                
                input_prompt += "You should output action in the command pool to accomplish the goal: " + modified_goal + "\n" 
                
                input_prompt += "You should use the following command for help when your action cannot be understood: " + self.agent.check_actions + "\n"
                

                history = self.agent.memory
                task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])
                if self.scienceworldSolver.memory is not None:
                        memory = self.scienceworldSolver.memory(f"Task: {modified_goal} ")
                        if memory is not None:
                            task_description += memory

                task_description += "\nAction: "
                
                action_raw = self.scienceworldSolver.reasoning(task_description, '', '')
                action = self.agent.action_parser_for_special_llms(action_raw)

                #success, action = self.agent.run()
                logger.info("Step {:02} - Action: {}".format(i, action))
                print("Step {:02} - Action: {}".format(i, action))
                trajectory.append({"Action":action, "id":i})
                
                observation, reward, isDone, info = self.env.step(action)
                if action in self.env.get_action_space(abstract=False):
                    grounding_acc_count += 1
                    
                #print(f"step: {i} ACTION: {action}\nOBSERVATION: {observation}")
                logger.info("Step {:02} - Observation: {}".format(i, observation))
                logger.info("Step {:02} - Progress Rate: {}\n".format(i, reward))
                print("Step {:02} - Observation: {}".format(i, observation))
                print("Step {:02} - Progress Rate: {}\n".format(i, reward))
                
                trajectory.append({"Observation":observation, "id":i})
                trajectory.append({"Progress Rate":reward, "id":i})
                
                if reward > last_reward:
                    score_change_record.append((i, reward))
                    correct_trajectory.append({"Action": action,"Observation": observation})
                    print(correct_trajectory)
                    # if self.scienceworldSolver.memory is not None :
                    #     self.scienceworldSolver.memory(f"Task and the action has been completed: {trajectory} \nThe next correct action is : {action}")
                last_reward = reward
                if isDone:
                    if self.scienceworldSolver.memory is not None :
                        print(f"Task : {modified_goal} \nThe correct trajectory is : {correct_trajectory}")
                        self.scienceworldSolver.memory(f"Task : {modified_goal} \nThe correct trajectory is : {correct_trajectory}")

                    env_details = {"task_name": task_name, "goal": self.agent.goal, "difficulty": self.env.difficulty}
                    self.agentboard.log_example(index, True, 1.0, grounding_acc_count / (i + 1), score_change_record, env_details, trajectory)
                
                    return 1.0, True, grounding_acc_count / (i + 1), score_change_record, i
                
                self.agent.update(action=action,
                                state=observation)
        else: 
            task_description = modified_goal
            task_type = task_name
            sub_tasks = self.scienceworldSolver.planning(task_type=task_type, task_description=task_description, feedback='')
            for sub_task in sub_tasks:
                print(sub_task)
            i = 0
            for sub_task_id in range(len(sub_tasks)):
                for sub_task_step_id in range(6):#防止无法完成子任务时，一直循环
                    print(f'This is subtaks {sub_task_id+1}\nThis subtask has been run {sub_task_step_id+1} times.')
                    i += 1
                    input_prompt = ''
                    input_prompt += instruction

                    if len(examples) > 0:
                        input_prompt += "\nHere are examples:\n"
                    input_prompt += examples + "\n"
                    
                    input_prompt += "The final task you should complete is : " + modified_goal + "\n"  
                    input_prompt += "The current subtask you should select the action in the command pool to complete is :" + sub_tasks[sub_task_id]['reasoning instruction'] + "\n" 
                    
                    input_prompt += "You should use the following commands for help when your action cannot be understood: " + self.agent.check_actions + "\n"
                    input_prompt += "If you think you've accomplished your goal, just output OK."

                    history = self.agent.memory
                    task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])
                    if self.scienceworldSolver.memory is not None:
                        memory = self.scienceworldSolver.memory(f"Task: {modified_goal}")
                        if memory is not None:
                            task_description += memory

                    task_description += "\nAction: "

                    action_raw = self.scienceworldSolver.reasoning(task_description, '', '')

                    action = self.agent.action_parser_for_special_llms(action_raw)

                    #success, action = self.agent.run()
                    logger.info("Step {:02} - Action: {}".format(i, action))
                    logger.info("Step {:02} - Action: {}".format(i, action_raw))
                    trajectory.append({"Action":action, "id":i})
                    
                    observation, reward, isDone, info = self.env.step(action)
                    if action in self.env.get_action_space(abstract=False):
                        grounding_acc_count += 1
                        
                    #print(f"step: {i} ACTION: {action}\nOBSERVATION: {observation}")
                    logger.info("Step {:02} - Observation: {}".format(i, observation))
                    logger.info("Step {:02} - Progress Rate: {}\n".format(i, reward))
                    
                    trajectory.append({"Observation":observation, "id":i})
                    trajectory.append({"Progress Rate":reward, "id":i})
                    
                    if reward > last_reward:
                        score_change_record.append((i, reward))
                        correct_trajectory.append({"Action": action,"Observation": observation})
                        print(correct_trajectory)
                        # if self.scienceworldSolver.memory is not None :
                        #     self.scienceworldSolver.memory(f"Task and the action has been completed: {trajectory} \nThe next correct action is : {action}")
                    last_reward = reward
                    if isDone:
                        if self.scienceworldSolver.memory is not None :
                            print(f"Task : {modified_goal} \nThe correct trajectory is : {correct_trajectory}")
                            self.scienceworldSolver.memory(f"Task : {modified_goal} \nThe correct trajectory is : {correct_trajectory}")

                        env_details = {"task_name": task_name, "goal": self.agent.goal, "difficulty": self.env.difficulty}
                        
                        self.agentboard.log_example(index, True, 1.0, grounding_acc_count / (i + 1), score_change_record, env_details, trajectory)
                    
                        return 1.0, True, grounding_acc_count / (i + 1), score_change_record, i
                    
                    self.agent.update(action=action,
                                       state=observation)

                    if 'OK' in action_raw :
                        break

        
        env_details = {"task_name": task_name, "goal": self.agent.goal, "difficulty": self.env.difficulty}
        try: example_prompt = self.agent.get_example_prompt()
        except: example_prompt = None  
        
        progress_rate = reward
        
        self.agentboard.log_example(index, isDone, progress_rate, grounding_acc_count / (i + 1), score_change_record, env_details, trajectory, example_prompt)

        return progress_rate, isDone, grounding_acc_count / (i + 1), score_change_record, i

    def evaluate(self):
        scores = []
        self.env = load_environment("scienceworld", self.env_cfg)
        labels = self.env.labels
        count = 0
        scores = []
        score_state_records = []
        grounding_accs = []
        srs = []
        # global completion_tokens ,prompt_tokens
        # completion_tokens=0
        # prompt_tokens = 0
        
        difficulties = []
        
        for index, (k, v) in enumerate(labels.items()):

            
            task_name = v["task_name"]
            var = v["var"]
            modified_goal = v["modified_goal"]
            
            #print(f"Starting Task: {task_name}, variation: {var}, goal: {modified_goal}")
            logger.goal("Example {} | Goal: {}".format(index, f"task_name: {task_name}, var: {var}, {modified_goal}"))
            max_retries = 2
            retries = 0
            # score, done, grounding_acc, score_change_record, num_steps = self.evaluate_env(index, task_name, var, modified_goal)
            # try:
            if isinstance(self.scienceworldSolver.reasoning, REASONING_STEPBACK):
                self.scienceworldSolver.reasoning.principle = ''
                print('stepback已初始化')
            score, done, grounding_acc, score_change_record, num_steps = self.evaluate_env(index, task_name, var, modified_goal)
            difficulties.append(self.env.difficulty)
            logger.finish("Example {} | Success: {} , Progress Rate: {} , Steps: {}\n".format(index, done, score, num_steps + 1))
            completion_tokens, prompt_tokens, price = get_price()
            count += 1
            if done:
                srs.append(1.0)
            else:
                srs.append(0.0)
            scores.append(score)
            grounding_accs.append(grounding_acc)
            score_state_records.append(score_change_record)
            # except Exception as e:
            #     error_log_file_path = os.path.join("..","error_log.txt")
            #     with open(error_log_file_path,"a") as log_file:
            #         log_file.write(f"--Planning module: {self.scienceworldSolver.planning}  --Reasoning module: {self.scienceworldSolver.reasoning}   --Tooluse module: None   --Memory module: {self.scienceworldSolver.memory}\nTask {task_name} (index: {index}) failed with error: {str(e)}\n\n")
                # print(f"--Planning module: {self.scienceworldSolver.planning}  --Reasoning module: {self.scienceworldSolver.reasoning}   --Tooluse module: None   --Memory module: {self.scienceworldSolver.memory}\nTask {task_name} (index: {index}) failed.\n\n")
            
            #print(f"task: {task_name}, var: {var}, score: {score}, done: {done}" )

        #print(f"avg score: {sum(scores) * 1.0 / len(scores)}, SR: {sum(srs) * 1.0 / len(srs)}")

        sr = sum(srs) * 1.0 / len(srs)
        pr = sum(scores) * 1.0 / len(scores)
        gr = sum(grounding_accs) * 1.0 / len(grounding_accs)

        hard_sr = [sr for sr, difficulty in zip(srs, difficulties) if difficulty == "hard"]
        hard_sr = sum(hard_sr) / len(hard_sr) if len(hard_sr) > 0 else 0

        hard_pr = [pr for pr, difficulty in zip(scores, difficulties) if difficulty == "hard"]
        hard_pr = sum(hard_pr) / len(hard_pr) if len(hard_pr) > 0 else 0

        easy_sr = [sr for sr, difficulty in zip(srs, difficulties) if difficulty == "easy"]
        easy_sr = sum(easy_sr) / len(easy_sr) if len(easy_sr) > 0 else 0

        easy_pr = [pr for pr, difficulty in zip(scores, difficulties) if difficulty == "easy"]
        easy_pr = sum(easy_pr) / len(easy_pr) if len(easy_pr) > 0 else 0
                    
        
        self.agentboard.log_summary(sr, pr, gr, score_state_records, hard_sr, hard_pr, easy_sr, easy_pr)
        print("-"*100)
        price = completion_tokens*10/1000000+prompt_tokens*2.5/1000000
        print(f'total_completion_tokens:{completion_tokens}, total_prompt_tokens:{prompt_tokens}, total_price={completion_tokens*10/1000000+prompt_tokens*2.5/1000000}')
        print("-"*100)
        return  srs, scores, grounding_accs, score_state_records, easy_sr, hard_sr, easy_pr, hard_pr, price

    def _grounding_fn(self, action):
        valid_actions = self.env.GetValidActions()
        return "check valid actions" if action not in valid_actions else action

    @classmethod
    def from_config(cls,
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm=None,
                    scienceworldSolver=None
                    ):
        llm_name = llm_config.get("name", "gpt")
        agent_name = agent_config.get("name", "GPTAgent")
        baseline_dir = run_config.get("baseline_dir", "data/baseline_results")
        log_path = run_config.get("log_path", None)
                
        return cls(llm_name=llm_name,
                   llm_config=llm_config,
                   agent_name=agent_name,
                   agent_config=agent_config,
                   env_config=env_config,
                   run_config=run_config,
                   llm=llm,
                   baseline_dir=baseline_dir,
                   log_path = log_path,
                   scienceworldSolver = scienceworldSolver
                   )


