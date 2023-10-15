from elasticsearch import Elasticsearch
import plotly.graph_objects as go
import json
from plotly.utils import PlotlyJSONEncoder


def create_top_events_donut_chart(es: Elasticsearch):
    index_name = "wazuh-alerts-*"
    body = generate_query_body()
    
    response = es.search(index=index_name, body=body)
    buckets = response['aggregations']['top_events']['buckets']
    event_names, counts = extract_data(buckets)

    if not counts:
        fig = create_no_data_figure()
    else:
        fig = create_pie_chart_figure(event_names, counts)
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def generate_query_body():
    return {
        "size": 0,
        "aggs": {
            "top_events": {
                "terms": {"field": "rule.description", "size": 5}  
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
    event_names = [bucket['key'] for bucket in buckets]
    counts = [bucket['doc_count'] for bucket in buckets]
    return event_names, counts

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
            text='<b>Top 5 Events<b>',
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

def create_pie_chart_figure(event_names, counts):
    colors = ["#003f5c","#58508d","#bc5090","#ff6361","#ffa600"]

    fig = go.Figure(go.Pie(
        labels=event_names, 
        values=counts,
        hole=0.5,
        textinfo='percent',
        hovertemplate=("<b>Count: %{value}</b>" +
                       "<extra></extra>" 
        ),
        marker=dict(colors=colors)
    ))
    fig.update_layout(
        margin=dict(l=20, r=50, t=60, b=0),
        title=dict(
            text='<b>Top 5 Events<b>',
            x=0.05,
            y=0.95,
            font=dict(size=20, color='black', family='Arial')
        ),
        width=700,
        height=300,
        plot_bgcolor='white',
        legend_title_text='Event Name',
        legend=dict(x=1, y=1)
    )
    return fig
