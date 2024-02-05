#!/usr/bin/env python3


from nspMplsIp import MplsIp
import time
import sys
import argparse
import json

DEBUG = 0

def del_pathProfiles_table(nsp_instance, profileUUId, debug):
    return nsp_instance.del_pathProfiles(profileUUId, debug) 
   

def main(args):
    start = time.time()
    nsp = MplsIp("../config.yaml", verify=False)
    
                    
    if del_pathProfiles_table(nsp, args.UUID, DEBUG):
        print(f"INFO: Profile {args.UUID} has been deleted succesfully")    
    else:
        print(f"ERROR: It has been an error creating profile {args.UUID}") 
    
    nsp.nsp_instance.TerminateSession(debug=DEBUG)
    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete Profile')
    parser.add_argument('--UUID', type=str, help='Specify UUID of the Profile')

    # Add more arguments as needed
    
    args = parser.parse_args()

    if not any(vars(args).values()) or args.UUID is None:
        parser.print_help()
        sys.exit() 
     
    main(args)    
