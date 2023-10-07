import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
import json
from plotly.utils import PlotlyJSONEncoder

def create_total_agent_alerts_bar_graph(es: Elasticsearch):

    index_name = "wazuh-alerts-*"

    # Query to get total alerts grouped by agent
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
            "agents": {
                "terms": {
                    "field": "agent.name",
                    "size": 10,  # Getting top 10 agents by alert counts. Adjust if necessary.
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        }
    }

    response = es.search(index=index_name, body=body)

    buckets = response['aggregations']['agents']['buckets']

    agents = [str(bucket['key']) for bucket in buckets]
    alert_counts = [bucket['doc_count'] for bucket in buckets]

    traces = []

    # Using the same colors as provided
    colors = ['#F8B195','#F67280','#C06C84','#6C5B7B','#355C7D'] 

    for agent, alert_count, color in zip(agents, alert_counts, colors):
        hover_text = f'<b>Count: {alert_count}</b>'
        trace = go.Bar(
            x=[agent], 
            y=[alert_count], 
            name=agent, 
            marker_color=color, 
            width=[0.6],
            hoverinfo='text', 
            hovertext=[hover_text]
        )

        traces.append(trace)

    fig = go.Figure(data=traces)

    fig.update_layout(
        margin=dict(
            l=20,
            r=50,
            t=60,
            b=0
        ),
        title=dict(
            text='<b>Total Alerts Per Agent<b>',
            x=0.05,
            y=0.95,
            font=dict(
                size=20,
                color='black',
                family='Arial',
            )
        ),
        width=630,
        height=300,
        plot_bgcolor='white',
        yaxis=dict(
            title='Number of Alerts',
            showline=True,
            linewidth=1,
            linecolor='lightgrey',
            showticksuffix='all',
            ticks='outside',
            tickvals=list(range(0, 151, 10)),
            ticklen=5,
            tickcolor='lightgrey',
            title_standoff=20
        ),
        xaxis=dict(
            showticklabels=False,
            showline=True,
            linewidth=1,
            linecolor='lightgrey'
        ),
        legend=dict(x=1, y=1)
        )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
