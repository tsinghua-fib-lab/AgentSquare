import os
import re
import sys
import json
import traceback
import datetime
import importlib
import numpy as np
from typing import TypedDict, List, Dict, Tuple, Optional, Any
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from recombination import recombination
from module_evolution import evolution
from module_predictor import predict_performance

# Type definitions
class ModuleInfo(TypedDict):
    thought: str
    name: str
    module_type: str
    code: str
    performance: float

class Agent(TypedDict):
    planning: str
    reasoning: str
    tooluse: str
    memory: str

class TestedCase(Agent):
    performance: float

# Constants
TASK_DESCRIPTION = '''ALFworld is a suite of text-based environments that challenge an agent to solve 
multi-step tasks in a variety of interactive environments. It includes 6 types of tasks in which an agent 
needs to achieve a high-level goal (e.g. examine paper under desklamp) by navigating and interacting 
with a simulated household via text actions (e.g. go to coffeetable 1, take paper 2, use desklamp 1).'''

MODULE_TYPES = ['planning', 'reasoning', 'tooluse', 'memory']

def load_modules_from_json(filename: str) -> Tuple[Dict[str, str], List[ModuleInfo]]:
    """
    Load module information from a JSON file.
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        Tuple containing candidate modules and archive
    """
    with open(filename, 'r') as f:
        modules = json.load(f)
    
    candidates = {module["name"]: module["thought"] for module in modules}
    archive = [
        ModuleInfo(
            thought=module["thought"],
            name=module["name"],
            module_type=module["module type"],  # Manual mapping
            code=module["code"],
            performance=module["performance"]
        )
        for module in modules
    ]
    
    return candidates, archive

def run_benchmark(agent: Agent, n: int = 50) -> float:
    """
    Test agent performance on benchmark.
    
    Args:
        agent: Agent configuration
        n: Number of test runs
        
    Returns:
        Test performance score
    """
    original_cwd = os.getcwd()
    original_pythonpath = sys.path.copy()
    
    try:
        os.chdir('alfworld')
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)
        if parent_path in sys.path:
            sys.path.remove(parent_path)
        sys.path.append(os.path.join(current_path, 'alfworld'))
        
        import alfworld_run
        importlib.reload(alfworld_run)
        from alfworld_run import run_alfworld
        
        performance = run_alfworld(
            planning=agent['planning'],
            reasoning=agent['reasoning'],
            tooluse=agent['tooluse'],
            memory=agent['memory'],
            llms_type=['gpt-4o-mini'],
            n=n
        )
        return performance
        
    except Exception as e:
        error_msg = f"Error running benchmark: {e}"
        error_detail = f"Detailed error info:\n{traceback.format_exc()}"
        print(error_msg)
        print(error_detail)
        
        # Write error information to log file
        with open('agent_search_benchmark_errors.log', 'a') as f:
            f.write(f"\nTime: {datetime.datetime.now()}\n")
            f.write(f"Agent configuration: {agent}\n")
            f.write(error_msg + '\n')
            f.write(error_detail + '\n')
            f.write('-' * 80 + '\n')
            
        return 0
        
    finally:
        os.chdir(original_cwd)
        sys.path = original_pythonpath

def write_test_module(module_type: str, module_code: str) -> None:
    """
    Write test module to corresponding file.
    
    Args:
        module_type: Module type
        module_code: Module code
    """
    module_file = f'tasks/alfworld2/{module_type}_modules.py'
    base_class = f"{module_type.capitalize()}Base"
    test_class = f"{module_type.capitalize()}Test"
    
    with open(module_file, 'a') as f:
        if module_code == "pass":
            f.write(f'\nclass {test_class}({base_class}):\n    pass\n')
        else:
            f.write('\n' + re.sub(
                r'class \w+\(.*Base\)',
                f'class {test_class}({base_class})',
                module_code.replace("'\n'", "'\\n'").replace(":\n'", ":\\n'")
            ))

def remove_test_module(module_type: str) -> None:
    """
    Remove test module from file.
    
    Args:
        module_type: Module type
    """
    module_file = f'tasks/alfworld2/{module_type}_modules.py'
    test_class = f"{module_type.capitalize()}Test"
    
    with open(module_file, 'r') as f:
        lines = f.readlines()
    
    start_idx = -1
    for i, line in enumerate(lines):
        if f'class {test_class}' in line:
            start_idx = i
            break
    
    if start_idx != -1:
        lines = lines[:start_idx]
        with open(module_file, 'w') as f:
            f.writelines(lines)

def prepare_test_agent(agent: Agent, archives: Dict[str, List[ModuleInfo]]) -> Dict[str, str]:
    """
    Prepare agent test parameters.
    
    Args:
        agent: Agent to test
        archives: Module archives by type
        
    Returns:
        Test parameter configuration
    """
    test_params = {}
    for module_type in MODULE_TYPES:
        module_name = agent[module_type]
        if module_name != 'None':
            module_archive = archives[module_type]
            for module in module_archive:
                if module['name'] == module_name:
                    write_test_module(module_type, module['code'])
                    test_params[module_type] = 'test'
                    break
        else:
            write_test_module(module_type, "pass")
            test_params[module_type] = 'none'
    
    return test_params

def cleanup_test_modules() -> None:
    """Clean up all test modules"""
    for module_type in MODULE_TYPES:
        remove_test_module(module_type)

def save_to_json(data: Any, filename: str, folder: str = "agent_search_output") -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filename: File name
        folder: Output folder
    """
    try:
        Path(folder).mkdir(exist_ok=True)
        filepath = Path(folder) / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved to {filepath}")
    except Exception as e:
        error_msg = f"Error saving JSON file: {e}"
        error_detail = f"Detailed error info:\n{traceback.format_exc()}"
        print(error_msg)
        print(error_detail)
        
        # Write error information to log file
        with open('agent_search_json_save_errors.log', 'a') as f:
            f.write(f"\nTime: {datetime.datetime.now()}\n")
            f.write(f"Filename: {filename}\n")
            f.write(error_msg + '\n')
            f.write(error_detail + '\n')
            f.write('-' * 80 + '\n')

def test_new_modules(
    evolution_modules: Dict[str, ModuleInfo],
    evolution_agents: List[Agent]
) -> Dict[str, ModuleInfo]:
    """
    Test newly generated modules.
    
    Args:
        evolution_modules: New modules by type
        evolution_agents: List of evolved agents
        
    Returns:
        Test results for each module
    """
    test_results = {}
    
    # Prepare test agents, test only non-tooluse modules
    test_agents = []
    for module_type in ['planning', 'reasoning', 'memory']:
        if module_type in evolution_modules:
            test_agent = {
                'planning': 'none',
                'reasoning': 'none',
                'tooluse': 'none',
                'memory': 'none'
            }
            if module_type == 'reasoning':
                test_agent['reasoning'] = 'test'
            elif module_type == 'planning':
                test_agent['planning'] = 'test'
                test_agent['reasoning'] = 'io'
            elif module_type == 'memory':
                test_agent['memory'] = 'test'
                test_agent['reasoning'] = 'io'
            test_agents.append(test_agent)
    
    # Write test modules, only for non-tooluse modules
    for module_type, module in evolution_modules.items():
        if module_type != 'tooluse':
            write_test_module(module_type, module['code'])
    
    # Run tests in parallel
    with ProcessPoolExecutor(max_workers=len(test_agents)) as executor:
        test_futures = [executor.submit(run_benchmark, agent, 50) for agent in test_agents]
        test_performances = [future.result() for future in test_futures]
    
    # Clean up test modules
    cleanup_test_modules()
    
    # Organize test results
    for (module_type, module), performance in zip(
        [(k, v) for k, v in evolution_modules.items() if k != 'tooluse'],
        test_performances
    ):
        result = module.copy()
        result['performance'] = performance
        test_results[module_type] = result
    
    return test_results

def test_agent(agent: Agent, archives: Dict[str, List[ModuleInfo]]) -> float:
    """
    Test the performance of a single agent.
    
    Args:
        agent: Agent to test
        archives: Module archives by type
        
    Returns:
        Test performance score
    """
    # Prepare test parameters
    test_params = prepare_test_agent(agent, archives)
    
    # Run test
    measured = run_benchmark(test_params, 50)
    
    # Clean up test modules
    cleanup_test_modules()
    
    return measured

def update_tested_cases(tested_cases: List[TestedCase], agent: Agent, performance: float) -> None:
    """
    Update list of tested cases, adding the new test case.
    
    Args:
        tested_cases: List of tested cases
        agent: Agent tested
        performance: Test performance
    """
    tested_cases.append({
        **agent,
        "performance": performance
    })

def agent_search():
    """
    Implement agent search reinforcement method described in AgentSquare paper.
    
    Process:
    1. Start with initial agent
    2. Generate new agents through module evolution
    3. Test new agents on benchmark, update current agent if performance improves
    4. Generate new agents through recombination
    5. Predict performance of new agents using value model
    6. Test the best agent on benchmark, update current agent if performance improves
    7. Repeat the above steps
    """
    try:
        # Load modules
        module_data = {
            'planning': load_modules_from_json('planning_modules.json'),
            'reasoning': load_modules_from_json('reasoning_modules.json'),
            'tooluse': load_modules_from_json('tooluse_modules.json'),
            'memory': load_modules_from_json('memory_modules.json')
        }
        
        candidates = {k: v[0] for k, v in module_data.items()}
        archives = {k: v[1] for k, v in module_data.items()}
        
        # Initialize
        current_agent: Agent = {
            'planning': 'None',
            'reasoning': 'IO',
            'tooluse': 'None',
            'memory': 'None'
        }
        
        tested_cases: List[TestedCase] = [{
            'planning': 'None',
            'reasoning': 'IO',
            'tooluse': 'None',
            'memory': 'None',
            'performance': 0.56  # Initial performance
        }]
        
        current_performance = 0.56  # Initial performance
        
        # Record best performance and agent count
        best_performances = [current_performance]
        iterations = [0]
        agent_counts = [1]
        
        # Search iterations
        num_iterations = 10
        
        # Record test counts
        test_counts = {
            'total': 0,
            'iterations': []
        }
        
        for iteration in range(num_iterations):
            print(f"\n====== Iteration {iteration+1} ======")
            
            # Record test count for this iteration
            iteration_test_count = 0
            
            # 1. Module evolution phase
            print("[Module Evolution Phase]")
            evolution_results = evolution(
                current_agent,
                archives['planning'],
                archives['reasoning'],
                archives['tooluse'],
                archives['memory']
            )
            
            evolution_agents = evolution_results[0]
            evolution_modules = {
                'reasoning': evolution_results[1],
                'planning': evolution_results[2],
                'memory': evolution_results[3],
                'tooluse': evolution_results[4]
            }
            
            # 2. Test new modules
            print("[Testing New Modules]")
            test_results = test_new_modules(evolution_modules, evolution_agents)
            
            # Update candidates and archives
            for module_type, result in test_results.items():
                if result['performance'] > 0:
                    candidates[module_type][result['name']] = result['thought']
                    archives[module_type].append(result)
                    print(f"New {module_type} module {result['name']} tested successfully, performance: {result['performance']}")
                else:
                    evolution_agents = [
                        agent for agent in evolution_agents 
                        if agent[module_type] != result['name']
                    ]
                    print(f"New {module_type} module {result['name']} test failed")
            
            # Filter generated agents, exclude those using tooluse
            filtered_agents = [
                agent for agent in evolution_agents 
                if agent['tooluse'] == 'None'
            ]
            
            # 3. Test agents generated by evolution
            print("[Testing Evolved Agents]")
            evolution_test_results = []
            
            for agent in filtered_agents:
                performance = test_agent(agent, archives)
                evolution_test_results.append((agent, performance))
                update_tested_cases(tested_cases, agent, performance)
                iteration_test_count += 1
                print(f"Evolved agent test: {agent}, performance: {performance}")
            
            # Update current agent and performance (if there's a better one)
            for agent, performance in evolution_test_results:
                if performance > current_performance:
                    current_agent = agent
                    current_performance = performance
                    print(f"Found better agent through evolution: {agent}, performance: {performance}")
            
            # 4. Recombination phase
            print("[Recombination Phase]")
            recombination_agents = recombination(
                TASK_DESCRIPTION,
                current_agent,
                candidates['planning'],
                candidates['reasoning'],
                candidates['tooluse'],
                candidates['memory'],
                tested_cases
            )
            
            # Filter recombination generated agents, exclude those using tooluse
            filtered_recombination_agents = [
                agent for agent in recombination_agents 
                if agent['tooluse'] == 'None'
            ]
            
            # 5. Predict performance of recombined agents
            print("[Predicting Recombined Agent Performance]")
            predicted_scores = predict_performance(candidates, archives, filtered_recombination_agents)
            
            # Find agent with highest predicted score
            best_agent_idx = predicted_scores.index(max(predicted_scores))
            top_agent = filtered_recombination_agents[best_agent_idx]
            
            # 6. Test the best predicted agent
            print("[Testing Best Recombined Agent]")
            print(f"Predicted agent performance: {max(predicted_scores)}, configuration: {top_agent}")
            performance = test_agent(top_agent, archives)
            update_tested_cases(tested_cases, top_agent, performance)
            iteration_test_count += 1
            print(f"Actual agent performance: {performance}")
            
            # Update current agent and performance (if there's a better one)
            if performance > current_performance:
                current_agent = top_agent
                current_performance = performance
                print(f"Found better agent through recombination: {top_agent}, performance: {performance}")
            
            # Update test counts
            test_counts['total'] += iteration_test_count
            test_counts['iterations'].append(iteration_test_count)
            
            # Record iteration results
            iterations.append(iteration + 1)
            best_performances.append(current_performance)
            agent_counts.append(test_counts['total'])
            
            # Save intermediate results
            save_to_json(current_agent, f'current_agent_iteration_{iteration}.json')
            save_to_json(tested_cases, f'tested_cases_iteration_{iteration}.json')
            save_to_json(test_counts, f'test_counts_iteration_{iteration}.json')
            for module_type in MODULE_TYPES:
                save_to_json(candidates[module_type], f'{module_type}_candidates_iteration_{iteration}.json')
                save_to_json(archives[module_type], f'{module_type}_archive_iteration_{iteration}.json')
        
        # Output final results
        print("\n====== Search Complete ======")
        print(f"Best agent: {current_agent} performance: {current_performance}")
        print(f"Total test count: {test_counts['total']}")
        print(f"Test count per iteration: {test_counts['iterations']}")
        
        # Save final results
        save_to_json(current_agent, 'current_agent_final.json')
        save_to_json(tested_cases, 'tested_cases_final.json')
        save_to_json(test_counts, 'test_counts_final.json')
        for module_type in MODULE_TYPES:
            save_to_json(candidates[module_type], f'{module_type}_candidates_final.json')
            save_to_json(archives[module_type], f'{module_type}_archive_final.json')
    
    except Exception as e:
        error_msg = f"Error in agent search process: {e}"
        error_detail = f"Detailed error info:\n{traceback.format_exc()}"
        print(error_msg)
        print(error_detail)
        
        # Write error information to log file
        with open('agent_search_process_errors.log', 'a') as f:
            f.write(f"\nTime: {datetime.datetime.now()}\n")
            f.write(error_msg + '\n')
            f.write(error_detail + '\n')
            f.write('-' * 80 + '\n')

if __name__ == "__main__":
    agent_search() 