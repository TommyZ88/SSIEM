#!/bin/bash

echo "
Copying the rules file..."
docker cp ./setup/custom_rules.xml wazuh:/var/ossec/etc/rules/

sleep 5

echo "
Restarting wazuh manager..."
docker exec -it wazuh service wazuh-manager restart


