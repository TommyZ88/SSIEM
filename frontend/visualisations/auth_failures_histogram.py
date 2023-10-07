import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
from datetime import datetime
import json
from plotly.utils import PlotlyJSONEncoder

def create_auth_failures_histogram(es: Elasticsearch):
    index_name = "wazuh-alerts-*"

    body = {
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

    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['failures_over_time']['buckets']

    timestamps = []
    agent_failures = {}

    for bucket in buckets:
        ts = datetime.utcfromtimestamp(bucket['key'] / 1e3).strftime('%Y-%m-%d %H:%M:%S')
        timestamps.append(ts)

        for agent_bucket in bucket['agents']['buckets']:
            agent_name = agent_bucket['key']
            count = agent_bucket['doc_count']

            if agent_name not in agent_failures:
                agent_failures[agent_name] = []

            agent_failures[agent_name].append(count)

    fig = go.Figure()

    colors = ['#F8B195','#F67280','#C06C84','#6C5B7B','#355C7D']

    for i, (agent, counts) in enumerate(agent_failures.items()):
        fig.add_trace(go.Bar(
            x=timestamps,
            y=counts,
            name=agent,
            marker_color=colors[i % len(colors)],
            hovertemplate=(
                "<b>Date/Time:</b> %{x}<br>" +
                "<b>Count:</b> %{y}<br>" +
                "<extra></extra>"  # This hides additional info usually shown in hover
            )
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
        xaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='lightgrey',
            tickangle=-45  # for better visibility of x-axis labels (timestamps)
        ),
        legend=dict(x=1, y=1)
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
