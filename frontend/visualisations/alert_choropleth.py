from elasticsearch import Elasticsearch
import plotly.express as px
import json
from plotly.utils import PlotlyJSONEncoder

def create_alert_choropleth(es: Elasticsearch):
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
        "alerts_by_country": {
            "terms": {
                "field": "GeoLocation",
                "size": 200,
                "missing": "Unknown Location" 
            }
        }
    }
}

    res = es.search(index="wazuh-alerts-*", body=body)

    countries = ["Australia"]
    values = [res['hits']['total']['value']]

    # Create a choropleth map
    fig = px.choropleth(
        data_frame=res,
        locations=countries,
        color=values,
        locationmode='country names',
        color_continuous_scale="Viridis",
        labels={'color':'Number of Alerts'}
    )
    
    fig.update_layout(
        margin=dict(
            l=20,
            r=50,
            t=60,
            b=0
        ),
        title=dict(
            text='<b>Number of Alerts by Country<b>',
            x=0.05,
            y=0.95,
            font=dict(
                size=20,
                color='black',
                family='Arial'
            )
        ),
        width=800,
        plot_bgcolor='white',
        showlegend=False,  # This line removes the legend
        geo=dict(
            landcolor='#f2f0e9',       # Color for continents
            coastlinecolor='#b3d3dd',      # Color for country borders
            showocean=True, 
            oceancolor="#b3d3dd",
            showlakes=False,
            projection_type="equirectangular"  # This is one type of map projection. You can use others like 'mercator', 'orthographic' etc.
        )
    )


    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)
