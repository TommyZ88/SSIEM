from elasticsearch import Elasticsearch
import plotly.graph_objects as go
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
                "date_histogram": {"field": "@timestamp", "fixed_interval": "5m"},
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

    # Custom colors from area_chart.py
    colors = ['#F8B195','#F67280','#C06C84','#6C5B7B','#355C7D']
    severity_levels = df["severity"].unique()

    # Create a line chart using Graph Objects
    fig = go.Figure()
    for severity, color in zip(severity_levels, colors):
        filtered_df = df[df["severity"] == severity]
        fig.add_trace(
            go.Scatter(
                x=filtered_df["timestamps"],
                y=filtered_df["counts"],
                mode='lines+markers',
                name=str(severity),
                line=dict(color=color, width=5),
                marker=dict(size=10),
                hovertemplate=(
                "<b>Date/Time:</b> %{x}<br>" +
                "<b>Count:</b> %{y}<br>" +
                "<extra></extra>"  # This hides additional info usually shown in hover
            )
            )
        )
    
    # Applying the styles as per area_chart.py
    fig.update_layout(
        margin=dict(
            l=20,  # left margin in pixels
            r=50,  # right margin in pixels
            t=60,  # top margin in pixels
            b=0    # bottom margin in pixels
        ),
        title=dict(
            text='<b>Distribution of Alert Severity Levels Over Time<b>',
            x=0.05,  # Move title a little to the left
            y=0.95,  # Move title a little to the top
            font=dict(
                size=20,           # Font size
                color='black',     # Font color
                family='Arial',
            )
        ),
        width=850,
        height=300,
        plot_bgcolor='white',
        yaxis=dict(
            title='Number of Alerts',
            showline=True,
            linewidth=1,
            linecolor='lightgrey',
            showticksuffix='all',
            ticks='outside',
            ticklen=5,
            tickcolor='lightgrey',
            title_standoff=20
        ),
        xaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='lightgrey'
        ),
        legend=dict(x=1, y=1, title_text="Alert Level")
    )
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)
