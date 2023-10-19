from elasticsearch import Elasticsearch
from pandas import DataFrame
from datetime import datetime

def create_event_logs_table(es: Elasticsearch):
    body = generate_query_body()
    logs = fetch_event_logs(es, body)
    table_data = extract_table_data(logs)
    
    if not logs:
        table_html = create_no_data_table()
    else:
        table_html = create_data_table(table_data)
    
    return table_html


def generate_query_body():
    return {
        "size": 200,
        "query": {
            "bool": {
                "must": {"match_all": {}},
                "must_not": {"term": {"agent.id": "000"}}
            }
        },
        "sort": [{"@timestamp": "desc"}]
    }


def fetch_event_logs(es: Elasticsearch, body: dict):
    res = es.search(index="wazuh-alerts-*", body=body)
    return res['hits']['hits']


def extract_table_data(logs: list):
    table_data = []
    for log in logs:
        source = log["_source"]
        
        timestamp = source.get("@timestamp")
        if timestamp:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        
        agent_name = source.get("agent", {}).get("name", "")
        agent_ip = source.get("agent", {}).get("ip", "")
        
        table_data.append({
            "Timestamp": timestamp,
            "Agent Name": agent_name,
            "IP Address": agent_ip,
            "Event": source.get("rule", {}).get("description", ""),
            "Severity": source.get("rule", {}).get("level", "")
        })
    
    return table_data


def create_data_table(table_data: dict):
    df = DataFrame(table_data, columns=["Timestamp", "Agent Name", "IP Address", "Event", "Severity"])
    return df.to_html(index=False, classes='table table-striped')


def create_no_data_table():
    no_data_html = '''
    <style>
        .notable1-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 30vh;  
        }
        
        .notable1-image {
            width: 18%;  
        }
    </style>
    <div class="notable1-container">
        <img src="../static/images/noresults.png" alt="No Results" class="notable1-image"/>
    </div>
    '''
    return no_data_html
