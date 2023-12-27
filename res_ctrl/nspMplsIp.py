import warnings
warnings.filterwarnings("ignore", module="urllib3")
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import requests
from nspcommon import NSPClient
import json


class nspNode:
    def __init__(self, data):
        #print(data['nodeId']['uri']['string'])
        self.nodeId = data['nodeId']['uri']['string']
        terminationPoint = [(data['terminationPoint'][item]) for item in data['terminationPoint']]
        self.terminationPoint =  [(nspTerminationPoint(item)) for item in terminationPoint] 
        self.nspNode = data['nspNode']

class nspTerminationPoint:
    def __init__(self, data):
        #print(data['nspTerminationPoint']['terminationPointState']['terminationPointParams']['tpId']['ipAddress']['ipv4Address']['string'])
        self.tpId = data['tpId']['uri']['string']
        self.routerIpAddress = data['nspTerminationPoint']['terminationPointState']['terminationPointParams']['routerIpAddress']
        try:
            self.tpIpv4 = data['nspTerminationPoint']['terminationPointState']['terminationPointParams']['tpId']['ipAddress']['ipv4Address']['string']
        except TypeError:
            self.tpIpv4 = 'Undefined'    
        try:
            self.remoteTpIpv4 = data['nspTerminationPoint']['terminationPointState']['terminationPointParams']['remoteTpId']['ipAddress']['ipv4Address']['string']
        except TypeError:
            self.remoteTpIpv4 = 'Undefined'    
        try:
            self.nonIpProtocol = data['nspTerminationPoint']['terminationPointState']['terminationPointParams']['nonIpProtocol']
        except TypeError:
            self.nonIpProtocol = 'Nope'
        try:
            self.areaIds = data['nspTerminationPoint']['terminationPointState']['terminationPointParams']['areaIds']
        except TypeError:
            self.areaIds = 'Undefined'                   

class nspNetwork:
    def __init__(self, data):
        self.networkId = data['networkId']['uri']['string']
        self.links = [(data['link'][item]) for item in data['link']]
        data_node = [(data['node'][item]) for item in data['node']]
        self.nodes = [(nspNode(item)) for item in data_node]

    
class MplsIp:
    def __init__(self, config_file, verify=True):
        self.nsp_instance = NSPClient(config_file,verify)
        self.auth_token = self.nsp_instance.get_auth_token()
        if not verify:
            urllib3.disable_warnings(InsecureRequestWarning)    

    def _get_data_from_endpoint(self, endpoint):
        url = f"https://{self.nsp_instance.server}:8543/sdn/api/v4/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-type': 'application/json'
        }
        print(url,headers)
        response = requests.get(url, headers=headers, verify=self.nsp_instance.verify)

        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'data' in data['response']:
                return data['response']['data']
        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: {response.status_code} {response.text}")
        

    def _post_data_to_endpoint(self, endpoint, data, debug):
        url = f"https://{self.nsp_instance.server}:8543/sdn/api/v4/{endpoint}"

        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-type': 'application/json'
        }
        payload = json.dumps(data)
        if debug:
            print(url,headers, payload)
        response = requests.post(url, headers=headers, verify=self.nsp_instance.verify, data=payload)

        if response.status_code == 200:
            print("Object has been created successfully")
            if debug: 
                print(f"DEBUG: Status code: {response.status_code}\nDEBUG: Response Text: {response.text}")
            return 1    
        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: {response.status_code} {response.text}")
        

    def _del_data_to_endpoint(self, endpoint, debug):
        url = f"https://{self.nsp_instance.server}:8543/sdn/api/v4/{endpoint}"

        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-type': 'application/json'
        }
        
        response = requests.delete(url, headers=headers, verify=self.nsp_instance.verify)

        if response.status_code == 200:
            print("Object has been deleted successfully")
            if debug: 
                print(f"DEBUG: Status code: {response.status_code}\nDEBUG: Response Text: {response.text}")
            return 1    
        else:
            raise Exception(f"Failed to retrieve {endpoint}. Status code: {response.status_code} {response.text}")


    def get_lspPaths(self, filter):
        if not filter:
            return self._get_data_from_endpoint("mpls/lsp-paths")
        if filter == '*':
            return self._get_data_from_endpoint("mpls/lsp-paths")
        else:
            return self._get_data_from_endpoint(f"mpls/lsp-paths?{filter}")

    def get_lsps(self, filter):
        if not filter:
            return self._get_data_from_endpoint("mpls/lsps")
        if filter == '*':
            return self._get_data_from_endpoint("mpls/lsps")
        else:
            return self._get_data_from_endpoint(f"mpls/lsps?{filter}")
    
    def get_pathProfiles(self, filter):
        if not filter:
            return self._get_data_from_endpoint("template/path-profiles")
        if filter == '*':
            return self._get_data_from_endpoint("template/path-profiles")
        else:
            return self._get_data_from_endpoint(f"template/path-profiles?{filter}")        

    def get_links(self):
        return self._get_data_from_endpoint("nsp/net/l3/networks")
       
        

    def post_pathProfiles(self, data, debug):
        return self._post_data_to_endpoint("template/path-profiles", data, debug)
    
    def post_lspPath(self, data, debug):
        return self._post_data_to_endpoint("mpls/lsp-path", data, debug)

    def del_pathProfiles(self, profile, debug):
        return self._del_data_to_endpoint(f"template/path-profiles/{profile}", debug)

    def del_lspPath(self, lspPath, debug):
        return self._del_data_to_endpoint(f"mpls/lsp-path/{lspPath}", debug)    
