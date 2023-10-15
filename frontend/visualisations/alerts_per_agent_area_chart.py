from elasticsearch import Elasticsearch
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import json
from plotly.utils import PlotlyJSONEncoder

def create_alerts_per_agent_area_chart(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    body = generate_query_body()
    
    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['alerts_over_time']['buckets']
    data_points = extract_data(buckets)

    if not buckets:
        fig = create_no_data_figure()
    else:
        fig = create_area_chart_figure(data_points)
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def generate_query_body():
    return {
        "size": 0,
        "aggs": {
            "alerts_over_time": {
                "date_histogram": {"field": "@timestamp", "fixed_interval": "5m"},
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


def extract_data(buckets):
    data = []
    for bucket in buckets:
        timestamp = bucket['key_as_string']
        for agent_bucket in bucket['agent_names']['buckets']:
            agent_name = agent_bucket['key']
            count = agent_bucket['doc_count']
            data.append({
                "Timestamp": datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'),
                "Agent Name": agent_name,
                "Alert Count": count
            })
    return pd.DataFrame(data)


def create_no_data_figure():
    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source="../static/images/noresults.png",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.5, sizey=0.5,
            xanchor="center", yanchor="middle"
        )
    )
    fig.update_layout(
        title=dict(
            text='<b>Number of Alerts Per Agent Over Time<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        width=700,
        height=300,
        plot_bgcolor='white'
    )
    return fig


def create_area_chart_figure(df):
    fig = go.Figure()
    agents = df["Agent Name"].unique()
    colors = ["#58508d","#bc5090","#ff6361","#ffa600"]
    for agent, color in zip(agents, colors):
        filtered_df = df[df["Agent Name"] == agent]
        r, g, b = [int(x) for x in bytes.fromhex(color[1:])]
        fig.add_trace(go.Scatter(
            x=filtered_df["Timestamp"],
            y=filtered_df["Alert Count"],
            mode='lines+markers',
            fill='tozeroy',
            name=agent,
            line=dict(color=color, width=5),
            marker=dict(size=10),
            fillcolor=f'rgba({r},{g},{b},0.9)',
            hovertemplate=("<b>Date/Time:</b> %{x}<br>" + "<b>Count:</b> %{y}<br>" + "<extra></extra>")
        ))
    fig.update_layout(
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Number of Alerts Per Agent Over Time<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        width=700,
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
        xaxis=dict(showline=True, linewidth=1, linecolor='lightgrey'),
        legend=dict(x=1, y=1)
    )
    return fig
