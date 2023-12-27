import warnings
warnings.filterwarnings("ignore", module="urllib3")
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import yaml


class NSPClient:
    def __init__(self, config_file, verify=True):
        self.config = self.load_config(config_file)
        self.server = self.config['server']
        self.base_url = f"https://{self.server}/rest-gateway/rest/api/v1/auth/token"
        self.username = self.config['username']
        self.password = self.config['password']
        self.verify = verify

        if not self.verify:
            urllib3.disable_warnings(InsecureRequestWarning)

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def get_auth_token(self):
        url = self.base_url
        headers = {'Content-Type': 'application/json'}
        data = {"grant_type": "client_credentials"}

        response = requests.post(url, headers=headers, json=data, auth=(self.username, self.password), verify=self.verify)
        
        if response.status_code == 200:
            self.auth_token = response.json()['access_token']
            return self.auth_token
        else:
            raise Exception(f"Failed to get auth token. Status code: {response.status_code}")

    def TerminateSession(self, debug=0):
        url = f"https://{self.server}/rest-gateway/rest/api/v1/auth/revocation"
        payload = f"token={self.auth_token}&token_type_hint=token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if debug:
            print(f"{url}, {payload}, {headers}")
        response = requests.request("POST", url, headers=headers, auth=(self.username, self.password), data=payload, verify=self.verify)

        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to terminate session. Status code: {response.status_code} {response.text}")

