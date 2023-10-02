from elasticsearch import Elasticsearch
import plotly.express as px
from datetime import datetime
import json
from plotly.utils import PlotlyJSONEncoder


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

    #fig = px.pie(values=values, names=labels, color_discrete_sequence=px.colors.sequential.Plasma)
    fig = px.pie(values=values, names=labels)
    
    hover_template = "<b>Severity: %{label}</b><br>Count: %{value}<extra></extra>"
    fig.update_traces(textinfo='percent+label', hovertemplate=hover_template)
    
    fig.update_layout(title_text='Alert Severity',
                      title_x=0.5,
                      #font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple"),
                      #legend=dict(x=0, y=1, traceorder='normal', orientation='h',
                      #            font=dict(family="Arial, sans-serif", size=10, color="black"),
                      #            bgcolor="LightSteelBlue", itemclick='toggleothers'),
                      legend_title_text='Severity')
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)