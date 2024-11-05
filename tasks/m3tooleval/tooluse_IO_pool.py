tooluse_IO_pool = {'travel': '''[1] find_flights: Finds flights based on source, destination and date. Arguments: from_location (str), to_location (str), date (str) in YYYY-MM-DD format.
Format example: 'Action: find_flights, A, B, 2023-12-25 End Action'
Returns a list of flights, each represented as a dictionary with keys "from_location", "to_location" (destination), "date", and "price".
Example: [{"from_location": "A", "to_location": "B", "date": "2023-12-25", "price": 450}]
    Signature: find_flights(destination: str, date: str) -> List[Dict]
[2] book_hotel: Books a hotel based on location and preferences. Arguments: location (str), *preferences (variable number of str arguments).
Format example: 'Action: book_hotel, B, wifi, pool End Action'
Returns a list of hotels, each represented as a dictionary with keys "location", "preferences", "price_per_night", and "rating".
Example: [{"location": "A", "preferences": ["wifi", "pool"], "price_per_night": 120, "rating": 4}]
    Signature: book_hotel(location: str, *preferences: str) -> List[Dict]
[3] budget_calculator: Calculates the total budget for a trip. Arguments: flight_price (float), hotel_price_per_night (float), num_nights (int).
Format example: 'Action: budget_calculator, 500, 100, 4 End Action'
Returns the total budget (float).
    Signature: budget_calculator(flight_price: float, hotel_price_per_night: float, num_nights: int) -> float
[4] max: Finds the maximum value among the given arguments. Accepts variable number of float arguments.
Format example: 'Action: max, 142, 174, 10 End Action'
    Signature: max(*args: float) -> float
[5] min: Finds the minimum value among the given arguments. Accepts variable number of float arguments.
Format example: 'Action: min, 101, 12, 47, 14 End Action'
    Signature: min(*args: float) -> float
[6] sum: Sums the given arguments. Accepts variable number of float arguments.
Format example: 'Action: sum, 21, 74, 70, 2, 69 End Action'
    Signature: sum(*args: float) -> float
''',
'message': '''[1] convert_hex_to_ascii: Converts a hexadecimal string to ASCII. Arguments: hex_string (str)
Format example: 'Action: convert_hex_to_ascii, 1da5d41741 End Action'
    Signature: convert_hex_to_ascii(hex_string: str) -> str
[2] reverse_string: Reverses a string. Arguments: string (str)
Format example: 'Action: reverse_string, dad4ax1a4 End Action'
    Signature: reverse_string(string: str) -> str
[3] caesar_decode: Decodes a string using the Caesar cipher. Arguments: message (str), shift (int)
Format example: 'Action: caesar_decode, sadadawfxa42, 3 End Action'
    Signature: caesar_decode(message: str, shift: int) -> str
[4] string_length: Finds the length of a string. Arguments: string (str)
Format example: 'Action: string_length, 3dad47gvnt41 End Action'
    Signature: string_length(string: str) -> int
[5] minimum_value: Finds the minimum value from given arguments. Arguments: *args (variable number of arguments)
Format example: 'Action: minimum_value, 28841, 1547, 26547 End Action'
    Signature: minimum_value(*args) -> int/float
[6] maximum_value: Finds the maximum value from given arguments. Arguments: *args (variable number of arguments)
Format example: 'Action: maximum_value, 3132, 470, 896701, 7452 End Action'
    Signature: maximum_value(*args) -> int/float
''',
'dna': '''[1] count_nucleotides: Counts the occurrences of each nucleotide in a DNA sequence. Arguments: dna_sequence (str)
Format example: 'Action: count_nucleotides, DADAINAGCAGCD End Action'
    Signature: count_nucleotides(dna_sequence: str) -> dict
[2] transcribe_dna_to_mrna: Transcribes DNA sequence to mRNA. Arguments: dna_sequence (str)
Format example: 'Action: maximum_value, DADAINAGCAGCD End Action'
    Signature: transcribe_dna_to_mrna(dna_sequence: str) -> str
[3] translate_mrna_to_amino_acid: Translates mRNA sequence to a chain of amino acids. Arguments: mrna_sequence (str)
Format example: 'Action: translate_mrna_to_amino_acid, DADAINAGCAGCD End Action'
    Signature: translate_mrna_to_amino_acid(mrna_sequence: str) -> str
[4] find_max_nucleotide: Return the nucleotide (str) with the maximum count (int). Arguments: nucleotide_counts in the form of (k1, v1, k2, v2, ..., kn, vn)
Format example: 'Action: find_max_nucleotide, A, 4, G, 1, C, 5  End Action'
    Signature: find_max_nucleotide(*args) -> (str, int)
[5] is_valid_dna_sequence: Checks if the DNA sequence is valid. Arguments: dna_sequence (str)
Format example: 'Action: is_valid_dna_sequence, DADAINAGCAGCD End Action'
    Signature: is_valid_dna_sequence(dna_sequence: str) -> bool
[6] reverse_transcribe_mrna_to_dna: Reverse transcribes mRNA sequence to DNA. Arguments: mrna_sequence (str)
Format example: 'Action: reverse_transcribe_mrna_to_dna, ADAINAGCAGCD End Action'
    Signature: reverse_transcribe_mrna_to_dna(mrna_sequence: str) -> str
''',
'trade': '''[1] convert_currency: Converts the commodity price to local currency. Arguments: base_price (float), conversion_rate (float)
Format example: 'Action: convert_currency, 100 * 10, 1.5 End Action'
    Signature: convert_currency(base_price: float, conversion_rate: float) -> float
[2] calculate_tariff: Calculates the trade tariff based on the converted price. Arguments: price (float), tariff_rate (float, in %)
Format example: 'Action: calculate_tariff, 200, 8 End Action'
    Signature: calculate_tariff(price: float, tariff_rate: float) -> float
[3] estimate_final_value: Estimates the final trade value including the tariff. Arguments: price (float), tariff (float)
Format example: 'Action: estimate_final_value, 210, 32.3  End Action'
    Signature: estimate_final_value(price: float, tariff: float) -> float
[4] calculator: Evaluates the given expression and returns the result. Accepts a calculation expression as input. For example, "2 + (3 * 4)" will return 14.
Format example: 'Action: calculator, 2 + (3 * 4) End Action'
    Signature: calculator(expression: str) -> float
[5] find_minimum: Finds the minimum value among the given arguments. Accepts variable number of float arguments.
Format example: 'Action: find_minimum, 41.2, 78, 910, 100 End Action'
    Signature: find_minimum(*args: float) -> float
[6] find_maximum: Finds the maximum value among the given arguments. Accepts variable number of float arguments.
Format example: 'Action: find_maximum, 84, 25.3, 97 End Action'
    Signature: find_maximum(*args: float) -> float
''',
'web': '''[1] click_url: Clicks on a URL. A clickable URL looks like [Clickable '<url_argument>'] in the webpage.
Arguments: url (str).
Format example: 'Action: click_url, '/example/potion/rare_potion' End Action'
Returns the rendered content of the webpage after clicking the URL showing on the current rendered page.
    Signature: click_url(url: str) -> str
[2] go_to_previous_page: Goes back to the previous page. It has no arguments.
Format example: 'Action: go_to_previous_page End Action'
After going back to the previous page, return the rendered content of the webpage.
    Signature: go_to_previous_page() -> str
[3] scroll_down: Scrolls down the view. It has no arguments.
Format example: 'Action: scroll_down End Action'
Returns the rendered content of the webpage after scrolling down.
    Signature: budget_calculator(flight_price: float, hotel_price_per_night: float, num_nights: int) -> float
[4] scroll_up: Scrolls up the view. It has no arguments.
Format example: 'Action: scroll_up End Action'
Returns the rendered content of the webpage after scrolling up.
    Signature: scroll_up() -> str
[5] view: Return the current view in string format of the rendered webpage. It has no arguments.
Format example: 'Action: view End Action'
Returns the rendered content of the webpage.
You should call this when you want to see the rendered content of the current webpage.
    Signature: view() -> str
[6] calculator: Evaluates the given expression and returns the result. Accepts a calculation expression as input. For example, "2 + (3 * 4)" will return 14.
Format example: 'Action: calculator, 2 + (3 * 4) End Action'
    Signature: calculator(expression: str) -> float
'''}
