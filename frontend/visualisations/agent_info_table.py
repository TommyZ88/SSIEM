from elasticsearch import Elasticsearch
from pandas import DataFrame
from datetime import datetime


def create_agent_info_table(es: Elasticsearch):
    body = {
        "size": 10,
        "query": {
            "bool": {
                "must_not": [
                    {"term": {"id": "000"}}
                ]
            }
        }
    }
    agents = fetch_agent_data(es, body)
    table_data = extract_table_data(agents)
    
    if not agents:
        table_html = create_no_data_table()
    else:
        table_html = create_data_table(table_data)
    
    return table_html


def fetch_agent_data(es: Elasticsearch, body: dict):
    res = es.search(index="wazuh-monitoring-*", body=body)
    return res['hits']['hits']


def extract_table_data(agents: list):
    table_data = {}
    for agent in agents:
        source = agent["_source"]
        timestamp = agent.get("_source", {}).get("timestamp")
        if timestamp:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        agent_id = source.get("id", "")
        
        if agent_id not in table_data or (timestamp and timestamp > table_data[agent_id]["timestamp"]):
            table_data[agent_id] = {
                "name": source.get("name", ""),
                "ip": source.get("ip", ""),
                "status": source.get("status", ""),
                "timestamp": timestamp
            }
    
    return table_data


def create_data_table(table_data: dict):
    df = DataFrame([(id, data['name'], data['ip'], data['status']) for id, data in table_data.items()], columns=["Agent ID", "Name", "IP", "Status"])
    return df.to_html(index=False, classes='table table-striped')


def create_no_data_table():
    no_data_html = '''
    <style>
        .notable-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 30vh;  
        }
        
        .notable-image {
            width: 18%;  
        }
    </style>
    <div class="notable-container">
        <img src="../static/images/noresults.png" alt="No Results" class="notable-image"/>
    </div>
    '''
    return no_data_html
