#!/bin/zsh

# Function to show usage and help
show_help() {
    echo "Usage: $1 nsp-ip nsp-user nsp-pass"
    echo "Script Post LSP info in a IETF YANG JSON Format"
    echo "    nsp-ip - NSP IP Address or Hostname"
    echo "    nsp-user - NSP Username"
    echo "    nsp-pass - NSP Password"
    echo "    lsp-name - Name to use for the lsp"      
}

# Check for the correct number of arguments
if [ "$#" -ne 4 ]; then
    echo "Error: Incorrect number of arguments."
    show_help $0
    exit 1
fi

# Assign arguments to variables
NSP_IP="$1"
NSP_USER="$2"
NSP_PASS="$3"
LSP_NAME="$4"

# Main logic of the script

# obtaining token from NSP
content=$(curl -k --location -g "https://${NSP_IP}/rest-gateway/rest/api/v1/auth/token" \
-u "${NSP_USER}:${NSP_PASS}" \
--header 'Content-Type: application/json' \
--data '{
"grant_type": "client_credentials"
}') 

access_token=$(echo "$content" | awk -F'"' '{print $4}')

# Set the access token as an environment variable
NSP_TOKEN="$access_token"

echo "----\n"


# Get LSP data in IETF format
echo "Post LSP data in IETF format"

curl -k --location --globoff "https://${NSP_IP}:8545/restconf/data/ietf-te:te/tunnels" \
--header 'Accept: application/yang-data+json' \
--header 'Content-Type: application/yang-data+json' \
--header "Authorization: bearer ${NSP_TOKEN}" \
--data '{
    "tunnel": [
        {
            "name": "test02",
            "encoding": "ietf-te-types:lsp-encoding-packet",
            "admin-state": "ietf-te-types:tunnel-admin-state-up",
            "signaling-type": "ietf-te-types:path-setup-rsvp",
            "source": "1.1.1.1",
            "destination": "1.1.1.2",
            "primary-paths": {
                "primary-path": [
                    {
                        "name": "hopless",
                        "use-path-computation": "true"
                    }
                ]
            },
            "association-objects": {
                "association-object-extended": [
                    {
                        "association-key" : "nokia-path-profile-1",
                        "id": "1",
                        "extended-id" : "4F"
                    }
                ]

            }
        }
    ]
}'\
| python3 -m json.tool  

echo "----\n"



# Ending token
ending=$(curl -k --location -g "https://${NSP_IP}/rest-gateway/rest/api/v1/auth/revocation" \
  -u "${NSP_USER}:${NSP_PASS}"\
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "token=$NSP_TOKEN" \
  --data-urlencode 'token_type_hint=token') 
echo $ending



# Exit with a successful status
exit 0
