#!/usr/bin/env python3

from nspMplsIp import MplsIp
import time
import sys
import argparse
import json

DEBUG = 0

def post_pathProfiles_table(nsp_instance, data, debug):
    return nsp_instance.post_pathProfiles(data, debug) 
   

def main(args):
    start = time.time()
    nsp = MplsIp("../config.yaml", verify=False)

    try:
        with open(args.datafile, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error reading data from file: {e}")
        exit()
    
    if args.name is not None:
        data['data']['name'] = args.name
    if args.objective is not None:
        data['data']['objective'] = args.objective
    if args.profileId is not None:
        data['data']['profileId'] = args.profileId
    if args.maxCost is not None:
        data['data']['maxCost'] = args.maxCost
    if args.maxTeMetric is not None:
        data['data']['maxTeMetric'] = args.maxTeMetric                        
    

    if post_pathProfiles_table(nsp, data, DEBUG):
        print(f"INFO: Profile {data['data']['name']} has been created succesfully")    
    else:
        print(f"ERROR: It has been an error creating profile {data['data']['name']}") 
    
    nsp.nsp_instance.TerminateSession(debug=DEBUG)
    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Profile')
    parser.add_argument('--datafile', type=str, help='File with Profile Data')
    parser.add_argument('--name', type=str, help='Overwrite Profile Name')
    parser.add_argument('--objective', type=str, help='Overwrite Profile Objective')
    parser.add_argument('--profileId', type=str, help='Overwrite Profile ID')
    parser.add_argument('--maxCost', type=str, help='Overwrite MaxCost')
    parser.add_argument('--maxTeMetric', type=str, help='Overwrite maxTeMetric')

    # Add more arguments as needed
    
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit() 

    if not args.datafile:
        print("ERROR: Please, specify a data file\n")
        parser.print_help()
        sys.exit()         
    main(args)    
