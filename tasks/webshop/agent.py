
class Agent():
    def __init__(self, name, profile, MEMORY, REASONING, TOOLUSE, PLANNING, llms_type):
        self.name = name 
        self.profile = profile 
        if MEMORY is not None:
            self.memory = MEMORY(llms_type)
        else:
            self.memory = None
        if TOOLUSE is not None:
            self.tooluse = TOOLUSE(llms_type)
        else:
            self.tooluse = None
        if PLANNING is not None:
            self.planning = PLANNING(llms_type)
        else:
            self.planning = None
        self.reasoning = REASONING(self.profile, self.memory, llms_type)
