import plotly.graph_objects as go
from elasticsearch import Elasticsearch
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder


def create_top_mitre_attacks_donut_chart(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    body = generate_query_body()

    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['top_attacks']['buckets']
    data = extract_data(buckets)

    if not buckets:
        fig = create_no_data_figure()
    else:
        fig = create_donut_chart_figure(data)
    
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
            "top_attacks": {
                "terms": {
                    "field": "rule.mitre.id",
                    "size": 10 
                }
            }
        }
    }


def extract_data(buckets):
    data = {
        "attack_id": [],
        "counts": []
    }
    for bucket in buckets:
        attack_id = bucket['key']
        count = bucket['doc_count']
        data["attack_id"].append(attack_id)
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
            text='<b>Top MITRE Attacks Techniques<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        width=420,
        height=300,
        plot_bgcolor='white'
    )
    return fig


def create_donut_chart_figure(data):
    colors = ["#58508d","#bc5090","#ff6361","#ffa600"]
    colors = colors[:len(data["attack_id"])]  

    fig = go.Figure(data=[go.Pie(labels=data['attack_id'], values=data['counts'], hole=.5)])
    fig.update_traces(textinfo='percent', hovertemplate="<b>ID: %{label}</b><br>Count: %{value}<extra></extra>",
                      marker=dict(colors=colors))
    fig.update_layout(
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Top MITRE Attacks Techniques<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        width=420,
        height=300,
        plot_bgcolor='white',
        legend_title_text='MITRE ID',
        legend=dict(x=1, y=1, font=dict(family="Arial, sans-serif", size=10, color="black"))
    )
    return fig
