from elasticsearch import Elasticsearch
import plotly.express as px
from datetime import datetime

def create_alert_pie_chart(es: Elasticsearch):
    today = datetime.utcnow()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    body = {
        "size": 0,
        "query": {
            "range": {
                "@timestamp": {
                    "gte": start_of_today
                }
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

    fig = px.pie(values=values, names=labels)
    return fig.to_html(full_html=False)