from elasticsearch import Elasticsearch
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder

def create_distribution_alert_severity_line_graph(es: Elasticsearch):
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
            "severity_over_time": {
                "date_histogram": {"field": "@timestamp", "fixed_interval": "10m"},
                "aggs": {
                    "severity_levels": {"terms": {"field": "rule.level"}}
                }
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['severity_over_time']['buckets']
    
    if not buckets:
        return "No data available"
    
    # Initialize data dictionary to hold timestamps, severity levels, and counts
    data = {
        "timestamps": [],
        "severity": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract timestamps, severity levels, and counts
    for bucket in buckets:
        timestamp = bucket['key_as_string']
        for severity_bucket in bucket['severity_levels']['buckets']:
            severity = severity_bucket['key']
            count = severity_bucket['doc_count']
            
            # Append the extracted data to the lists in the data dictionary
            data["timestamps"].append(timestamp)
            data["severity"].append(severity)
            data["counts"].append(count)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a line chart using plotly.express
    fig = px.line(df, x='timestamps', y='counts', color='severity', 
                  labels={'timestamps': 'Time', 'counts': 'Alert Count', 'severity': 'Severity Level'},
                  title='Distribution of Alert Severity Levels Over Time')
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)