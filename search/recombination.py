from utils import llm_response

def recombination(task_description: str, 
                 current_agent: dict[str, str],
                 planning_candidate: dict[str, str],
                 reasoning_candidate: dict[str, str], 
                 tooluse_candidate: dict[str, str],
                 memory_candidate: dict[str, str],
                 tested_case: list[dict[str, float]]) -> list[tuple[str, str, str, str]]:
    prompt = 'You are an AI agent expert. Now you are required to design a LLM-based agent to solve the task of ' \
    + task_description + 'The agent is composed of four fundamental modules(including None): planning, reasoning, tool use and memory. \
    For each module you are required to choose one from the follwing provided candidates. \
    Planning module candidates and descriptions: ' + str(planning_candidate) + ' Reasoning module candidates and descriptions: ' + str(reasoning_candidate) + ' Tool use module candidates and descriptions: ' + str(tooluse_candidate) + ' Memory module candidates and descriptions: ' + str(memory_candidate) \
    + 'The performance of some existing module combinations: ' + str(tested_case) +'. ' \
    + 'You are expected to give a new module combination to improve the performance on the task by considering (1) the matching degree between the module description and task description (2) performance of existing module combinations on the task. \
    Your answer must follow the format and not contain any other information.:' +str({'planning': '<your choice>', 'reasoning': '<your choice>', 'tooluse': '<your choice>', 'memory': '<your choice>'})
    
    model = 'gpt-4o-mini'
    response = llm_response(prompt=prompt, model=model, temperature=0.1)
    agent = eval(response)

    planning = agent['planning']
    reasoning = agent['reasoning']
    tooluse = agent['tooluse'] 
    memory = agent['memory']

    # Create 4 new agents, each replacing one module
    agent1 = {
        'planning': planning,
        'reasoning': current_agent['reasoning'],
        'tooluse': current_agent['tooluse'],
        'memory': current_agent['memory']
    }
    agent2 = {
        'planning': current_agent['planning'],
        'reasoning': reasoning,
        'tooluse': current_agent['tooluse'],
        'memory': current_agent['memory']
    }
    agent3 = {
        'planning': current_agent['planning'],
        'reasoning': current_agent['reasoning'],
        'tooluse': tooluse,
        'memory': current_agent['memory']
    }
    agent4 = {
        'planning': current_agent['planning'],
        'reasoning': current_agent['reasoning'],
        'tooluse': current_agent['tooluse'],
        'memory': memory
    }

    return [agent1, agent2, agent3, agent4]
