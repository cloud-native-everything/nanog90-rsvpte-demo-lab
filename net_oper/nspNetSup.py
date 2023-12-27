import warnings
warnings.filterwarnings("ignore", module="urllib3")
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import requests
from nspcommon import NSPClient
import json


class NetSup:
    def __init__(self, config_file, verify=False):
        self.nsp_instance = NSPClient(config_file,verify)
        self.auth_token = self.nsp_instance.get_auth_token()
        if not verify:
            urllib3.disable_warnings(InsecureRequestWarning)    
    def _get_data_from_endpoint(self, endpoint,debug):
        url = f"https://{self.nsp_instance.server}:8545/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-type': 'application/json'
        }
        if debug:
            print(f"DEBUG: Endpoint:\n{url}\nDEBUG: Headers:\n{headers}")
        response = requests.get(url, headers=headers, verify=self.nsp_instance.verify)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: \"{response.status_code}\" \"{response.text}\"")
        
    def _get_yang_from_endpoint(self, endpoint, debug=0):
        url = f"https://{self.nsp_instance.server}:8545/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'
        }
        if debug:
            print(f"DEBUG: Endpoint:\n{url}\nDEBUG: Headers:\n{headers}")
        response = requests.get(url, headers=headers, verify=self.nsp_instance.verify)

        if response.status_code == 200:
            return response.json()

        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: {response.status_code} {response.text}")        
        

    def _post_data_to_endpoint(self, endpoint, data, debug=0):
        url = f"https://{self.nsp_instance.server}:8545/{endpoint}"

        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-type': 'application/json'
        }
        payload = json.dumps(data)
        if debug:
            print(f"DEBUG: Endpoint:\n{url}\nDEBUG: Headers:\n{headers}\nDEBUG: Payload:\n{headers}")
        response = requests.post(url, headers=headers, verify=self.nsp_instance.verify, data=payload)

        if response.status_code in [200, 201, 204]:
            if debug: 
                print(f"DEBUG: Status code: {response.status_code}\nDEBUG: Response Text: {response.text}")
            return 200
        elif "Data already exists" in response.text:
            if debug: 
                print(f"DEBUG: Status code: {response.status_code}\nDEBUG: Response Text: {response.text}")
            return 300             
        elif "Exclusive datastore access unavailable" in response.text:
            raise Exception(f"Device is in configuration mode from other place. Access has been blocked")         
        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: {response.status_code} {response.text}")
        

    def _del_data_to_endpoint(self, endpoint, debug=0):
        url = f"https://{self.nsp_instance.server}:8545/{endpoint}"

        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-type': 'application/json'
        }
        if debug:
            print(f"DEBUG: Endpoint:\n{url}\nDEBUG: Headers:\n{headers}")
        response = requests.delete(url, headers=headers, verify=self.nsp_instance.verify, data='')

        if response.status_code in [200, 201, 204]:
            if debug: 
                print(f"DEBUG: Status code: {response.status_code}\nDEBUG: Response Text: {response.text}")
            return 200    
        elif "Data missing" or "Entry does not exist" in response.text:
            if debug: 
                print(f"DEBUG: Status code: {response.status_code}\nDEBUG: Response Text: {response.text}")
            return 300               
        elif "Exclusive datastore access unavailable" in response.text:
            raise Exception(f"Device is in configuration mode from other place. Access has been blocked")    
        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: {response.status_code} {response.text}")

    def get_networkElements(self,debug=0):
        netelements = self._get_data_from_endpoint("restconf/data/nsp-equipment:network/network-element",debug)
        if 'nsp-equipment:network-element' in netelements:
            return netelements['nsp-equipment:network-element']
        else:
            raise Exception(f"Failed to retrieve \'nsp-equipment:network-element\'")

    def get_pcc(self, neId, debug):
        return self._get_yang_from_endpoint(f"restconf/data/network-device-mgr:network-devices/network-device={neId}/root/nokia-conf:/configure/router/pcep",debug)
    
    def get_lsp(self, neId, debug):
        return self._get_yang_from_endpoint(f"restconf/data/network-device-mgr:network-devices/network-device={neId}/root/nokia-conf:/configure/router=Base/mpls/lsp",debug)
    
    def post_lsp(self, neId, data, debug):
        return self._post_data_to_endpoint(f"restconf/data/network-device-mgr:network-devices/network-device={neId}/root/nokia-conf:/configure/router=Base/mpls",data,debug)
    
    def del_lsp(self, neId, lspName, debug):
        return self._del_data_to_endpoint(f"restconf/data/network-device-mgr:/network-devices/network-device={neId}/root/nokia-conf:/configure/router=Base/mpls/lsp={lspName}",debug)
    
    def get_router_info(self, neId, debug):
        return self._get_yang_from_endpoint(f"restconf/data/network-device-mgr:network-devices/network-device={neId}/root/nokia-conf:/configure/router=Base",debug)



