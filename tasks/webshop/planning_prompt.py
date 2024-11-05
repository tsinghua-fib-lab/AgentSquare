
planning_prompt = {"online_shopping": '''I would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
sub-task 1: {{'description': 'I first need to do a search to find items that might qualify.', 'reasoning instruction': 'Search based on attributes other than price.', 'tool use instruction': None}}
sub-task 2: {{'description': 'Then I need to find the most suitable item in the item list.', 'reasoning instruction': 'Find the most qualified item in the item list.', 'tool use instruction': None}}
sub-task 3: {{'description': 'Finally, I need to click the attributes of the selected item and decide to buy it.', 'reasoning instruction': 'Click the attributes of the selected item and  buy it.', 'tool use instruction': None}}'''
}
                   
