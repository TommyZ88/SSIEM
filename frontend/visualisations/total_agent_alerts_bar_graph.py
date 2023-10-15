import plotly.graph_objects as go
from elasticsearch import Elasticsearch
import json
from plotly.utils import PlotlyJSONEncoder


def create_total_agent_alerts_bar_graph(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    body = generate_query_body()
    
    response = es.search(index=index_name, body=body)
    agents, alert_counts = extract_data(response)
    
    if not agents:
        fig = create_no_data_figure()
    else:
        fig = create_bar_chart_figure(agents, alert_counts)
    
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


def extract_data(response):
    buckets = response['aggregations']['agents']['buckets']
    agents = [str(bucket['key']) for bucket in buckets]
    alert_counts = [bucket['doc_count'] for bucket in buckets]
    return agents, alert_counts


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
            text='<b>Total Alerts Per Agent<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False),
        width=630,
        height=300,
        plot_bgcolor='white'
    )
    return fig


def create_bar_chart_figure(agents, alert_counts):
    fig = go.Figure()
    colors = ["#58508d","#bc5090","#ff6361","#ffa600"]

    for agent, alert_count, color in zip(agents, alert_counts, colors):
        hover_text = f'<b>Count: {alert_count}</b>'
        fig.add_trace(go.Bar(
            x=[agent], 
            y=[alert_count], 
            name=agent, 
            marker_color=color, 
            width=[0.6],
            hoverinfo='text', 
            hovertext=[hover_text]
        ))

    fig.update_layout(
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Total Alerts Per Agent<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
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
        xaxis=dict(showticklabels=False, showline=True, linewidth=1, linecolor='lightgrey'),
        legend=dict(x=1, y=1)
    )
    return fig
