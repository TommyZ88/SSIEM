from elasticsearch import Elasticsearch
from pandas import DataFrame
from datetime import datetime

def create_event_logs_table(es: Elasticsearch):
    # Define the search query to retrieve 1000 log entries, sorted by timestamp in descending order
    body = {
        "size": 1000,
        "query": {
            "bool": {
                "must": {"match_all": {}},
                "must_not": {"term": {"agent.id": "000"}}
            }
        },
        "sort": [{"@timestamp": "desc"}]
    }
    
    # Execute the search query on the Elasticsearch index "wazuh-alerts-*"
    res = es.search(index="wazuh-alerts-*", body=body)
    
    # Extract the log entries from the search results
    logs = res['hits']['hits']

    table_data = []
    # Iterate over each log entry to extract relevant information
    for log in logs:
        source = log["_source"]
        
        # Parse the timestamp into a datetime object, if available
        timestamp = source.get("@timestamp")
        if timestamp:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Extract agent name and IP address from the log entry
        agent_name = source.get("agent", {}).get("name", "")
        agent_ip = source.get("agent", {}).get("ip", "")
        
        # Append the extracted information to the table_data list
        table_data.append({
            "Timestamp": timestamp,
            "Agent Name": agent_name,
            "IP Address": agent_ip,
            "Event": source.get("rule", {}).get("description", ""),
            "Severity": source.get("rule", {}).get("level", "")
        })
    
    # Convert the table_data list to a DataFrame and then to an HTML table
    df = DataFrame(table_data, columns=["Timestamp", "Agent Name", "IP Address", "Event", "Severity"])
    return df.to_html(index=False, classes='table table-striped')
