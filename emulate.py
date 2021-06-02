import json
import time
import argparse
import os
from datetime import datetime


def load_config(path: str) -> dict:
    with open(path) as json_file:
        config = json.load(json_file)

    return config


def execute_experiment(config: dict):
    n = len(config['events'])

    timeline = {}

    cleared = True
    for i in range(1, n + 1):
        event = config['events'][str(i)]
        print(f'Applying event {i}  with configuration:', event)
        start = str(datetime.now())
        cleared = apply_condition(config['interface'], event, cleared)
        end = str(datetime.now())
        timeline[str(i)] = {'start': start, 'end': end, 'duration': event['duration'], 'rules': event['rules']}

    return timeline


def apply_condition(interface: str, event: dict, is_cleared: bool):
    if event['rules'][0] == 'clear':
        condition = f'sudo tc qdisc del dev {interface} root'
        cleared = True

    else:
        if is_cleared:
            condition = f'sudo tc qdisc add dev {interface} root netem'
        else:
            os.system(f'sudo tc qdisc del dev {interface} root')
            condition = f'sudo tc qdisc add dev {interface} root netem'

        for rule in event['rules']:
            condition += ' ' + rule
        cleared = False

    os.system(condition)
    time.sleep(event['duration']/1000)

    return cleared


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Network simulation script.')

    parser.add_argument('--config', '-c', default='configs/example.json',
                        help='Config file for the simulation.')

    parser.add_argument('--output', '-o',
                        help='Optional output file that saves the timestamps of the events that might be useful for'
                             'analysis later.')

    args = parser.parse_args()

    config = load_config(args.config)

    print('Configuration file read:')
    print(config, '\n')
    timeline = execute_experiment(config)

    if args.output:
        print(f'Creating output file {args.output}')
        with open(args.output, 'w') as outfile:
            json.dump(timeline, outfile)
    else:
        print('No output file.')



