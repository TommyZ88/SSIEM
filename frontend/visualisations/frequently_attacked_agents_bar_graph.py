import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
import json
from plotly.utils import PlotlyJSONEncoder

def create_frequently_attacked_agents_bar_graph(es: Elasticsearch):

    index_name = "wazuh-monitoring-*"

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
            "hosts": {
                "terms": {
                    "field": "name",
                    "size": 100,
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

    colors = ['#54A5C0','#E3577A','#60BDA5','#F2BD47']
    # Create separate bar traces for each host
    traces = []
    for host, attack_count, color in zip(hosts, attack_counts, colors):
        trace = go.Bar(x=[host], y=[attack_count], name=host, marker_color=color, width=[0.6])
        traces.append(trace)

    fig = go.Figure(data=traces)

    fig.update_layout(
        margin=dict(
            l=20,  # left margin in pixels
            r=50,  # right margin in pixels
            t=60,  # top margin in pixels
            b=0   # bottom margin in pixels
        ),
        title=dict(
            text='Most Frequently Attacked Machines',
            x=0.05,  # Move title a little to the left
            y=0.95,  # Move title a little to the top
            font=dict(
                size=20,           # Font size
                color='black',     # Font color
                family='Arial',
            )
        ),
        width=600,
        height=340,
        plot_bgcolor='white',  # Background color for the plotting area
        #paper_bgcolor='whitesmoke',  # Background color for the entire figure
        yaxis=dict(
            title='Number of Attacks',
            showline=True,       # Display the y-axis line
            linewidth=1,         # Set the line width
            linecolor='grey',    # Set the line color
            tickvals=list(range(0, 41, 5))  # Ticks every 5 units. Adjust as needed.
        ),
        xaxis=dict(
            showticklabels=False,
            showline=True,       # Display the x-axis line
            linewidth=1,         # Set the line width
            linecolor='grey'    # Set the line color
        ),
        legend=dict(x=1, y=1)
        )

    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)