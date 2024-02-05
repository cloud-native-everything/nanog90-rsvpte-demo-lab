#!/bin/zsh

# Function to show usage and help
show_help() {
    echo "Usage: $1 nsp-ip nsp-user nsp-pass"
    echo "Script to upload YANG and Intent structured"
    echo "    nsp-ip - NSP IP Address or Hostname"
    echo "    nsp-user - NSP Username"
    echo "    nsp-pass - NSP Password"    
    echo "    Converter Mapping Path i.e. ./converter-mapping" 
    echo "    Converter Intent Mapping Path i.e. ./converter-inetent-mapping" 
}

# Check for the correct number of arguments
if [ "$#" -ne 5 ]; then
    echo "Error: Incorrect number of arguments."
    show_help $0
    exit 1
fi

# Assign arguments to variables
NSP_IP="$1"
NSP_USER="$2"
NSP_PASS="$3"
PATH_TO_CONVERTED_MAPPING="$4"
PATH_TO_CONVERTED_INTENT_MAPPING="$5"

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

  ## Upload MD Converter mapping files to server
  echo "Uploading MD Converter mapping files to server"

  curl -k -X POST "https://${NSP_IP}:8545/restconf/operations/nsp-yang-mapping-converter:nsp-yang-mapping-converter/uploadFile?nsp-plugin-id=yang" \
  --header 'Accept: application/json' \
  --header "Authorization: bearer ${NSP_TOKEN}" \
  --form 'file="'@${PATH_TO_CONVERTED_MAPPING}'/common/commonMapping.json"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/common/GlobalQosHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/common/SiteTrackingHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/common/SvcTrackingHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMCommonMapping.json"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMMapping.json"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMSitePostProcessing.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMSvcPostProcessing.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMTunnelBindingHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMTunnelBindingTrackingHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMEpPostProcessing.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l2nm/L2NMEpTrackingHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3NMMapping.json"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3VpnBgpPeerHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3VpnEpPostProcessing.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3NMEpTrackingHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3VpnIpHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3VpnStaticRouteHandler.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3VpnSitePostProcessing.java"' \
  --form 'file=@"'${PATH_TO_CONVERTED_MAPPING}'/l3nm/L3VpnSvcPostProcessing.java"'

  echo "----\n"

  # Upload Intent mapping file to server
  ## Note: you have to import intents in advanced
  echo "Uploading Intent mapping file to server"

  curl -k -X POST "https://${NSP_IP}:8545/restconf/operations/nsp-yang-mapping-converter:nsp-yang-mapping-converter/uploadFile?nsp-plugin-id=intent" \
  --header 'Accept: application/json' \
  --header "Authorization: bearer ${NSP_TOKEN}" \
  --form "file=@${PATH_TO_CONVERTED_INTENT_MAPPING}/IntentMapping.json"
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
