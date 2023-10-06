from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder

def create_top_events_donut_chart(es: Elasticsearch):
    # Define the Elasticsearch query body
    body = {
        "size": 0,
        "aggs": {
            "top_events": {
                "terms": {"field": "rule.description", "size": 5}  # Adjust the size to get the top 5 events
            }
        },
        "query": {
            "bool": {
                "must": {"match_all": {}},
                "must_not": {"term": {"agent.id": "000"}}
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['top_events']['buckets']
    
    if not buckets:
        return "No data available"
    
    # Initialize data dictionary to hold event names and counts
    data = {
        "event_name": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract event names and counts
    for bucket in buckets:
        event_name = bucket['key']
        count = bucket['doc_count']
        
        # Append the extracted data to the lists in the data dictionary
        data["event_name"].append(event_name)
        data["counts"].append(count)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)

    # Custom colors from mitre.py
    colors = ['#F8B195', '#F67280', '#C06C84', '#6C5B7B', '#355C7D']
    colors = colors[:len(data["event_name"])]
    
    # Create a donut chart using plotly.express with styling applied
    fig = px.pie(df, names='event_name', values='counts', hole=.5, color_discrete_sequence=colors,
                 title='Top 5 Events')

    hover_template = "<b>Count: %{value}</b>"
    fig.update_traces(textinfo='percent', hovertemplate=hover_template)
    
    # Apply styling from mitre.py
    fig.update_layout(
        margin=dict(
            l=20,
            r=50,
            t=60,
            b=0
        ),
        title=dict(
            text='<b>Top 5 Events<b>',
            x=0.05,
            y=0.95,
            font=dict(
                size=20,
                color='black',
                family='Arial'
            )
        ),
        width=650,
        height=300,
        plot_bgcolor='white',
        legend_title_text='Event Name',
        legend=dict(
            x=1, 
            y=1, 
            font=dict(
                family="Arial, sans-serif", 
                size=10, 
                color="black"))
    )
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)
