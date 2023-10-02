from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder

def create_top_mitre_attacks_donut_chart(es: Elasticsearch):
    # Define the Elasticsearch query body
    body = {
        "size": 0,
        "query": {
            "bool": {
                "must_not": [
                    {"term": {"agent.id": "000"}}
                ]
            }
        },
        "aggs": {
            "top_attacks": {
                "terms": {"field": "rule.mitre.id", "size": 10},  # Adjust the size to get the top N MITRE ATT&CKs
                "aggs": {
                    "attack_name": {"terms": {"field": "rule.mitre.tactic"}}
                }
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['top_attacks']['buckets']
    
    if not buckets:
        return "No data available"
    
    # Initialize data dictionary to hold attack IDs, attack names, and counts
    data = {
        "attack_id": [],
        "attack_name": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract attack IDs, attack names, and counts
    for bucket in buckets:
        attack_id = bucket['key']
        attack_name = bucket['attack_name']['buckets'][0]['key']  # Assuming there is at least one tactic per technique
        count = bucket['doc_count']
        
        # Append the extracted data to the lists in the data dictionary
        data["attack_id"].append(attack_id)
        data["attack_name"].append(attack_name)
        data["counts"].append(count)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a donut chart using plotly.express
    fig = px.pie(df, names='attack_name', values='counts', hole=.5, 
                 title='Top MITRE Attacks Techniques')
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)
