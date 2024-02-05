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
        
    def _get_yang_from_endpoint(self, endpoint, debug=0):
        url = f"https://{self.nsp_instance.server}:8545/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Accept': 'application/yang-data+json',
            'Content-Type': 'application/yang-data+json'
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
            'Accept': 'application/yang-data+json',
            'Content-Type': 'application/yang-data+json'
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
            'Accept': 'application/yang-data+json',
            'Content-Type': 'application/yang-data+json'
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
    
    def get_lsp(self, debug):
        return self._get_yang_from_endpoint(f"restconf/data/ietf-te:te/tunnels",debug)
    
    def post_lsp(self, data, debug):
        return self._post_data_to_endpoint(f"restconf/data/ietf-te:te/tunnels",data,debug)
    
    def del_lsp(self, lspName, debug):
        return self._del_data_to_endpoint(f"restconf/data/ietf-te:te/tunnels/tunnel={lspName}",debug)
    


