#!/bin/bash

# Start Docker Compose For Windows Devices
docker-compose -f Docker_Compose.yml up -d

# Loop until the Elasticsearch container is detected as running
while true; do
    # Check if the Elasticsearch container is running
    if docker ps | grep -q 'elasticsearch'; then
        # Execute the Elasticsearch script
        echo "Waiting for Elasticsearch to initialise"
        sleep 30
        ./setup/windows-elasticsearch.sh
        break
    else
        sleep 10
    fi
done

# Loop until the Wazuh container is detected as running
while true; do
    # Check if the Wazuh container is running
    if docker ps | grep -q 'wazuh'; then
        # Execute the Wazuh script
        echo "Waiting for Wazuh to initialise"
        sleep 30
        ./setup/wazuh.sh
        break
    else
        sleep 10
    fi
done

