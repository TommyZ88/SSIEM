from elasticsearch import Elasticsearch
from pandas import DataFrame
from datetime import datetime
import time

def create_event_logs_table(es: Elasticsearch):
    body = {
        "size": 1000,
        "query": {"match_all": {}},
        "sort": [{"@timestamp": "desc"}]
    }
    res = es.search(index="wazuh-alerts-*", body=body)
    logs = res['hits']['hits']

    table_data = []
    for log in logs:
        source = log["_source"]
        timestamp = source.get("@timestamp")
        if timestamp:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        agent_name = source.get("agent", {}).get("name", "")
        agent_ip = source.get("agent", {}).get("ip", "")
        
        table_data.append({
            "Agent Name": agent_name,
            "IP Address": agent_ip,
            "Timestamp": timestamp,
            "Event": source.get("rule", {}).get("description", ""),
            "Severity": source.get("rule", {}).get("level", "")
        })
    
    df = DataFrame(table_data, columns=["Agent Name", "IP Address","Timestamp", "Event", "Severity"])
    return df.to_html(index=False, classes='table table-striped')
