from elasticsearch import Elasticsearch
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import json
from plotly.utils import PlotlyJSONEncoder

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
    
    # Create a Figure using Graph Objects
    fig = go.Figure()
    agents = df["Agent Name"].unique()
    colors = ['#54A5C0','#E3577A','#F2BD47','#60BDA5']

    for agent, color in zip(agents, colors):
        filtered_df = df[df["Agent Name"] == agent]
        # Extracting RGB values from the color
        r, g, b = [int(x) for x in bytes.fromhex(color[1:])]
        
        fig.add_trace(
            go.Scatter(
                x=filtered_df["Timestamp"],
                y=filtered_df["Alert Count"],
                mode='lines+markers',
                fill='tozeroy',
                name=agent,
                line=dict(color=color),
                fillcolor=f'rgba({r},{g},{b},0.8)'  # 70% opacity
            )
        )
    
    # Applying the styles as per bar_chart.py
    fig.update_layout(
        margin=dict(
            l=20,  # left margin in pixels
            r=50,  # right margin in pixels
            t=60,  # top margin in pixels
            b=0    # bottom margin in pixels
        ),
        title=dict(
            text='<b>Number of Alerts Per Agent Over Time<b>',
            x=0.05,  # Move title a little to the left
            y=0.95,  # Move title a little to the top
            font=dict(
                size=20,           # Font size
                color='black',     # Font color
                family='Arial',
            )
        ),
        width=700,
        height=200,
        plot_bgcolor='white',
        yaxis=dict(
            title='Number of Alerts',
            showline=True,
            linewidth=1,
            linecolor='lightgrey',
            showticksuffix='all',
            ticks='outside',
            tickvals=list(range(5, 31, 5)),  # Ticks every 5 units. Adjust as needed.
            ticklen=5,
            tickcolor='lightgrey',
            title_standoff=20
        ),
        xaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='lightgrey'
        ),
        legend=dict(x=1, y=1)
    )
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)
