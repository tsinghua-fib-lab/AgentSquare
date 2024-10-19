import sys
import importlib
import argparse
def run(planning=None, reasoning=None, tooluse=None, memory=None, llms_type=['gpt=3.5-turbo-instruct']):
    sys.argv = [
        'main.py',
        '--output_dir', 'outputs/travel_itinerary_planning',
        '--task_regex_filter', 'travel_itinerary_planning.*',
        '--n_turns_limit', '10',
        '--model', ','.join(llms_type),
        '--planning', planning,
        '--reasoning', reasoning,
        '--memory', memory,
        '--tooluse', tooluse,
        '--task_name', 'travel',
    ]
    import main
    correct_travel, total_travel, price_travel = main.run_m3tool()
    sys.argv = [
        'main.py',
        '--output_dir', 'outputs/message_decoder',
        '--task_regex_filter', 'message_decoder.*',
        '--n_turns_limit', '10',
        '--model', ','.join(llms_type),
        '--planning', planning,
        '--reasoning', reasoning,
        '--memory', memory,
        '--tooluse', tooluse,
        '--task_name', 'message',
    ]
    importlib.reload(main)
    correct_message, total_message, price_message = main.run_m3tool()
    sys.argv = [
        'main.py',
        '--output_dir', 'outputs/dna_sequencer',
        '--task_regex_filter', 'dna_sequencer.*',
        '--n_turns_limit', '10',
        '--model', ','.join(llms_type),
        '--planning', planning,
        '--reasoning', reasoning,
        '--memory', memory,
        '--tooluse', tooluse,
        '--task_name', 'dna',
    ]
    importlib.reload(main)
    correct_dna, total_dna, price_dna = main.run_m3tool()
    sys.argv = [
        'main.py',
        '--output_dir', 'outputs/trade_calculator',
        '--task_regex_filter', 'trade_calculator.*',
        '--n_turns_limit', '10',
        '--model', ','.join(llms_type),
        '--planning', planning,
        '--reasoning', reasoning,
        '--memory', memory,
        '--tooluse', tooluse,
        '--task_name', 'trade',
    ]
    importlib.reload(main)
    correct_trade, total_trade, price_trade = main.run_m3tool()
    sys.argv = [
        'main.py',
        '--output_dir', 'outputs/web_browsing',
        '--task_regex_filter', 'web_browsing.*',
        '--n_turns_limit', '10',
        '--model', ','.join(llms_type),
        '--planning', planning,
        '--reasoning', reasoning,
        '--memory', memory,
        '--tooluse', tooluse,
        '--task_name', 'web',
    ]
    importlib.reload(main)
    correct_web, total_web, price_web = main.run_m3tool()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ALFWorld with specified modules.')
    parser.add_argument('--planning', type=str, default='none', help='Specify planning module')
    parser.add_argument('--reasoning', type=str, default='io', help='Specify reasoning module')
    parser.add_argument('--tooluse', type=str, default='none', help='tooluse is not required in ALFworld')
    parser.add_argument('--memory', type=str, default='none', help='Specify memory module')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo-0125', help='Specify the LLM model type')
    args = parser.parse_args()
    run(
        planning=args.planning,
        reasoning=args.reasoning,
        tooluse=args.tooluse,
        memory=args.memory,
        llms_type=[args.model]
    )

