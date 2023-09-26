from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd
from datetime import datetime

def create_alerts_per_agent_line_chart(es: Elasticsearch):
    
    # Define the Elasticsearch query body
    body = {
        "size": 0,
        "aggs": {
            "events_by_type": {
                "terms": {"field": "event.type.keyword", "size": 10}
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    
    # Extract the buckets from the aggregation results
    buckets = res['aggregations']['events_by_type']['buckets']
    
    # Initialize data dictionary to hold event_types and counts
    data = {
        "event_type": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract event_type and counts
    for bucket in buckets:
        event_type = bucket['key']
        count = bucket['doc_count']
        
        # Append the extracted data to the lists in the data dictionary
        data["event_type"].append(event_type)
        data["counts"].append(count)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a bar chart using plotly.express
    fig = px.bar(df, x='event_type', y='counts', 
                 title='Number of Events by Event Type',
                 labels={'event_type': 'Event Type', 'counts': 'Number of Events'})
    
    # Return the plot as an HTML string
    return fig.to_html(full_html=False)