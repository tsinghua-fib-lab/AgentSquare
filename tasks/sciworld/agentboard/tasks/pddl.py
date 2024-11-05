import os
import json
import numpy as np

from llm import load_llm
from agents import load_agent
from environment import load_environment
from common.registry import registry
from utils.logging.logger import TaskLogger
from utils.logging.agent_logger import AgentLogger

from .base_task import BaseTask

logger = AgentLogger(__name__)


@registry.register_task("pddl")
class EvalPddl(BaseTask):
    
    # default problem config: 
    
    
    def __init__(self,
                 llm_name = "gpt",
                 llm_config = None,
                 agent_name = "POMDPAgent",
                 agent_config = None,
                 env_config = None,
                 max_num_steps = 20,
                 llm = None,
                 baseline_dir = None,
                 log_path = None,
                 PddlSolver = None
                ):
        
        super().__init__()

        if llm is None:
            llm = load_llm(llm_name, llm_config)
        self.llm = llm
        init_prompt_path = agent_config.get("init_prompt_path", None)
        agent_config["init_prompt_path"] = None
        self.agent = load_agent(agent_name, agent_config, llm)
        
        self.label_path = env_config.get("label_path", None)
        
        self.env_num_per_task = env_config.get("env_num_per_task", 1)
        self.game_name = env_config.get("game_name", []) # list of game levels
        self.env_configs = self.get_all_environment_configs()
        self.max_num_steps = max_num_steps
        self.PddlSolver = PddlSolver
        
        
        if init_prompt_path is not None:    # load from file
            self.init_prompt_game_dict = json.load(open(init_prompt_path, 'r')) 
        
        self.baseline_dir = baseline_dir
        
        self.agentboard = TaskLogger(task_name="pddl", log_path=log_path, max_num_steps=self.max_num_steps, baseline_dir=self.baseline_dir)

    def load_seq(self, path):
        all_seqs = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                all_seqs.append(line.strip())
        return all_seqs
    
    def load_annotation(self, path):
        all_annotations = None  
        difficulty = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                line = json.loads(line.strip())
                if "difficulty" in line:
                    difficulty.append(line["difficulty"])
                else:
                    raise ValueError("No difficulty in annotation file")
        return all_annotations, difficulty
    
    def get_all_environment_configs(self):
        env_configs = []
        iter_num = 0
        _, difficulties = self.load_annotation(self.label_path)
        
        for game_name in self.game_name:
            num_problems = min(self.env_num_per_task, Num_Problems[game_name])
            for i in range(num_problems):
                env_configs.append({
                    "game_name": game_name,
                    "problem_index": i,
                    "difficulty": difficulties[iter_num]
                })
                
                iter_num += 1
        
        return env_configs
    
    
    def evaluate_env(self, id):
        env = load_environment("pddl", self.env_configs[id])
        game_name = env.game_name
        init_obs = env._get_obs()
        goal = env._get_goal()
        self.agent.reset(goal, init_obs)
        
        trajectory = []
        trajectory.append({"Goal":goal, "id":0})
        trajectory.append({"Observation":init_obs, "id":0})  
        
        logger.goal("Example {} | Goal: {}".format(id, self.agent.goal))
        logger.info("Step {:02} - Message: {}".format(0, init_obs))


        max_steps = self.max_num_steps
        reward = 0.
        last_reward = 0.
        grounding_acc_count = 0
        score_change_record = []  
        
        # init prompt
        
        instruction = self.init_prompt_game_dict[game_name]['instruction']
        examples = self.init_prompt_game_dict[game_name]['examples']
        system_message = self.init_prompt_game_dict[game_name]['system_msg']
        
        if self.PddlSolver.planning is None:
            for step_id in range(max_steps):
                input_prompt = ''
                input_prompt += instruction

                if len(examples) > 0:
                    input_prompt += "\nHere are examples:\n"
                for example in examples:
                    input_prompt += example + "\n"
                
                input_prompt += "You should perform actions to accomplish the goal: " + goal + "\n" 
                
                input_prompt += "You should use the following commands for help when your action cannot be understood: " + self.agent.check_actions + "\n"
                

                history = self.agent.memory
                task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])

                task_description += "\nAction: "

                messages = [
                {"role": "system", "content": ''},
                {"role": "user", "content": task_description}
                ]
                num_of_tokens = self.llm.num_tokens_from_messages(messages)
                while num_of_tokens > self.llm.context_length - self.llm.max_tokens-1000:#多减1k防止reasoning模块调用token超出
                    history = history[1:]
                    task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])
                    task_description += "\nAction: "
                    # task_description += "\nPlease enter your action:"
                    messages = [
                        {"role": "system", "content": ''},
                        {"role": "user", "content": task_description}
                    ]
                    num_of_tokens = self.llm.num_tokens_from_messages(messages)
                

                action = self.PddlSolver.reasoning(task_description, '', '')

                action = self.agent.action_parser_for_special_llms(action)

                #success, action = self.agent.run(init_prompt_dict = self.init_prompt_game_dict[game_name])
                
                trajectory.append({"Action":action, "id":step_id})
                
                logger.info("Step {:02} - Action: {}".format(step_id, action))
                state, reward, done, infos = env.step(action)
                
                trajectory.append({"Observation":state, "id":step_id})
                trajectory.append({"Progress Rate":reward, "id":step_id})
                
                if infos.get("action_is_valid", False): 
                    grounding_acc_count += 1
                
                if reward > last_reward:
                    score_change_record.append((step_id, reward))
                last_reward = reward
                
                logger.info("Step {:02} - Observation: {}".format(step_id, state))
                logger.info("Step {:02} - Progress Rate: {}\n".format(step_id, reward))
                self.agent.update(action, state)
                
                if done:
                    
                    env_details = {"task_name": env.game_name, "goal": self.agent.goal, "difficulty": env.difficulty}
                    
                    progress_rate = reward
                    
                    self.agentboard.log_example(id, env.won, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory)

                    return env.won, progress_rate, step_id + 1, grounding_acc_count / (step_id + 1), score_change_record

        else: 
            task_description = goal
            task_type = game_name
            sub_tasks = self.PddlSolver.planning(task_type=task_type, task_description=task_description, feedback='')
            step_id = 0
            for sub_task_id in range(len(sub_tasks)):
                for sub_task_step_id in range(5):#防止无法完成子任务时，一直循环
                    step_id += 1
                    input_prompt = ''
                    input_prompt += instruction

                    if len(examples) > 0:
                        input_prompt += "\nHere are examples:\n"
                    for example in examples:
                        input_prompt += example + "\n"
                    
                    input_prompt += "You should perform actions to accomplish the goal: " + sub_tasks[sub_task_id]['reasoning instruction'] + "\n" 
                    
                    input_prompt += "You should use the following commands for help when your action cannot be understood: " + self.agent.check_actions + "\n"
                    input_prompt += "If you think you've accomplished your goal, just output OK."

                    history = self.agent.memory
                    task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])

                    task_description += "\nAction: "

                    messages = [
                    {"role": "system", "content": ''},
                    {"role": "user", "content": task_description}
                    ]
                    num_of_tokens = self.llm.num_tokens_from_messages(messages)
                    while num_of_tokens > self.llm.context_length - self.llm.max_tokens-1000:#多减1k防止reasoning模块调用token超出
                        history = history[1:]
                        task_description = input_prompt + "\n".join([item[0] + ": " + item[1] for item in history])
                        task_description += "\nAction: "
                        # task_description += "\nPlease enter your action:"
                        messages = [
                            {"role": "system", "content": ''},
                            {"role": "user", "content": task_description}
                        ]
                        num_of_tokens = self.llm.num_tokens_from_messages(messages)
                    

                    action_raw = self.PddlSolver.reasoning(task_description, '', '')

                    action = self.agent.action_parser_for_special_llms(action_raw)

                    #success, action = self.agent.run(init_prompt_dict = self.init_prompt_game_dict[game_name])
                    
                    trajectory.append({"Action":action, "id":step_id})
                    
                    logger.info("Step {:02} - Action: {}".format(step_id, action))
                    state, reward, done, infos = env.step(action)
                    
                    trajectory.append({"Observation":state, "id":step_id})
                    trajectory.append({"Progress Rate":reward, "id":step_id})
                    
                    if infos.get("action_is_valid", False): 
                        grounding_acc_count += 1
                    
                    if reward > last_reward:
                        score_change_record.append((step_id, reward))
                    last_reward = reward
                    
                    logger.info("Step {:02} - Observation: {}".format(step_id, state))
                    logger.info("Step {:02} - Progress Rate: {}\n".format(step_id, reward))
                    self.agent.update(action, state)
                    
                    if done:
                        
                        env_details = {"task_name": env.game_name, "goal": self.agent.goal, "difficulty": env.difficulty}
                        
                        progress_rate = reward
                        
                        self.agentboard.log_example(id, env.won, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory)

                        return env.won, progress_rate, step_id + 1, grounding_acc_count / (step_id + 1), score_change_record
                    if 'OK' in action_raw:
                        break
            

        env_details = {"task_name": env.game_name, "goal": self.agent.goal, "difficulty": env.difficulty}
        try: example_prompt = task_description
        except: example_prompt = None  
        
        progress_rate = reward
        
        self.agentboard.log_example(id, False, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory, example_prompt)
            
        return False, progress_rate, step_id + 1, grounding_acc_count / (step_id + 1), score_change_record
                
    
    
    def evaluate(self):
        num_envs = len(self.env_configs)
        success_rate = []
        num_steps = []
        all_progress_rates = []
        score_state_records = []
        grounding_accs = []
        difficulties = []
        
        for id in range(num_envs):

            success, progress_rate, steps, grounding_acc, score_change_record = self.evaluate_env(id)
            all_progress_rates.append(progress_rate)
            grounding_accs.append(grounding_acc)
            score_state_records.append(score_change_record)
            difficulties.append(self.env_configs[id]["difficulty"])
            
            if success:
                success_rate.append(1)
            else:
                success_rate.append(0)
            logger.finish("Example {} | Success: {} , Progress Rate: {} , Steps: {}\n".format(id, success, progress_rate, steps))
            completion_tokens, prompt_tokens, price = self.llm.get_price()
            print(f'completion_tokens:{completion_tokens}, prompt_tokens:{prompt_tokens}, price={completion_tokens*2/1000000+prompt_tokens*1.5/1000000}')

        sr = sum(success_rate) * 1.0 / len(success_rate)
        pr = sum(all_progress_rates) * 1.0 / len(all_progress_rates)
        gr = sum(grounding_accs) * 1.0 / len(grounding_accs)

        hard_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "hard"]
        hard_sr = sum(hard_sr) / len(hard_sr) if len(hard_sr) > 0 else 0

        hard_pr = [pr for pr, difficulty in zip(all_progress_rates, difficulties) if difficulty == "hard"]
        hard_pr = sum(hard_pr) / len(hard_pr) if len(hard_pr) > 0 else 0

        easy_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "easy"]
        easy_sr = sum(easy_sr) / len(easy_sr) if len(easy_sr) > 0 else 0

        easy_pr = [pr for pr, difficulty in zip(all_progress_rates, difficulties) if difficulty == "easy"]
        easy_pr = sum(easy_pr) / len(easy_pr) if len(easy_pr) > 0 else 0


        self.agentboard.log_summary(sr, pr, gr, score_state_records, hard_sr, hard_pr, easy_sr, easy_pr)
        
        return success_rate, all_progress_rates, grounding_accs, score_state_records, easy_sr, hard_sr, easy_pr, hard_pr
    
    @classmethod
    def from_config(cls, 
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm = None,
                    PddlSolver = None  
                    ):
        env_name = env_config.get("name", "pddl")
        assert env_name == "pddl"
        
        max_num_steps = run_config.get("max_num_steps", 20)
        baseline_dir = run_config.get("baseline_dir", "data/baseline_results")
        llm_name = llm_config.get("name", "gpt")
        agent_name = agent_config.get("name", "POMDPAgent")
        log_path = run_config.get("log_path", None)
    
        return cls(llm_name = llm_name,
                 llm_config = llm_config,
                 agent_name = agent_name,
                 agent_config = agent_config,
                 env_config = env_config,
                 max_num_steps = max_num_steps,
                 llm = llm,
                 baseline_dir = baseline_dir,
                 log_path = log_path,
                 PddlSolver = PddlSolver
                )
        
        
Num_Problems = {
    "barman":20, "blockworld":10,"gripper":20, "tyreworld":10
}
