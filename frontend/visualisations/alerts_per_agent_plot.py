from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd

def create_alerts_per_agent_plot(es: Elasticsearch):
    # Define the Elasticsearch query body
    # It includes aggregations to group data by agent.id and further group by dates
    body = {
        "size": 0,  # We set the size to 0 as we are interested in aggregation results only
        "aggs": {
            "alerts_per_agent": {
                "terms": {"field": "agent.id.keyword"},  # Grouping by agent.id
                "aggs": {
                    "alerts_over_time": {
                        "date_histogram": {"field": "@timestamp", "calendar_interval": "day"}  # Further grouping by dates
                    }
                }
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    
    # Extract the buckets from the aggregation results
    buckets = res['aggregations']['alerts_per_agent']['buckets']
    
    # Initialize data dictionary to hold agent_id, dates, and counts
    data = {
        "agent_id": [],
        "dates": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract agent_id, dates, and counts
    for bucket in buckets:
        agent_id = bucket['key']  # The key of the bucket is the agent_id
        dates = [item['key_as_string'] for item in bucket['alerts_over_time']['buckets']]  # Extract dates from nested buckets
        counts = [item['doc_count'] for item in bucket['alerts_over_time']['buckets']]  # Extract document count for each nested bucket
        
        # Extend the lists in the data dictionary with the extracted data
        data["agent_id"].extend([agent_id] * len(dates))
        data["dates"].extend(dates)
        data["counts"].extend(counts)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a line plot using plotly.express
    fig = px.line(df, x='dates', y='counts', color='agent_id', title='Number of Alerts per Agent Over Time', labels={'dates': 'Date', 'counts': 'Number of Alerts'})
    
    # Return the plot as an HTML string
    return fig.to_html(full_html=False)