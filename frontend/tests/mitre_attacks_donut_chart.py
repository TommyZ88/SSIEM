from elasticsearch import Elasticsearch
import plotly.express as px
import pandas as pd
import json
from plotly.utils import PlotlyJSONEncoder

def create_top_mitre_attacks_donut_chart(es: Elasticsearch):
    # Define the Elasticsearch query body
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
            "top_attacks": {
                "terms": {
                    "field": "rule.mitre.id",
                    "size": 10  # Adjust the size to get the top N MITRE ATT&CKs
                }
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['top_attacks']['buckets']
    
    if not buckets:
        return "No data available"
    
    # Initialize data dictionary to hold attack IDs and counts
    data = {
        "attack_id": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract attack IDs and counts
    for bucket in buckets:
        attack_id = bucket['key']
        count = bucket['doc_count']
        
        # Append the extracted data to the lists in the data dictionary
        data["attack_id"].append(attack_id)
        data["counts"].append(count)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)

    # Custom colors
    colors = ['#F8B195', '#F67280', '#C06C84', '#6C5B7B', '#355C7D'] 
    colors = colors[:len(data["attack_id"])]  # Ensure that the length of colors does not exceed the number of labels
    
    # Create a donut chart using plotly.express
    fig = px.pie(df, names='attack_id', values='counts', hole=.5, color_discrete_sequence=colors,
                 title='Top MITRE Attacks Techniques')
    
    hover_template = "<b>ID: %{label}</b><br>Count: %{value}<extra></extra>"
    fig.update_traces(textinfo='percent', hovertemplate=hover_template)

    # Styling from the pie chart
    fig.update_layout(
        margin=dict(
            l=20,
            r=50,
            t=60,
            b=0
        ),
        title=dict(
            text='<b>Top MITRE Attacks Techniques<b>',
            x=0.05,  # Move title a little to the left
            y=0.95,  # Move title a little to the top
            font=dict(
                size=20,
                color='black',
                family='Arial'
            )
        ),
        width=420,
        height=300,
        plot_bgcolor='white',
        legend_title_text='MITRE ID',
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
