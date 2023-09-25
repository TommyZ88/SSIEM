from elasticsearch import Elasticsearch
from pandas import DataFrame

def create_agent_info_table(es: Elasticsearch):
    body = {"size": 1000} 
    res = es.search(index="wazuh-monitoring-*", body=body)
    agents = res['hits']['hits']

    table_data = []
    for agent in agents:
        source = agent["_source"]
        agent_id = source.get("id", "")

        name = source.get("name", "")
        ip = source.get("ip", "")
        status = source.get("status", "")
        
        table_data.append([agent_id, name, ip, status])

    df = DataFrame(table_data, columns=["Agent ID", "Name", "IP", "Status"])
    return df.to_html(index=False, classes='table table-striped')