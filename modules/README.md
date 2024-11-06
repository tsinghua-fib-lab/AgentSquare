# Reasoning Interface

The Reasoning module is designed to handle subtasks sequentially, where each subtask and any optional feedback are provided as input to the reasoning function.  The module then produces a solution for each individual stage, supporting systematic problem-solving across multi-step tasks.

## Overview

This module is composed of two main classes:
1. **ReasoningBase**: A base class that handles task description processing, and memory management.
2. **ReasoningIO/COT/TOT/...**: The main interface class, which extends `ReasoningBase` and allows for various extensions.

## I/O
```python
class ReasoningBase:
    def __init__(self, profile_type_prompt: str, llms_type: list[str]):
        # profile_type_prompt: the role-playing prompt of large language model
        # llms_type: list of language model types, using first one

class ReasoningCOT(ReasoningBase):
    def __call__(self, task_description: str, feedback: str = ''):
        # task_description: the description of the task to be processed
        # feedback: feedback text to refine the task reasoning
        return reasoning_result
        # reasoning_result: the reasoning result of the current step
```

# Memory Interface

The Memory module is designed to dynamically store and retrieve an agent’s past thoughts, actions, and observations, enabling a context-aware reasoning process. This module allows systematic logging and retrieval of relevant memories, supporting agents in making informed decisions based on historical data.

## Overview

This module is composed of two main classes:
1. **MemoryBase**: A base class that provides basic functionality for managing memory.
2. **MemoryDILU/Generatve/...**: The main interface class, which extends `MemoryBase` and provides core functionality for managing memory, including adding and retrieving memory logs.

## I/O
```python
class MemoryDILU(MemoryBase):
    def __init__(self, llms_type: list[str]):
        # llms_type: list of language model types, using first one

    def __call__(self, current_situation: str = ''):
        # current_situation: the current situation of the task, including the trajectory of tasks to be completed or tasks already completed.
        return updated memory/retrived memory
        # updated memory: the updated memory after adding the current situation
        # retrived memory: the retrived memory of the current situation
``` 

# Planning Interface

The Planning module is responsible for decomposing complex tasks into manageable sub-tasks. It takes a high-level task description and optional feedback and generates a structured sequence of sub-tasks, each with specific reasoning and tool-use instructions. This modular approach is essential for breaking down complex, long-term tasks.

## Overview

This module is composed of two main classes:
1. **PlanningBase**: A base class that provides basic functionality for task decomposition.
2. **PlanningIO/DILU/...**: The main interface class, which extends `PlanningBase` and handles prompt creation and task decomposition.

## I/O
```python
class PlanningBase():
    def __init__(self, llms_type: list[str]):
        # llms_type: list of language model types, using first one
    
    def __call__(self, task_type: str, task_description: str, feedback: str):
        # task_type: the type of the task
        # task_description: the detailed description of the task
        # feedback: feedback text to refine the task decomposition
        return plan
        # plan: a list of dictionaries, where each dictionary contains a sub-task description, reasoning instruction, and tool-use instruction.
``` 

# ToolUse Interface

The ToolUse module enables effective use of external tools, overcoming the limitations of the LLM's internal knowledge.  During the reasoning process for each sub-task, this module selects the best-matched tool from a pre-defined tool pool to address specific problems.  This approach empowers agents to solve complex tasks by leveraging external resources.

## Overview

This module is composed of two main classes:
1. **ToolUseBase**: A base class that provides basic functionality for tool selection.
2. **ToolUseIO/ToolBench/...**: The main interface class, which extends `ToolUseBase` and handles tool selection based on task descriptions.

## I/O
```python
class ToolUseBase():
    def __init__(self, llms_type: list[str]):
        # llms_type: list of language model types, using first one

class ToolUseIO(ToolUseBase):
    def __call__(self, task_description: str, tool_instruction: str, feedback_of_previous_tools: str):
        # task_description: the detailed description of the task
        # tool_instruction: find the appropriate tool based on the tool instruction.
        # feedback_of_previous_tools: feedback text to refine the tool selection
        return tooluse_result
        # tooluse_result: the result of the tooluse module
``` 
