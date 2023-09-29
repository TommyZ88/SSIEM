from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd
from datetime import datetime

def create_top_events_donut_chart(es: Elasticsearch):
    # Define the Elasticsearch query body
    body = {
        "size": 0,
        "aggs": {
            "top_events": {
                "terms": {"field": "rule.description", "size": 5}  # Adjust the size to get the top 5 events
            }
        },
        "query": {
            "bool": {
                "must": {"match_all": {}},
                "must_not": {"term": {"agent.id": "000"}}
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['top_events']['buckets']
    
    if not buckets:
        return "No data available"
    
    # Initialize data dictionary to hold event names and counts
    data = {
        "event_name": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract event names and counts
    for bucket in buckets:
        event_name = bucket['key']
        count = bucket['doc_count']
        
        # Append the extracted data to the lists in the data dictionary
        data["event_name"].append(event_name)
        data["counts"].append(count)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a donut chart using plotly.express
    fig = px.pie(df, names='event_name', values='counts', hole=.5, 
                 title='Top 5 Events')
    
    # Return the plot as an HTML string
    return fig.to_html(full_html=False)
