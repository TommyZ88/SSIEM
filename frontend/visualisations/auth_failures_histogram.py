import plotly.graph_objects as go
from elasticsearch import Elasticsearch
from datetime import datetime
import json
from plotly.utils import PlotlyJSONEncoder


def create_auth_failures_histogram(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    body = generate_query_body()
    
    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['failures_over_time']['buckets']
    timestamps, agent_failures = extract_data(buckets)

    if not agent_failures:
        fig = create_no_data_figure()
    else:
        fig = create_bar_chart_figure(timestamps, agent_failures)
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def generate_query_body():
    return {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"rule.id": ["2501", "5503", "5301"]}}
                ],
                "must_not": [
                    {"term": {"agent.id": "000"}}
                ]
            }
        },
        "aggs": {
            "failures_over_time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "fixed_interval": "5m"
                },
                "aggs": {
                    "agents": {
                        "terms": {
                            "field": "agent.name",
                            "size": 10,
                            "order": {
                                "_count": "desc"
                            }
                        }
                    }
                }
            }
        }
    }


def extract_data(buckets):
    timestamps = [datetime.utcfromtimestamp(bucket['key'] / 1e3).strftime('%Y-%m-%d %H:%M:%S') for bucket in buckets]
    agent_failures = {}
    for bucket in buckets:
        for agent_bucket in bucket['agents']['buckets']:
            agent_name = agent_bucket['key']
            count = agent_bucket['doc_count']
            agent_failures.setdefault(agent_name, []).append(count)
    return timestamps, agent_failures


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
            text='<b>Authentication Failures Over Time<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        width=830,
        height=300,
        plot_bgcolor='white'
    )
    return fig


def create_bar_chart_figure(timestamps, agent_failures):
    fig = go.Figure()
    colors = ["#58508d","#bc5090","#ff6361","#ffa600"]
    for i, (agent, counts) in enumerate(agent_failures.items()):
        fig.add_trace(go.Bar(
            x=timestamps,
            y=counts,
            name=agent,
            marker_color=colors[i % len(colors)],
            hovertemplate=("<b>Date/Time:</b> %{x}<br>" + "<b>Count:</b> %{y}<br>" + "<extra></extra>")
        ))
    fig.update_layout(
        barmode='stack',
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Authentication Failures Over Time<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        width=830,
        height=300,
        plot_bgcolor='white',
        yaxis=dict(
            title='Number of Failures',
            showline=True,
            linewidth=1,
            linecolor='lightgrey',
            showticksuffix='all',
            ticks='outside',
            tickvals=list(range(0, 41, 5)),
            ticklen=5,
            tickcolor='lightgrey',
            title_standoff=20
        ),
        xaxis=dict(showline=True, linewidth=1, linecolor='lightgrey', tickangle=-45),
        legend=dict(x=1, y=1)
    )
    return fig
