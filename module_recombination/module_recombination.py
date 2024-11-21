from utils import llm_response


task_description = 'ALFworld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).' 

planning_candidate = {'None':'Do not use planning module',
                        'IO':'Input the task description to a LLM and directly output the sub-tasks',
                        'hugginggpt':'Input a task description into a LLM and output as few sub-tasks as possible. It is often used for image processing tasks and focuses on the correlation between sub-tasks',
                        'DEPS':'Input a task description in a LLM and output sub-goals. It is commonly used for embodied intelligence tasks',
                        'openagi':'Input a task description in a LLM and output a to-do list. It is often used to solve tasks using various tools',
                        'voyage': 'Input a task description in a LLM and output sub-goals.  It is often used to solve open world exploration problems'
                        }
reasoning_candidate = {'IO':'Input the task description to a LLM and directly output the answer',
                        'CoT':'A reasoning method prompting LLMs to think step-by-step for eliciting multi-step reasoning behavior',
                        'TOT':'A reasoning method prompting LLMs to perform deliberate decision making by considering multiple different reasoning paths and self-evaluating choices to decide the next course of action, as well as looking ahead or backtracking when necessary to make global choices',
                        'self-refine':'A reasoning method for improving initial outputs from LLMs through iterative feedback and refinement',
                        'CoT-SC': 'Combine multiple answers from these Chain-of-Thought (CoT) agents to produce a more accurate final answer through ensembling.',
                        'STEPBACK': 'Let LLM first think about the principles involved in solving this task which could be helpful.',
                        'DILU': 'Added a system prompt to act like an expert on something',
                        }  
tooluse_candidate = {'None':'Do not use tool use module',
                        'IO':'Input the task description to a tool use module and directly output the response',
                        'ANYTOOL': 'Select the tool category based on the task description, and then select the specific tool',
                        'TOOLBENCH': 'Convert the instructions and API documentation into vector representations, and then retrieve the most relevant API by calculating the vector similarity.',
                        'TOOLFORMER': 'Determine the best response using an LLM by inputting the problem description into a tool-use module, performing three selections, and directly outputting the best one.'}
memory_candidate = {'None':'Do not use memory module',
                    'Dilu':'Store the task resolution trajectory. Based on the task name to retrieve the relevant task solving trajectory',
                    'voyager':'Store the task resolution trajectory, and summarize the task resolutiong trajectory. Based on the task summary to retrieve relevant the task resolution trajectory',
                    'Generative':'Store the task resolution trajectories. Retrieve relevant task-solving trajectories based on the task name, and select the one that the LLM considers most important',
                    'tp': 'Store the task resolution trajectories. Retrieve relevant task-solving trajectories based on the task name, and output guidance to heuristically assist the LLM in completing the current task',
                    }

tested_case = [{'planning':'None', 'reasoning':'IO', 'tooluse':'None', 'memory':'None', 'performance':0.41}]

prompt = 'You are an AI agent expert. Now you are required to design a LLM-based agent to solve the task of ' \
+ task_description + 'The agent is composed of four fundamental modules: planning, reasoning, tool use and memory. \
For each module you are required to choose one from the follwing provided candidates. \
Planning module candidates and descriptions: ' + str(planning_candidate) + ' Reasoning module candidates and descriptions: ' + str(reasoning_candidate) + ' Tool use module candidates and descriptions: ' + str(tooluse_candidate) + ' Memory module candidates and descriptions: ' + str(memory_candidate) \
+ 'The performance of some existing module combinations: ' + str(tested_case) +'. ' \
+ 'You are expected to give a new module combination to improve the performance on the task by considering (1) the matching degree between the module description and task description (2) performance of existing module combinations on the task. \
Your answer should follow the format:' +str({'planning': '<your choice>', 'reasoning': '<your choice>', 'tooluse': '<your choice>', 'memory': '<your choice>'})
model = 'gpt-4o'
response = llm_response(prompt=prompt, model=model, temperature=0.1)
agent = eval(response)

planning = agent['planning']
reasoning = agent['reasoning']
tooluse = agent['tooluse']
memory = agent['memory']
