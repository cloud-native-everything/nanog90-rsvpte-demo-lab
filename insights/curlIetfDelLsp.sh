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

IFS=','
set -A LSP_NAME $4   # Set the elements into an array


# Main logic of the script
main() {
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

    for element in "${LSP_NAME[@]}"; do
        echo "processing LSP: ${element}\n"
        curl -k --location --globoff --request DELETE "https://${NSP_IP}:8545/restconf/data/ietf-te:te/tunnels/tunnel=${element}" \
        --header 'Accept: application/yang-data+json' \
        --header 'Content-Type: application/yang-data+json' \
        --header "Authorization: Bearer ${NSP_TOKEN}" \
        --data '' \
        | python3 -m json.tool  
        echo "----\n"
        sleep 1
    done





  # Ending token
  ending=$(curl -k --location -g "https://${NSP_IP}/rest-gateway/rest/api/v1/auth/revocation" \
  -u "${NSP_USER}:${NSP_PASS}"\
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "token=$NSP_TOKEN" \
  --data-urlencode 'token_type_hint=token') 
  echo $ending
}

# Execute main function
main

# Exit with a successful status
exit 0



