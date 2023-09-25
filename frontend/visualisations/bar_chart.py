import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch

def create_bar_chart(es: Elasticsearch):

    index_name = "wazuh-monitoring-*"

    body = {
        "size": 0,
        "aggs": {
            "hosts": {
                "terms": {
                    "field": "name",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        }
    }

    response = es.search(index=index_name, body=body)

    buckets = response['aggregations']['hosts']['buckets']

    print (buckets)

    hosts = [str(bucket['key']) for bucket in buckets]
    attack_counts = [bucket['doc_count'] for bucket in buckets]

    fig = go.Figure(data=[go.Bar(x=hosts, y=attack_counts)])
    fig.update_layout(title='Most Frequently Attacked Machines',
                      xaxis_title='Machine Name',
                      yaxis_title='Number of Attacks')

    return fig.to_html(full_html=False)