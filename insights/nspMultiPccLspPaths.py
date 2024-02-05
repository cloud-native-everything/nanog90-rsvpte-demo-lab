from datetime import datetime

## Import Classes
from net_oper.nspNetSup import NetSup

# Constants
CONN_FILE = "config.yaml"
    
def _multiLspMgmt_create(path_config, data, Qty, debug):


    if path_config['destinationAddressIpv4'] is not None:
        data['nokia-conf:lsp']['to'] = path_config['destinationAddressIpv4']
    if path_config['sourceAddressIpv4'] is not None:
        data['nokia-conf:lsp']['from'] = path_config['sourceAddressIpv4']
    if path_config['sourceRouterAddressIpv4'] is not None:
        neId = path_config['sourceRouterAddressIpv4']      

    nsp = NetSup(CONN_FILE, verify=False)    

    current_lsps = nsp.get_lsp(neId, debug)
    filtered_lsp_names = [entry['lsp-name'] for entry in current_lsps['nokia-conf:lsp'] if entry['lsp-name'].startswith(path_config['pathNamePrefix'])]
    if debug:
        print(f"{datetime.now()} - DEBUG: filtered_lsp_names = f{filtered_lsp_names}")
    pathQty = max(len(filtered_lsp_names), Qty)  
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
        data['nokia-conf:lsp']['path-profile']['profile-id'] = int(path_config['profileId'])          
    if path_config['pathNamePrefix'] is not None:
        if pathQty % 2 == 0:
            data['nokia-conf:lsp']['lsp-name'] = path_config['pathNamePrefix'] + "-" + str(pathQty) + "-" + str(int(path_config['groupIdFrom']) + pathQty // 2)    
            data['nokia-conf:lsp']['path-profile']['path-group'] = int(path_config['groupIdFrom']) + pathQty // 2
        else:
            data['nokia-conf:lsp']['lsp-name'] = path_config['pathNamePrefix'] + "-" + str(pathQty) + "-" + str(int(path_config['groupIdFrom']) + pathQty // 2 + 1)         
            data['nokia-conf:lsp']['path-profile']['path-group']  = int(path_config['groupIdFrom']) + pathQty // 2 + 1          
    else:
        print(f"{datetime.now()} - FATAL ERROR: defining path name {path_config['pathNamePrefix']+str(pathQty)}")
        exit(1)   
            
    post_response = nsp.post_lsp(neId, data, debug)
    if post_response in [200]:
        print(f"{datetime.now()} - INFO: LSP Path {data['nokia-conf:lsp']['lsp-name']} has been created succesfully")    
    elif post_response in [300]:     
        print(f"{datetime.now()} - INFO: LSP Path {data['nokia-conf:lsp']['lsp-name']} already exists")                  
    else:
        print(f"{datetime.now()} - FATAL ERROR: It has been an error creating LSAP Path {data['nokia-conf:lsp']['lsp-name']}")
        exit(1)

    if debug:
            print(f"{datetime.now()} - DEBUG: Function Returns pathQty+1 = {pathQty}")       
    nsp.nsp_instance.TerminateSession(debug)
    return pathQty
    

def _multiLspMgmt_delete(path_config, data, Qty, debug):


    if path_config['destinationAddressIpv4'] is not None:
        data['nokia-conf:lsp']['to'] = path_config['destinationAddressIpv4']
    if path_config['sourceAddressIpv4'] is not None:
        data['nokia-conf:lsp']['from'] = path_config['sourceAddressIpv4']
    if path_config['sourceRouterAddressIpv4'] is not None:
        neId = path_config['sourceRouterAddressIpv4']      

    nsp = NetSup(CONN_FILE, verify=False)    

    current_lsps = nsp.get_lsp(neId, debug)
    filtered_lsp_names = [entry['lsp-name'] for entry in current_lsps['nokia-conf:lsp'] if entry['lsp-name'].startswith(path_config['pathNamePrefix'])]
    if debug:
        print(f"{datetime.now()} - DEBUG: filtered_lsp_names = f{filtered_lsp_names}")
    pathQty = max(len(filtered_lsp_names), Qty)  
    if debug:
        print(f"{datetime.now()} - DEBUG: Submitted Qty= {Qty}; Detected Qty = {pathQty}")

    if path_config['profileId'] is not None:
        data['nokia-conf:lsp']['path-profile']['profile-id'] = int(path_config['profileId'])
    if path_config['pathNamePrefix'] is not None:    
        data['nokia-conf:lsp']['lsp-name'] = path_config['pathNamePrefix'] + "-" + str(pathQty) + "-" + str(int(path_config['groupIdFrom']) + (pathQty-1) // 2 + 1)
    else:
        print(f"{datetime.now()} - FATAL ERROR: defining path name {path_config['pathNamePrefix']+str(pathQty)}")
        exit(1)        
 
    del_response = nsp.del_lsp(neId, data['nokia-conf:lsp']['lsp-name'], debug)
    if del_response in [200]:
        print(f"{datetime.now()} - INFO: LSP Path {data['nokia-conf:lsp']['lsp-name']} has been deleted succesfully")   
    elif del_response in [300]:
        print(f"{datetime.now()} - INFO: LSP Path {data['nokia-conf:lsp']['lsp-name']} is no longer there")                    
    else:
        print(f"{datetime.now()} - FATAL ERROR: It has been an error deleting LSAP Path {data['nokia-conf:lsp']['lsp-name']}")
        exit(1)
    nsp.nsp_instance.TerminateSession(debug)    
    return pathQty-1




