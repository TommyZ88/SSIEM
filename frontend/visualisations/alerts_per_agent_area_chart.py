from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd
from datetime import datetime

def create_alerts_per_agent_area_chart(es: Elasticsearch):
    # Define the Elasticsearch query body for aggregating alerts by agent and timestamp
    body = {
        "size": 0,
        "aggs": {
            "alerts_over_time": {
                "date_histogram": {"field": "@timestamp", "fixed_interval": "1h"},
                "aggs": {
                    "agent_names": {"terms": {"field": "agent.name", "size": 5}}
                }
            }
        },
        "query": {
            "bool": {
                "must": {"match_all": {}},
                "must_not": {"term": {"agent.id": "000"}}
            }
        }
    }
    
    # Execute the search query on the Elasticsearch index "wazuh-alerts-*"
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['alerts_over_time']['buckets']
    
    if not buckets:
        return "No data available"
    
    # Initialize data list to hold timestamps, agent names, and counts
    data = []
    
    # Iterate through each bucket and extract timestamps, agent names, and counts
    for bucket in buckets:
        timestamp = bucket['key_as_string']
        for agent_bucket in bucket['agent_names']['buckets']:
            agent_name = agent_bucket['key']
            count = agent_bucket['doc_count']
            
            # Append the extracted data to the data list
            data.append({
                "Timestamp": datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'),
                "Agent Name": agent_name,
                "Alert Count": count
            })
    
    # Convert the data list to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a curved area chart using plotly.express
    fig = px.area(df, x='Timestamp', y='Alert Count', color='Agent Name', line_shape='spline',
                  title='Number of Alerts Per Agent Over Time')
    
    # Return the plot as an HTML string
    return fig.to_html(full_html=False)