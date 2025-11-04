def workflow(solver, env):
    if solver.planning is None:
        for i in range(1, env.max_step_number):
            task_description = env.task_description
            if solver.tooluse is not None:
                solver.tooluse(task_type = env.task_type, tool_instruction=env.tool_instruction, feedback_previous_tools = env.feedback_previous_tools)
            action = solver.reasoning(task_description=task_description, feedback='')
            observation, reward, done = env.step([action])
            print(f'Act {i}: {action}\nObs {i}: {observation}')
            if done:
                if reward == 1:
                    if solver.memory is not None:
                        memory_cache = env.memory_update()
                        solver.memory(memory_cache)
                return reward
    else:
        task_description = env.task_description
        task_type = env.task_type
        i = 0
        sub_tasks = solver.planning(task_type=task_type, task_description=task_description, feedback='')
        for sub_task_id in range(len(sub_tasks)):
            env.prompt_reset()
            try:
                prompt_exp = env.prompt_exp_update(sub_task_id)
            except:
                return 0
            init_prompt = env.init_prompt_update(sub_tasks, sub_task_id)
            for step in range(env.max_step_number_plan):
                if solver.tooluse is not None:
                    solver.tooluse(task_type = env.task_type, tool_instruction=env.tool_instruction, feedback_previous_tools = env.feedback_previous_tools)
                task_description = prompt_exp + init_prompt + env.prompt
                action = solver.reasoning(task_description=task_description, feedback='')
                observation, reward, done = env.step([action])
                print(f'Act {i}: {action}\nObs {i}: {observation}')
                i += 1
                if done:
                    if reward == 1:
                        if solver.memory is not None:
                            env.memory_cache(sub_tasks, sub_task_id)
                            for memory_cache in env.memory_pool:
                                solver.memory(memory_cache)   
                    return reward
                if env.flag(action, sub_tasks, sub_task_id):
                    env.memory_cache(sub_tasks, sub_task_id)
                    break
    return 0