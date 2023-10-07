import plotly.express as px
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
import json
from plotly.utils import PlotlyJSONEncoder

def create_auth_failures_bar_graph(es: Elasticsearch):

    index_name = "wazuh-alerts-*"

    # Query to get authentication failures over time grouped by agent
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
            "agents": {
                "terms": {
                    "field": "agent.name",
                    "size": 10,  # Getting top 10 agents by failure counts. Adjust if necessary.
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
    auth_counts = [bucket['doc_count'] for bucket in buckets]

    traces = []

    #colors = ['#54A5C0','#E3577A','#F2BD47','#60BDA5']
    colors = ['#F8B195','#F67280','#C06C84','#6C5B7B','#355C7D'] 

    for agent, auth_count, color in zip(agents, auth_counts, colors):
        hover_text = f'<b>Count: {auth_count}</b>'
        trace = go.Bar(
            x=[agent], 
            y=[auth_count], 
            name=agent, 
            marker_color=color, 
            width=[0.6],
            hoverinfo='text', 
            hovertext=[hover_text]  # This line sets the custom hover text
        )

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
            text='<b>Total Authentication Failures<b>',
            x=0.05,  # Move title a little to the left
            y=0.95,  # Move title a little to the top
            font=dict(
                size=20,           # Font size
                color='black',     # Font color
                family='Arial',
            )
        ),
        width=630,
        height=300,
        plot_bgcolor='white',  # Background color for the plotting area
        yaxis=dict(
            title='Number of Failures',
            showline=True,       # Display the y-axis line
            linewidth=1,         # Set the line width
            linecolor='lightgrey',    # Set the line color
            showticksuffix='all',  # Show ticklines on the y-axis
            ticks='outside',       # Specify that the ticks should be outside the plot
            tickvals=list(range(0, 41, 5)),  # Ticks every 5 units. Adjust as needed.
            ticklen=5,             # Length of the ticks
            tickcolor='lightgrey',
            title_standoff=20      # Increase distance between title and axis
        ),
        xaxis=dict(
            showticklabels=False,
            showline=True,       # Display the x-axis line
            linewidth=1,         # Set the line width
            linecolor='lightgrey'    # Set the line color
        ),
        legend=dict(x=1, y=1)
        )

    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)