#!/usr/bin/env python3

## Importing Modules
from prettytable import PrettyTable
import time
import sys
import argparse
import json

## Importing Classes
from nspMplsIp import MplsIp
from nspMplsIp import nspNetwork


## Some Constants
DEBUG = 0

def get_pathProfiles_table(nsp_instance, filter,debug):
    table = PrettyTable(['UUID','name', 'profileId', 'objective', 'latencyThreshold', 'maxLatency','maxCost','maxTeMetric'])
    data = nsp_instance.get_pathProfiles(filter,debug)

    if DEBUG:
        formatted_data = json.dumps(data, indent=2)
        print(formatted_data)


    for item in data:
        UUID = item.get('id', '')
        name = item.get('name', '')
        profileId = item.get('profileId', '')
        objective = item.get('objective', '')
        latencyThreshold = item.get('latencyThreshold', '')
        maxLatency = item.get('maxLatency', '')
        maxCost = item.get('maxCost', '')
        maxTeMetric = item.get('maxTeMetric', '')
        table.add_row([UUID, name, profileId, objective, latencyThreshold, maxLatency,maxCost,maxTeMetric])        
    print(table)

def get_lspPaths_table(nsp_instance, filter,debug):
    table = PrettyTable(['UUID', 'Name', 'Tunnel ID', 'Type', 'Bandwidth', 'Latency'])
    data = nsp_instance.get_lspPaths(filter,debug)
   
    if DEBUG:
        formatted_data = json.dumps(data, indent=2)
        print(formatted_data)

    for item in data:
        UUID = item.get('pathId', '')
        name = item.get('pathName', '')
        id = item.get('tunnelId', '')
        type = item.get('pathType', '')
        bandwidth = item.get('measuredBandwidth', '')
        latency = item.get('latency', '')
        table.add_row([UUID, name, id, type, bandwidth, latency])     
    print(table)
   
def get_lsps_table(nsp_instance, filter,debug):
    table = PrettyTable(['UUID', 'lspName', 'tunnelId', 'measuredBandwidth'])
    data = nsp_instance.get_lsps(filter,debug)

    if DEBUG:
        formatted_data = json.dumps(data, indent=2)
        print(formatted_data) 

    for item in data:
        UUID = item.get('lspId', '')
        lspName = item.get('lspName', '')
        tunnelId = item.get('tunnelId', '')
        measuredBandwidth = item.get('measuredBandwidth', '')   
        table.add_row([UUID, lspName, tunnelId, measuredBandwidth])
    print(table)

def get_links_table(nsp_instance,debug):
    
    data = nsp_instance.get_links(debug)
    if DEBUG:
        formatted_data = json.dumps(data, indent=2)
        print(formatted_data) 

    nspNetworks = []
    for item in data['network']:
        nspNetworks.append(nspNetwork(data['network'][item]))

    for item in nspNetworks:
        print(f"\n>> NetworkId: {item.networkId}\n")
        table = PrettyTable([ 'name', 'trafficEngineering','adminStatus','maxResvLinkBandwidth', 'measuredMplsIpBw','latency','igpMetric'])
        for item2 in item.links:
            #linkId = item2.get('linkId', {}).get('uri',{}).get('string','')
            name_original = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('name','')
            index_of_arrow = name_original.find('=>')
            substring = name_original[index_of_arrow + 2:]
            name = substring.replace('-PointToPoint-Original', '')
            trafficEngineering = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('trafficEngineering','')
            adminStatus = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('adminStatus','')
            maxResvLinkBandwidth = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('maxResvLinkBandwidth','')
            measuredMplsIpBw = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('measuredMplsIpBw','')
            latency = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('latency','')
            igpMetric = item2.get('nspLink',{}).get('linkState',{}).get('linkParams',{}).get('igpMetric','')
            table.add_row([ name, trafficEngineering, adminStatus, maxResvLinkBandwidth, measuredMplsIpBw, latency, igpMetric])    
        print(table)   


def get_nspTp_table(nsp_instance,debug):
    
    data = nsp_instance.get_links(debug)
    if DEBUG:
        formatted_data = json.dumps(data, indent=2)
        print(formatted_data) 

    nspNetworks = []
    for item in data['network']:
        nspNetworks.append(nspNetwork(data['network'][item]))


    for item in nspNetworks:
        print(f"\n>> NetworkId: {item.networkId}\n")
        table = PrettyTable(['routerIpAddress', 'terminationPointIpv4', 'nonIpProtocol', 'areaIds'])
        prev_iprouter = None  # Store the previous iprouter to check for changes
        for item2 in item.nodes:
            routerIpAddress = [item3.routerIpAddress for item3 in item2.terminationPoint]
            terminationPointIpv4 = [item3.tpIpv4 for item3 in item2.terminationPoint]
            nonIpProtocol = [item3.nonIpProtocol if item3.nonIpProtocol is not None else 'Undefined' for item3 in item2.terminationPoint]
            areaIds = [item3.areaIds for item3 in item2.terminationPoint]

            # Make sure terminationPointIpv4, nonIpProtocol, and routerIpAddress have the same length
            num_rows = max(len(terminationPointIpv4), len(nonIpProtocol), len(routerIpAddress), len(areaIds))
            terminationPointIpv4 += [''] * (num_rows - len(terminationPointIpv4))
            nonIpProtocol += [''] * (num_rows - len(nonIpProtocol))
            routerIpAddress += [''] * (num_rows - len(routerIpAddress))
            areaIds += [''] * (num_rows - len(areaIds))

            # Sort based on iprouter (routerIpAddress)
            sorted_data = sorted(zip(routerIpAddress, terminationPointIpv4, nonIpProtocol, areaIds), key=lambda x: x[0])

            # Add sorted rows to the table with separator rows between different iprouter values
            for idx, (iprouter, tp_ipv4, non_ip_protocol, area) in enumerate(sorted_data):
                if prev_iprouter is not None and iprouter != prev_iprouter:
                    # Add a separator row with separator characters
                    table.add_row(['-' * len("routerIpAddress"), '-' * len("terminationPointIpv4"), '-' * len("nonIpProtocol"), '-' * len("areaIds")])
                table.add_row([iprouter, tp_ipv4, non_ip_protocol,area])
                prev_iprouter = iprouter

        print(table)



def main(args):
    start = time.time()
    nsp = MplsIp("../config.yaml", verify=False)
    
    debug=DEBUG

    if args.lsp:
        get_lsps_table(nsp, args.lsp,debug)
    elif args.path:
        get_lspPaths_table(nsp, args.path,debug)
    elif args.profile:
        get_pathProfiles_table(nsp, args.profile,debug)    
    elif args.link:
        get_links_table(nsp,debug)    
    elif args.node:
        get_nspTp_table(nsp,debug)                       
    
    nsp.nsp_instance.TerminateSession(debug=DEBUG)
    end = time.time()
    float_format = '{0:.2F}'
    print(f'Total time: {float_format.format(end - start)} seconds')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Path Control and Optimization. Example: python3 nsp-resCtrl.py --profile \'name=def\'')
    parser.add_argument('--lsp', type=str, help='Filter by LSP Path Fields like \'lspName=test\' or \'tunnelId=1\'')
    parser.add_argument('--path', type=str, help='Filter by LSP Path Fields like \'pathName=test\' or \'pathType=SRTE\'')
    parser.add_argument('--profile', type=str, help='Filter by Profile fields like \'name=\'')
    parser.add_argument('--link', action='store_true', help='Display all Links (no filter available)')
    parser.add_argument('--node', action='store_true', help='Display all Nodes (no filter available)')
    # Add more arguments as needed
    
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit() 

    main(args)    
