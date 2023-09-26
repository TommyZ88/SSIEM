from elasticsearch import Elasticsearch
import plotly.express as px
from datetime import datetime, timedelta


def create_auth_failure_bar_chart(es: Elasticsearch):
    body = {
        "size": 0,
        "aggs": {
            "auth_failures_over_time": {
                "date_histogram": {"field": "@timestamp", "fixed_interval": "10m"},
                "aggs": {"auth_failures": {"terms": {"field": "rule.description", "include": ["Authentication failure"]}}}
            }
        }
    }
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['auth_failures_over_time']['buckets']
    
    if not buckets:
        return "No data available"
    
    start_time = datetime.fromisoformat(buckets[0]['key_as_string'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(buckets[-1]['key_as_string'].replace('Z', '+00:00'))
    
    time_intervals = []
    current_time = start_time
    while current_time <= end_time:
        time_intervals.append(current_time)
        current_time += timedelta(minutes=15)

    timestamps = []
    counts = []
    for time_interval in time_intervals:
        bucket = next((bucket for bucket in buckets if datetime.fromisoformat(bucket['key_as_string'].replace('Z', '+00:00')) == time_interval), None)
        
        timestamps.append(time_interval.isoformat())
        if bucket:
            counts.append(bucket['doc_count'])
        else:
            counts.append(0)  
    
    fig = px.bar(x=timestamps, y=counts, labels={'x': 'Time', 'y': 'Failures Count'})
    fig.update_layout(title='Authentication Failures Over Time')
    return fig.to_html(full_html=False)