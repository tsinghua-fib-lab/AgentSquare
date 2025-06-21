import importlib
import sys
try:
    importlib.reload(sys.modules['reasoning_modules'])
    from reasoning_modules import *
except KeyError:
    # 如果reasoning_modules模块尚未加载，则直接导入
    from reasoning_modules import *

try:
    importlib.reload(sys.modules['planning_modules'])
    from planning_modules import *
except KeyError:
    # 如果planning_modules模块尚未加载，则直接导入
    from planning_modules import *

try:
    importlib.reload(sys.modules['memory_modules'])
    from memory_modules import *
except KeyError:
    # 如果memory_modules模块尚未加载，则直接导入
    from memory_modules import *

try:
    importlib.reload(sys.modules['tooluse_modules'])
    from tooluse_modules import *
except KeyError:
    # 如果tooluse_modules模块尚未加载，则直接导入
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
        'test': PlanningTest,
    }
    reasoning_map = {
        'io': ReasoningIO,
        'cot': ReasoningCOT,
        'cot-sc': ReasoningCOTSC,
        'tot': ReasoningTOT,
        'self-refine': ReasoningSelfRefine,
        'dilu': ReasoningDILU,
        'stepback': ReasoningStepBack,
        'sf-tot': ReasoningSelfReflectiveTOT,
        'test': ReasoningTest,
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
        'test': MemoryTest,
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
