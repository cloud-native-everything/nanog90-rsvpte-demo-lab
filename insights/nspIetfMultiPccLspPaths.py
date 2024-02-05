from datetime import datetime

## Import Classes
from net_oper.nspIetfNetSup import NetSup

# Constants
CONN_FILE = "config.yaml"

def int_to_hex_string(integer_value):
    # Convert the integer to a hexadecimal string
    hex_string = hex(integer_value)[2:]  # [2:] is used to remove the '0x' prefix

    # Convert the hexadecimal string to uppercase for standard formatting
    return hex_string.upper()

def _multiLspMgmt_create(path_config, data, Qty, debug):


    if path_config['destinationAddressIpv4'] is not None:
        data['tunnel'][0]['destination'] = path_config['destinationAddressIpv4']
    if path_config['sourceAddressIpv4'] is not None:
        data['tunnel'][0]['source'] = path_config['sourceAddressIpv4']  

    nsp = NetSup(CONN_FILE, verify=False)    

    current_lsps = nsp.get_lsp(debug)["ietf-te:tunnels"]
    if debug:
        print(f"DEBUG: LSP got by lsp_get: {current_lsps}")
    filtered_lsp_names = [entry['name'] for entry in current_lsps['tunnel'] if entry['name'].startswith(path_config['pathNamePrefix'])]
    if debug:
        print(f"{datetime.now()} - DEBUG: filtered_lsp_names = f{filtered_lsp_names}")
    pathQty = len(filtered_lsp_names)
    if pathQty > Qty:
        nsp.nsp_instance.TerminateSession(debug)
        if debug:
            print(f"{datetime.now()} - DEBUG: Submitted Qty= {Qty}; Function Returns Detected Qty = {pathQty}")
        return pathQty
    if debug:
        print(f"{datetime.now()} - DEBUG: Submitted Qty= {Qty}; Detected Qty = {pathQty}")

    pathQty = pathQty + 1
    if debug:
        print(f"{datetime.now()} - DEBUG: Increasing current pathQty to {pathQty}")    


    if path_config['profileId'] is not None:
        data['tunnel'][0]['association-objects']['association-object-extended'][0]['id'] = int(path_config['profileId'])          
    if path_config['pathNamePrefix'] is not None:
        if pathQty % 2 == 0:
            data['tunnel'][0]['name'] = path_config['pathNamePrefix'] + "-" + str(pathQty) + "-" + str(int(path_config['groupIdFrom']) + pathQty // 2)    
            data['tunnel'][0]['association-objects']['association-object-extended'][0]['extended-id'] = int_to_hex_string(int(path_config['groupIdFrom']) + pathQty // 2)
        else:
            data['tunnel'][0]['name'] = path_config['pathNamePrefix'] + "-" + str(pathQty) + "-" + str(int(path_config['groupIdFrom']) + pathQty // 2 + 1)         
            data['tunnel'][0]['association-objects']['association-object-extended'][0]['extended-id']  = int_to_hex_string(int(path_config['groupIdFrom']) + pathQty // 2 + 1)
    else:
        print(f"{datetime.now()} - FATAL ERROR: defining path name {path_config['pathNamePrefix']+str(pathQty)}")
        exit(1)   
            
    post_response = nsp.post_lsp(data, debug)
    if post_response in [200]:
        print(f"{datetime.now()} - INFO: LSP Path {data['tunnel'][0]['name']} has been created succesfully")    
    elif post_response in [300]:     
        print(f"{datetime.now()} - INFO: LSP Path {data['tunnel'][0]['name']} already exists")                  
    else:
        print(f"{datetime.now()} - FATAL ERROR: It has been an error creating LSAP Path {data['tunnel'][0]['name']}")
        exit(1)

    if debug:
            print(f"{datetime.now()} - DEBUG: Function Returns pathQty+1 = {pathQty}")       
    nsp.nsp_instance.TerminateSession(debug)
    return pathQty
    

def _multiLspMgmt_delete(path_config, data, Qty, debug):

    if path_config['destinationAddressIpv4'] is not None:
        data['tunnel'][0]['destination'] = path_config['destinationAddressIpv4']
    if path_config['sourceAddressIpv4'] is not None:
        data['tunnel'][0]['source'] = path_config['sourceAddressIpv4']    

    nsp = NetSup(CONN_FILE, verify=False)    

    current_lsps = nsp.get_lsp(debug)["ietf-te:tunnels"]
    filtered_lsp_names = [entry['name'] for entry in current_lsps['tunnel'] if entry['name'].startswith(path_config['pathNamePrefix'])]
    if debug:
        print(f"{datetime.now()} - DEBUG: filtered_lsp_names = f{filtered_lsp_names}")
    pathQty = max(len(filtered_lsp_names), Qty)  
    if debug:
        print(f"{datetime.now()} - DEBUG: Submitted Qty= {Qty}; Detected Qty = {pathQty}")

    if path_config['profileId'] is not None:
        data['tunnel'][0]['association-objects']['association-object-extended'][0]['id'] = int(path_config['profileId'])
    if path_config['pathNamePrefix'] is not None:    
        data['tunnel'][0]['name'] = path_config['pathNamePrefix'] + "-" + str(pathQty) + "-" + str(int(path_config['groupIdFrom']) + (pathQty-1) // 2 + 1)
    else:
        print(f"{datetime.now()} - FATAL ERROR: defining path name {path_config['pathNamePrefix']+str(pathQty)}")
        exit(1)        
 
    del_response = nsp.del_lsp(data['tunnel'][0]['name'], debug)
    if del_response in [200]:
        print(f"{datetime.now()} - INFO: LSP Path {data['tunnel'][0]['name']} has been deleted succesfully")   
    elif del_response in [300]:
        print(f"{datetime.now()} - INFO: LSP Path {data['tunnel'][0]['name']} is no longer there")                    
    else:
        print(f"{datetime.now()} - FATAL ERROR: It has been an error deleting LSAP Path {data['tunnel'][0]['name']}")
        exit(1)
    nsp.nsp_instance.TerminateSession(debug)    
    return pathQty-1




