#!/usr/bin/env python3

import yaml
import time
import sys
import argparse
import json

#importing classes or other local functions
from insights.nspIetfKafkaListener import KafkaEventListener

def start_app(_config, _data, _debug=0):

    if config['bootstrapServers'] is not None:
        kafka_listener = KafkaEventListener(
            bootstrap_servers= config['bootstrapServers'],
            topic=config['topic'],
            partition=int(config['partition']),
            ssl_ca_location=config['sslCaLocation'],
            period=int(config['period']),
            upthreshold=int(config['upThreshold']),
            upOccurrences=int(config['upOccurrences']),
            downthreshold=int(config['downThreshold']),
            downOccurrences=int(config['downOccurrences']),   
            config = _config,
            qty= config['pathQty'],
            data = _data,
            debug = _debug
    )
    else:
        Exception("Error reading config")
    first_path = str(config['pathNamePrefix']) + "-1-" + str(int(config['groupIdFrom'])+1)
    kafka_listener.lsp_usage_consume_messages(first_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start LSP Cloning App')
    parser.add_argument('--configfile', type=str, help='Yaml file with path data')
    parser.add_argument('--debug', action='store_true', help='Activate debug mode')
    # Add more arguments as needed
    
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit() 

    if not args.configfile:
        print("ERROR: Please, specify a config file\n")
        parser.print_help()
        sys.exit()     
    start = time.time()
    debug = 1 if args.debug else 0

    try:
        with open(args.configfile, 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading path config from file: {e}")
        exit()

    if debug:
        print(f"DEBUG: Json file path: {config}")

    try:
        with open(config['pathJsonTemplate'], 'r') as file:
            data = json.load(file)
            if debug:
                print(f"DEBUG: PCC LSP JSON Template: {data}")
    except Exception as e:
        print(f"Error reading data from file: {e}")
        exit()

    start_app(config, data, debug)    
