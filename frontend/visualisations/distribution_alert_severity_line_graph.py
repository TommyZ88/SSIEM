import plotly.graph_objects as go
from elasticsearch import Elasticsearch
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder

def create_distribution_alert_severity_line_graph(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    body = generate_query_body()
    
    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['severity_over_time']['buckets']
    data = extract_data(buckets)
    
    if not data["timestamps"]:
        fig = create_no_data_figure()
    else:
        fig = create_line_chart_figure(data)
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def generate_query_body():
    return {
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


def extract_data(buckets):
    data = {
        "timestamps": [],
        "severity": [],
        "counts": []
    }
    for bucket in buckets:
        timestamp = bucket['key_as_string']
        for severity_bucket in bucket['severity_levels']['buckets']:
            severity = severity_bucket['key']
            count = severity_bucket['doc_count']
            data["timestamps"].append(timestamp)
            data["severity"].append(severity)
            data["counts"].append(count)
    return data


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
            text='<b>Distribution of Alert Severity Levels Over Time<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        width=850,
        height=300,
        plot_bgcolor='white'
    )
    return fig


def create_line_chart_figure(data):
    df = pd.DataFrame(data)
    colors = ["#58508d","#bc5090","#ff6361","#ffa600"]
    severity_levels = df["severity"].unique()
    
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
                "<extra></extra>" 
            )
            )
        )
    
    fig.update_layout(
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Distribution of Alert Severity Levels Over Time<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
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
    return fig
