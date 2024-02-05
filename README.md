

# Automation Driven Traffic Steering (NSP LSP Cloning PCC Init App)

## Introduction

Inventive alternative with Python, involving API calls with systems like Telemetry and PCE controller, illustrated through a hands-on lab using containerlab.

Showcase an enhanced Label Switched Paths (LSP) management use case that can solve the unpredictable pattern of today’s traffic demand in WAN environments.

This app demonstrates the vital role of APIs in SDN solution like Network Service Platforms, showcasing their capability to mitigate and enhance automation gaps in Network IP technologies from diverse vendors, while affording customers the flexibility to employ their preferred programming language. 

This is part of a Tutorial presented in NANOG90, and includes two types of YANG models for the APIs and LSP definitions:
* IETF-TE YANG Model (draft-ietf-teas-yang-te-35) to define PCC Init LSPs PCE controlled. This APIs is presented via NSP using its Automation Framework.
* Nokia YANG for RSVP-TE Tunnels

We will present a solution sample of how we can provide an enhanced approach using NSP APIs and its Path Compotation features.

## Network Service Platform
Nokia NSP (Network Service Platform) is a solid platform with various applications, and one of them is the IP/MPLS Optimization app. This app provides powerful features like PCE (Path Computation Element) for managing and optimizing IP/MPLS networks efficiently. This repository focuses on developing Python applications that leverage the NSP IP/MPLS Optimization app's capabilities to create and delete multiple PCC initiated LSPs (Label Switched Paths) of the RSVP type via RESTCONF APIs and Module Driven capabilities of NSP. Those paths will be PCE controlled adding the required configurations to make this work via Path profiles defined in the MPLS/IP Optimization NSP App. Additionally, it includes applications to retrieve information and manage objects such as Path Profiles or individual LSPs using REST/RESTCONF APIs.

Note: This has been tested with the following versions
* NSP 23.11 and vSR 23.7.R1 (containerized vSR in containerlab 0.45.1)

## Installation

To use the Nokia NSP IP/MPLS Optimization Python Apps, follow these steps:

1. Clone this repository to your local machine using `git clone https://github.com/cloud-native-everything/nanog90-rsvpte-demo-lab`
2. Install the required dependencies by running(create your own virtual env is highly recommended) `pip3 install -r requirements.txt` 

## Setup
### Create and Activate Virtual Environment

First, create a virtual environment in Python to isolate the dependencies for this project and activate it:

```bash
sudo python3 -m venv .venv
source .venv/bin/activate
```
### Install requirements

After activating the virtual environment, install the required dependencies using pip:
```bash
pip3 install -r requirements.txt
```

## Config File
Before running the Python apps, you need to provide the necessary information and credentials to connect to the Nokia NSP. Create a config.yml file in the root of the project and add the following example configuration:
```yaml
server: 10.10.10.10
username: admin
password: admin123!
```
Replace the values with the actual IP address of your NSP server, the NSP username, and the corresponding password.
With the virtual environment set up and the config file in place, you are ready to run the Nokia NSP IP/MPLS Optimization Python Apps.

## Pepare Path Profile
In case you are not familiar with PCE (Path Computation Element), all LSP (Label Switched Path) Paths can be attached to a Path Profile to define optimization parameters such as enabling/disabling Disjoint, Bandwidth/Latency Thresholds, TE metrics, and more. Before creating any LSP path, you need to create a Path profile using the `nsp-postProfile.py` app.

### Creating a Path Profile
To create a Path Profile, navigate to the `res_ctrl` directory and use the `nsp-postProfile.py` app. The app works with JSON templates, and you can provide the necessary information using various switches. Here's the usage information:

```bash
cd res_ctrl
./nsp-postProfile.py 
usage: nsp-postProfile.py [-h] [--datafile DATAFILE] [--name NAME] [--objective OBJECTIVE] [--profileId PROFILEID]
                          [--maxCost MAXCOST] [--maxTeMetric MAXTEMETRIC]

Create Profile

optional arguments:
  -h, --help            show this help message and exit
  --datafile DATAFILE   File with Profile Data
  --name NAME           Overwrite Profile Name
  --objective OBJECTIVE
                        Overwrite Profile Objective
  --profileId PROFILEID
                        Overwrite Profile ID
  --maxCost MAXCOST     Overwrite MaxCost
  --maxTeMetric MAXTEMETRIC
                        Overwrite maxTeMetric
```

You can use the provided JSON template example [here](res_ctrl/profileTemplate.json). Modify the information in the template using the switches provided by the App. For example, the following command would create a Profile with ID 1002 and Name 'TestProfile-1002': `./nsp-postProfile.py --datafile profileTemplate.json --name 'TestProfile-1002' --profileId 1002`

To delete profile you will have to provide UUID. To obtain the ID you can use the App `./nsp-getResCtrl.py` as follows:

```bash
cd res_ctrl
./nsp-getResCtrl.py --profile 'name=Test'
+--------------------------------------+------------------+-----------+-----------+------------------+------------+---------+-------------+
|                 UUID                 |       name       | profileId | objective | latencyThreshold | maxLatency | maxCost | maxTeMetric |
+--------------------------------------+------------------+-----------+-----------+------------------+------------+---------+-------------+
| c145e9fa-d3fe-428b-b594-c4a0ad911cc9 | TestProfile-1002 |    1002   |    COST   |       -1.0       |    0.0     |    0    |      0      |
+--------------------------------------+------------------+-----------+-----------+------------------+------------+---------+-------------+
```

Using this id, you can delete the profile using `./nsp-delProfile.py --UUID c145e9fa-d3fe-428b-b594-c4a0ad911cc9`


## Starting the App fo Advanced LSP Cloning
<b>Important: This is still work in progress and is intended only for a demonstration of how APIs work, use it under your own risk!</b>

* The, you need to create the subcription using Insight Manager as it show on the next picture. This stat will be pull using kafka a python function.
* In order to use the kafka function, you will have to export the Kafka CA certiticate (it's located in the pod) to a PEM format. You can work it like the following:
```bash
# Those command have been used in Rocky Linux release 9.2
sudo dnf -y install keytool 
sudo dnf -y install java-11-openjdk-headless
keytool -importkeystore -srckeystore kafka.truststore.jks -srcstorepass $TRUST_PASS -srcstoretype JKS -destkeystore truststore.p12 -deststoretype PKCS12 -deststorepass $TRUST_PASS
openssl pkcs12 -in truststore.p12 -nokeys -out truststore.pem -passin pass:$TRUST_PASS
```

### How-to
To start the cloning process, you can use the following YAML file to define the necessary parameters:

```yaml
pathJsonTemplate: 'pccLspTemplate.json'
pathNamePrefix: 'pccLspCloneTest'
profileId: 10102
pathQty: 2
groupIdFrom: 60
destinationAddressIpv4: '1.1.1.2'
sourceAddressIpv4: '1.1.1.1'
sourceRouterAddressIpv4: '1.1.1.1'
bootstrapServers: '10.2.16.11:9192'  # Requires port too
topic: 'ns-eg-5715811f-3971-4890-b52d-f536e5a6c50e'
partition: '0'
sslCaLocation: 'truststore.pem'
upThreshold: '90000' # aggregate-octets-periodic
downThreshold: '1000'
```

Let's break down each element in the YAML file:
* `bootstrapServers`: Typically is the NSP IP and the port 9192
* `topic`: Topic defined in Insight Manager Subcription
* `partition`: normally is `0`
* `sslCaLocation`: location of the CA Kafka certificate
* `upThreshold`: Threshold in `aggregate-octets-periodic` will trigger an occurrence. Byt default the app is set to trigger a clone after two ocrrucences in one minute.
* `downThreshold`: Threshold in `aggregate-octets-periodic` (not working at the moment)

### Example of use

Using the same YAML file provided before, we would create the path with the commmad as follow:

```bash
./nsp-lspClone.py --configfile lspClone-config.yml 
```

You will see an outout like this:
```shell
% ./nsp-lspClone.py --configfile lspClone-config.yml 
2023-10-24 20:06:54.838455 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:04.875787 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:16.085897 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:24.891094 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:36.368772 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:45.372387 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:54.850528 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:07:54.850528 - INFO: Time Period has ended, resetting
2023-10-24 20:08:04.848652 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
```

To trigger ocurrences, you can use oam `lsp-ping` tool at the source router like this
```
A:R1# oam lsp-ping "pccLspCloneTest-1-61" send-count 60 size 9000 
LSP-PING pccLspCloneTest-1-61: 9000 bytes MPLS payload
Seq=1, send from intf to_R21, reply from 1.1.1.2
       udp-data-len=32 ttl=255 rtt=6.43ms rc=3 (EgressRtr)
Seq=2, send from intf to_R21, reply from 1.1.1.2
       udp-data-len=32 ttl=255 rtt=5.46ms rc=3 (EgressRtr)
Seq=3, send from intf to_R21, reply from 1.1.1.2
       udp-data-len=32 ttl=255 rtt=6.36ms rc=3 (EgressRtr)
Seq=4, send from intf to_R21, reply from 1.1.1.2
       udp-data-len=32 ttl=255 rtt=4.47ms rc=3 (EgressRtr)
Seq=5, send from intf to_R21, reply from 1.1.1.2
       udp-data-len=32 ttl=255 rtt=4.92ms rc=3 (EgressRtr)
Seq=6, send from intf to_R21, reply from 1.1.1.2
       udp-data-len=32 ttl=255 rtt=5.20ms rc=3 (EgressRtr)
```

And then, you should see an exit like this:
```
2023-10-24 20:10:04.893348 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 63154 (Under upThreshold)
2023-10-24 20:10:04.893348 - INFO: Time Period has ended, resetting
2023-10-24 20:10:14.851723 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 90220 (Over upThreshold)
2023-10-24 20:10:24.837238 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 90220 (Over upThreshold)
2023-10-24 20:10:34.833330 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 90220 (Over upThreshold)
2023-10-24 20:10:45.401250 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 90220 (Over upThreshold)
2023-10-24 20:10:54.869227 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 90220 (Over upThreshold)
2023-10-24 20:11:04.849553 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 27066 (Under upThreshold)
2023-10-24 20:11:15.161633 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
2023-10-24 20:11:15.161633 - INFO: Time Period has ended, resetting
2023-10-24 20:11:15.161633 - INFO: Threshold exceeded more than 2 times in the last 1 minutes! Triggering event...
2023-10-24 20:11:15.161842 - INFO: Event triggered. LSP Clone started!
2023-10-24 20:11:16.835697 - INFO: LSP Path pccLspCloneTest-1-61 already exists
2023-10-24 20:11:17.248318 - INFO: LSP Path pccLspCloneTest-2-61 already exists
2023-10-24 20:11:17.444215 - INFO: LSP Path pccLspCloneTest-3-62 has been created succesfully
2023-10-24 20:11:24.919714 - INFO: aggregate-octets-periodic at pccLspCloneTest-1-61: 0 (Under upThreshold)
```

Do not forget hit a star. Don't hesitate to contact me if you need help.
## What's next
The following are only proposals for next steps. Let us know if you want to collaborate.


# Disclaimer

**Note:** The code and information provided in this repository are for educational and informational purposes only. By using any code, scripts, or information from this repository, you agree that:

1. **No Warranty**: The code is provided "as is" without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. 

2. **No Liability**: In no event shall the author(s) or the employer(s) be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services, loss of use, data, or profits, or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.

3. **Use at Your Own Risk**: The use of code and information from this repository is entirely at your own risk. You are solely responsible for any technical or financial consequences that may result from using this code.

4. **Compliance**: You are responsible for ensuring that your use of the code complies with all relevant laws, regulations, and ethical standards.

5. **No Support**: The author(s) and the employer(s) are not obligated to provide any support or assistance related to the code or its usage.

Please exercise caution and due diligence when using the code and information provided in this repository. Always thoroughly review and test any code before using it in production environments. This disclaimer is subject to change without notice. By using the code and information in this repository, you acknowledge and agree to this disclaimer.

If you do not agree with this disclaimer, do not use the code or information provided in this repository.