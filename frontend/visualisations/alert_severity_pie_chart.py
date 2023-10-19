import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
from datetime import datetime
import json
from plotly.utils import PlotlyJSONEncoder


def create_alert_severity_pie_chart(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    start_of_today = get_start_of_today()
    body = generate_query_body(start_of_today)
    
    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['severity_count']['buckets']
    labels, values = extract_data(buckets)
    
    if not values:
        fig = create_no_data_figure()
    else:
        fig = create_pie_chart_figure(labels, values)
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def get_start_of_today():
    today = datetime.utcnow()
    return today.replace(hour=0, minute=0, second=0, microsecond=0)


def generate_query_body(start_of_today):
    return {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": start_of_today}}}
                ],
                "must_not": [
                    {"term": {"agent.id": "000"}}
                ]
            }
        },
        "aggs": {
            "severity_count": {
                "terms": {"field": "rule.level"}
            }
        }
    }


def extract_data(buckets):
    labels = [str(bucket['key']) for bucket in buckets]
    values = [bucket['doc_count'] for bucket in buckets]
    return labels, values


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
            text='<b>Alert Severity<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        width=430,
        height=300,
        plot_bgcolor='white'
    )
    return fig


def create_pie_chart_figure(labels, values):
    colors = ["#58508d","#bc5090","#ff6361","#ffa600"]
    colors = colors[:len(labels)]
    fig = px.pie(values=values, names=labels, color_discrete_sequence=colors)
    
    hover_template = "<b>Severity: %{label}</b><br>Count: %{value}<extra></extra>"
    fig.update_traces(textinfo='percent', hovertemplate=hover_template, pull=[0.05, 0.05, 0.05, 0.05, 0.05])
    
    fig.update_layout(
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Alert Severity<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        width=430,
        height=300,
        plot_bgcolor='white',
        legend_title_text='Severity Level',
        legend=dict(x=1, y=1, font=dict(family="Arial, sans-serif", size=10, color="black"))
    )
    return fig
