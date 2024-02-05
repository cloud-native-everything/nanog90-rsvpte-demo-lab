#!/bin/zsh

# Function to show usage and help
show_help() {
    echo "Usage: $1 nsp-ip nsp-user nsp-pass"
    echo "Script to upload YANG and Intent structured"
    echo "    nsp-ip - NSP IP Address or Hostname"
    echo "    nsp-user - NSP Username"
    echo "    nsp-pass - NSP Password"    
    echo "    Converter Intent Mapping Path i.e. ./converter-inetent-mapping" 
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
PATH_TO_CONVERTED_INTENT_MAPPING="$4"

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

  # Getting Intent mapping file to server
  ## Note: you have to import intents in advanced
  echo "Getting Intent mapping file to server"

  curl -k -X GET "https://${NSP_IP}:8545/restconf/operations/nsp-yang-mapping-converter:nsp-yang-mapping-converter" \
  --header 'Content-Type: application/json' \
  --header "Authorization: bearer ${NSP_TOKEN}" \
    | python3 -m json.tool 
  echo "----\n"

  # Ending token
  ending=$(curl -k --location -g "https://${NSP_IP}/rest-gateway/rest/api/v1/auth/revocation" \
  -u "${NSP_USER}:${NSP_PASS}" \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "token=$NSP_TOKEN" \
  --data-urlencode 'token_type_hint=token')
  echo $ending
}

# Execute main function
main

# Exit with a successful status
exit 0