from reasoning_modules import *
from planning_modules import *
from memory_modules import *
from tooluse_modules import *
def ModuleMap(planning=None, reasoning=None, tooluse=None, memory=None):
    planning_map = {
        'none': None,
        'io': PlanningIO,
        'hugginggpt': PlanningHUGGINGGPT,
        'openagi': PlanningOPENAGI,
        'voyage': PlanningVoyager,
        'td': PlanningTD,
        'deps': PlanningDEPS,
    }
    reasoning_map = {
        'io': ReasoningIO,
        'cot': ReasoningCOT,
        'cot-sc': ReasoningCOTSC,
        'tot': ReasoningTOT,
        'self-refine': ReasoningSelfRefine,
        'dilu': ReasoningDILU,
        'stepback': ReasoningStepBack,
        'sf-tot': ReasoningSelfReflectiveTOT
    }
    tooluse_map = {
        'none': None,
    }
    memory_map = {
        'none': None,
        'dilu': MemoryDILU,
        'voyage': MemoryVoyager, 
        'tp': MemoryTP,
        'generative': MemoryGenerative,
    }
    if planning.lower() in planning_map:
        planning_module  = planning_map[planning.lower()]
    else:
        raise KeyError("No corresponding planning module was found")
    if reasoning.lower() in reasoning_map:
        reasoning_module = reasoning_map[reasoning.lower()]
    else:
        raise KeyError("No corresponding reasoning module was found")
    if tooluse.lower() in tooluse_map:
        tooluse_module = tooluse_map[tooluse.lower()]
    else:
        raise KeyError("No corresponding tooluse module was found")
    if memory.lower() in memory_map:
        memory_module = memory_map[memory.lower()]
    else:
        raise KeyError("No corresponding memory module was found")
    return planning_module, reasoning_module, tooluse_module, memory_module
