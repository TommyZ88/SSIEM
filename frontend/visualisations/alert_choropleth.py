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
    fig.update_layout(title_text='Number of Alerts by Country')
    
    # Instead of returning HTML, convert the figure to JSON and return that.
    return json.dumps(fig, cls=PlotlyJSONEncoder)
