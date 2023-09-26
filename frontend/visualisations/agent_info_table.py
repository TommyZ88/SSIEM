from elasticsearch import Elasticsearch
from pandas import DataFrame
from datetime import datetime

def create_agent_info_table(es: Elasticsearch):
    body = {"size": 1000}
    res = es.search(index="wazuh-monitoring-*", body=body)
    agents = res['hits']['hits']

    table_data = {}
    for agent in agents:
        source = agent["_source"]
        timestamp = agent.get("_source", {}).get("timestamp")
        if timestamp:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')  # Parse the timestamp from string to datetime
        agent_id = source.get("id", "")

        # If the agent_id is not in table_data or the current agent has a newer timestamp, update the table_data entry for this agent_id.
        if agent_id not in table_data or timestamp > table_data[agent_id]["timestamp"]:
            table_data[agent_id] = {
                "name": source.get("name", ""),
                "ip": source.get("ip", ""),
                "status": source.get("status", ""),
                "timestamp": timestamp
            }

    # Create a DataFrame from the final table_data dictionary.
    df = DataFrame([(id, data['name'], data['ip'], data['status']) for id, data in table_data.items()], columns=["Agent ID", "Name", "IP", "Status"])
    return df.to_html(index=False, classes='table table-striped')
