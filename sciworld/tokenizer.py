import tiktoken

messages = [{"role": "system", "content": ''},{"role": "user", "content": 'The goal is to satisfy the following conditions: shot1 contains cocktail1. \nObservation: Cocktail1 part1 ingredient is ingredient1. Cocktail1 part2 ingredient is ingredient3. Cocktail2 part1 ingredient is ingredient2. Cocktail2 part2 ingredient is ingredient3. Cocktail3 part1 ingredient is ingredient1. Cocktail3 part2 ingredient is ingredient2. Dispenser1 dispenses ingredient1. Dispenser2 dispenses ingredient2. Dispenser3 dispenses ingredient3. Left hand is empty. Level l0 is next to level l1. Level l1 is next to level l2. Right hand is empty. Shaker1 is at empty level l0. Shaker1 is at level l0. Shaker1 is clean. Shaker1 is empty. Shaker1 is on the table. Shot1 is clean. Shot1 is empty. Shot1 is on the table. Shot2 is clean. Shot2 is empty. Shot2 is on the table. Shot3 is clean. Shot3 is empty. Shot3 is on the table. Shot4 is clean. Shot4 is empty. Shot4 is on the table.\nAction: check valid actions\nObservation: Valid actions are: right grasp shot1. , left grasp shot3. , left grasp shot1. , left grasp shot2. , right grasp shaker1. , right grasp shot4. , right grasp shot3. , right grasp shot2. , left grasp shaker1. , left grasp shot4. , check valid actions\nAction: right grasp shot1.\nObservation: You are holding right.\nAction: fill-shot glass shot1 with ingredient3 with right and left holding dispenser3\nObservation: Shot1 contains ingredient3. \nAction: check valid actions\nObservation: Valid actions are: pour-shot-to-clean-shaker from a shot glass shot1 with ingredient3 to a clean shaker shaker1 with hand right from level l0 to level l1, left grasp shot3. , left grasp shot2. , use hand right to empty-shot glass shot1 with beverage ingredient3. , right leave shot1. , left grasp shaker1. , left grasp shot4. , check valid actions\nAction: pour-shot-to-clean-shaker from a shot glass shot1 with ingredient3 to a clean shaker shaker1 with hand right from level l0 to level l1\nObservation:  Pour shot1 from a shot glass to a used shaker ingredient3 Shaker1 contains ingredient3. \nAction: clean-shot glass shot1 with ingredient3 with hand right holding shot glass and left\nObservation:  Shot1 is clean. \nAction: fill-shot glass shot1 with ingredient1 with right and left holding dispenser1\nObservation: Shot1 contains ingredient1.\nAction: pour-shot-to-used-shaker from a shot glass shot1 with ingredient1 to a used shaker shaker1 with hand right from level l1 to level l2\nObservation: Pour shot1 from a shot glass to a used shaker ingredient1 Shaker1 contains ingredient1. Shaker1 contains ingredient3. Shaker1 is at empty level l0. Shaker1 is at level l2. Shaker1 is on the table. Shaker1 is unshaked.\nAction: clean-shot glass shot1 with ingredient1 with hand right holding shot glass and left\nObservation: Shot1 is clean. \nAction: right leave shot1\nObservation: Right hand is empty.\nAction: right grasp shaker1\nObservation: You are holding right.\nAction: shake a cocktail cocktail1 with ingredient ingredient1 and ingredient ingredient3 in a shaker shaker1 with hand right and hand left\nObservation: Shaker1 is shaked.\nAction: pour-shaker-to-shot to a shot glass cocktail1 the ingredient shot1 with hand right from shaker shaker1 from level l2 to level l1\nObservation: Shot1 contains cocktail1. The task is completed.'}]

model = "gpt-3.5-turbo-0613"
try:
    encoding = tiktoken.encoding_for_model(model)
except KeyError:
    print("Warning: model not found. Using cl100k_base encoding.")
    encoding = tiktoken.get_encoding("cl100k_base")
        
tokens_per_message = 0
tokens_per_name = 0
if model in {
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4-0314",
    "gpt-4-32k-0314",
    "gpt-4-0613",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo-0125",
    }:
    tokens_per_message = 3
    tokens_per_name = 1
    
num_tokens = 0 
for message in messages:
    num_tokens += tokens_per_message
    for key, value in message.items():
        num_tokens += len(encoding.encode(value))
        if key == "name":
            num_tokens += tokens_per_name
num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
print(num_tokens)
