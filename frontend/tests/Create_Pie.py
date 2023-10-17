from elasticsearch import Elasticsearch
import plotly.express as px
import json
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime

def create_alert_severity_pie_chart(es: Elasticsearch):
    today = datetime.utcnow()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    body = {
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
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['severity_count']['buckets']

    labels = [str(bucket['key']) for bucket in buckets]
    values = [bucket['doc_count'] for bucket in buckets]

    #colors = ['#54A5C0', '#E3577A', '#F2BD47', '#60BDA5']
    colors = ['#F8B195','#F67280','#C06C84','#6C5B7B','#355C7D'] 

    # Ensure that the length of colors does not exceed the number of labels
    colors = colors[:len(labels)]

    fig = px.pie(values=values, names=labels, color_discrete_sequence=colors)
    
    hover_template = "<b>Severity: %{label}</b><br>Count: %{value}<extra></extra>"
    fig.update_traces(textinfo='percent', hovertemplate=hover_template)
    
    fig.update_layout(
        margin=dict(
            l=20,
            r=50,
            t=60,
            b=0
        ),
        title=dict(
            text='<b>Alert Severity<b>',
            x=0.05,  # Move title a little to the left
            y=0.95,  # Move title a little to the top
            font=dict(
                size=20,
                color='black',
                family='Arial'
            )
        ),
        width=430,
        height=300,
        plot_bgcolor='white',
        legend_title_text='Severity Level',
        legend=dict(
            x=1, 
            y=1, 
            font=dict(
                family="Arial, sans-serif", 
                size=10, 
                color="black"))
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)

