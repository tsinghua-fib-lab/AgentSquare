import re
from utils import llm_response

class REASONING_SELFREFINE():
    def __init__(self, profile_type_prompt, memory, tooluse, llms_type):
        self.feedback = ''
        self.profile_type_prompt = profile_type_prompt
        self.memory = memory
        self.llm_type = llms_type[0]
        self.tooluse = tooluse
        self.task_name_cache = None
    def __call__(self, task_description: str, tool_instruction :str='', feedback :str= ''):
        task_name = re.findall(r'Your task is to:\s*(.*?)\s*>', task_description)        
        if self.memory is not None:
            if self.task_name_cache is not None and self.task_name_cache == task_name:
                pass
            else:
                self.task_name_cache = task_name
                self.memory_cache = self.memory(task_description)
        else:
            self.memory_cache = ''
        if self.tooluse is not None:
            tooluse = self.tooluse(task_description, tool_instruction)
        else:
            tooluse = ''
        split_text = task_description.rsplit('You are in the', 1)
        examples = split_text[0]
        task_description = 'You are in the' + split_text[1]
        prompt = '''Solve the task step by step. Interact with a household to solve a task. Your instructions must follow the examples.{tooluse}
Here are some examples.
{examples}{memory}
Here is the task:
{task_description}'''
        prompt = prompt.format(task_description=task_description, examples=examples, memory=self.memory_cache, tooluse=tooluse)
        reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
        reasoning_result = self.refine(reasoning_result)
        return reasoning_result
    def refine(self, reasoning_result):
        if 'think' in reasoning_result:
            return reasoning_result
        prompt = f'''You need to check that the syntactic structure of the step meets the requirements.
requirements: '1. take a from b 2. go to a 3. : open a 4. put a in/on b, end. 5. clean a with b, end. 6. heat a with b, end. 7. cool a with b, end. 8. use a, end.', where 'a' and 'b' are variable.
examples：
take pencil 1 from desk 2   correct
take potato 1 with fridge 1 error, The preposition with take is from. revised: take potato 1 from bridge 1
go to cabinet 3   correct
go to countertop 2 and check   error, go to countertop 2 is the complete instruction. revised: go to countertop 2
open fridge 1 and take potato 2   error, open fridge 1 is the complete instruction. revised: open fridge 1
open safe 2   correct
put mug 2 in desk 1, end   error, The preposition with put is in/on. revised: put mug 2 in/on desk 1, end
put watch 1 in/on safe 1, end   correct
clean soapbar 1 with sinkbasin 1   error, Add "end" to the clean statement. revised: clean soapbar 1 with sinkbasin 1, end
clean lettuce 4 with sinkbasin 1, end   correct
heat egg 2 with microwave 1, end   correct
heat bread 1 with stoveburner 1, end   error, microwave is what you use to heat. revised: heat bread 1 with microwave 1, end
cool potato 2 with fridge 1, end   correct
cool pan 1, end   error,  bridge is whta you ues to cool. revised: cool pan 1 with bridge 1, end
use desklamp 3 to check statue 2   error, use desklamp3 is the complete instruction. revised: use desklamp 3, end
use desklamp 2, end   correct
Just focus on syntactic structure.
step: {reasoning_result}
You can only output in two formats:
"correct" or "error, revised: your step"
'''     

        #print(prompt)
        feedback_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.0)
        print(f'feedback_result :{feedback_result }')
        if 'correct' in feedback_result.lower():
            if ' in ' in reasoning_result:
                reasoning_result = reasoning_result.replace(' in ', ' in/on ')
            elif ' on ' in reasoning_result:
                reasoning_result = reasoning_result.replace(' on ', ' in/on ')
            return reasoning_result.replace('.', '')
        else:
            if ' in ' in feedback_result:
                feedback_result = feedback_result.replace(' in ', ' in/on ')
            elif ' on ' in feedback_result:
                feedback_result = feedback_result.replace(' on ', ' in/on ')
            return feedback_result.split(':')[-1].replace('.', '').strip()
#         print(f'feedback_result :{feedback_result }')
#         if 'correct' in feedback_result.lower():
#             return reasoning_result
#         else:
#             prompt = f'''Interact with a household to solve a task. Your instructions should follow the examples.
# Here are some examples.
# {examples}{self.memory_cache}
# Here is the task:
# Your recnt aenswer: {reasoning_result} , feedack: {feedback_result}
# {task_description}'''
#             reasoning_result = llm_response(prompt=prompt, model=self.llm_type, temperature=0.1, stop_strs=['\n'])
#             return reasoning_result
        
  


#         prompt = f'''You need to check that the syntactic structure of the step meets the requirements.
# requirements: '1. take a from b 2. go to a 3. : open a 4. put a in/on b, end. 5. clean a with b, end. 6. heat a with b, end. 7. cool a with b, end. 8. use a, end.', where 'a' and 'b' are variable.
# examples：
# take pencil 1 from desk 2   correct
# take potato 1 with fridge 1 error, revised: take potato 1 from bridge 1
# go to cabinet 3   correct
# go to countertop 2 and check   error, revised: go to countertop 2
# open fridge 1 and take potato 2   error, revised: open fridge 1
# open safe 2   correct
# put mug 2 in desk 1, end   error, revised: put mug 2 in/on desk 1, end
# put watch 1 in/on safe 1, end   correct
# clean soapbar 1 with sinkbasin 1   error, revised: clean soapbar 1 with sinkbasin 1, end
# clean lettuce 4 with sinkbasin 1, end   correct
# heat egg 2 with microwave 1, end   correct
# heat bread 1 with stoveburner 1, end   error, revised: heat bread 1 with microwave 1, end
# cool potato 2 with fridge 1, end   correct
# cool pan 1, end   error, revised: cool pan 1 with bridge 1, end
# use desklamp 3 to check statue 2   error, revised: use desklamp 3, end
# use desklamp 2, end   correct

# step: {reasoning_result}
# You can only output in two formats:
# "correct" or "error, revised:"
# '''     


#         prompt = f'''The output of the step is only in the following syntactic formats:
# syntactic formats: '1. take a from b 2. go to a 3. : open a 4. put a in/on b, end. 5. clean a with b, end. 6. heat a with b, end. 7. cool a with b, end. 8. use a, end.', where 'a' and 'b' are variable.
# Some correct and false examples：
# take pencil 1 from desk 2   correct
# take potato 1 with fridge 1 false, revised: take potato 1 from bridge 1
# go to cabinet 3   correct
# go to countertop 2 and check   false, revised: go to countertop 2
# open fridge 1 and take potato 2   false, revised: open fridge 1
# open safe 2   correct
# put mug 2 in desk 1, end   false, revised: put mug 2 in/on desk 1, end
# put watch 1 in/on safe 1, end   correct
# clean soapbar 1 with sinkbasin 1   false, revised: clean soapbar 1 with sinkbasin 1, end
# clean lettuce 4 with sinkbasin 1, end   correct
# heat egg 2 with microwave 1, end   correct
# heat bread 1 with stoveburner 1, end   false, revised: heat bread 1 with microwave 1, end
# cool potato 2 with fridge 1, end   correct
# cool pan 1, end   false, revised: cool pan 1 with bridge 1, end
# use desklamp 3   false, revised: use desklamp 3, end
# use desklamp 2, end   correct

# step: {reasoning_result}
# You can only output in two formats:
# "correct" or "false, revised:"
# '''   


#         prompt = f'''You need to check that the syntactic structure of the step meets the requirements.
# requirements: '1. take a from b 2. go to a 3. : open a 4. put a in/on b, end. 5. clean a with b, end. 6. heat a with b, end. 7. cool a with b, end. 8. use a, end.', where 'a' and 'b' are variable.
# Do not easily revise the variables given.
# examples：
# take pencil 1 from desk 2   correct
# take potato 1 with fridge 1 error, revised: take potato 1 from bridge 1
# go to cabinet 3   correct
# open safe 2   correct
# put mug 2 in desk 1, end   error, revised: put mug 2 in/on desk 1, end
# put watch 1 in/on safe 1, end   correct
# clean soapbar 1 with sinkbasin 1   error, revised: clean soapbar 1 with sinkbasin 1, end
# clean lettuce 4 with sinkbasin 1, end   correct
# heat egg 2 with microwave 1, end   correct
# heat bread 1 with microwave, end   error, revised: heat bread 1 with microwave 1, end
# cool potato 2 with fridge 1, end   correct
# cool pan 1 with fridge 1   error, revised: cool pan 1 with bridge 1, end
# use desklamp 2, end   correct

# step: {reasoning_result}
# You can only output in two formats:
# "correct" or "error, revised:"
# '''     