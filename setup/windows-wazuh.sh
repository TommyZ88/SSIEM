#!/bin/bash

echo "
Copying the rules file..."
winpty docker cp ./setup/custom_rules.xml wazuh:/var/ossec/etc/rules/

sleep 5

echo "
Restarting wazuh manager..."
winpty docker exec -it wazuh service wazuh-manager restart


