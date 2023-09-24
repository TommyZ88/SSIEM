from flask import Flask, jsonify, render_template
from elasticsearch import Elasticsearch
import plotly.express as px
import plotly.io as pio
from pandas import DataFrame
import pandas as pd

app = Flask(__name__)

es = Elasticsearch(['elasticsearch:9200'], # ES Connection To elastic DB
                   use_ssl=True,    
                   verify_certs=False,
                   scheme="https", 
                   http_auth=('admin', 'admin'))

pio.renderers.default = 'browser'  # set the default renderer to browser

@app.route('/dashboard')
def dashboard():
    plot1 = create_alert_level_over_time_plot() # Query and create multiple plots here
    plot2 = create_alerts_per_agent_plot()
    agent_table = create_agent_info_table()  # Initiating the creation of the agent_table here
    return render_template('dashboard.html', plot1=plot1, plot2=plot2, agent_table=agent_table)  # Render multiple templates with multiple plots


@app.route('/dashboard_data')
def dashboard_data():
    plot1 = create_alert_level_over_time_plot()
    plot2 = create_alerts_per_agent_plot()
    agent_table = create_agent_info_table()
    return jsonify(plot1=plot1.to_html(full_html=False), plot2=plot2.to_html(full_html=False), agent_table=agent_table)

@app.route('/management') #account management page
def management():
    return render_template('management.html')


def create_alert_level_over_time_plot():
    body = {
        "size": 0,
        "aggs": {
            "alerts_over_time": {
                "date_histogram": {"field": "@timestamp", "calendar_interval": "day"},
                "aggs": {"avg_level": {"avg": {"field": "rule.level"}}}
            }
        }
    }
    res = es.search(index="wazuh-alerts-*", body=body)
    buckets = res['aggregations']['alerts_over_time']['buckets']

    dates = [bucket['key_as_string'] for bucket in buckets]
    levels = [bucket['avg_level']['value'] for bucket in buckets]

    fig = px.line(x=dates, y=levels, labels={'x': 'Date', 'y': 'Average Alert Level'})
    fig.update_layout(title='Alert Level Over Time')
    fig.update_xaxes(tick0=dates[0] if dates else "2023-09-01", dtick="86400000")  # 86400000 milliseconds per day

    return fig.to_html(full_html=False)


def create_agent_info_table():
    body = {"size": 1000}  # adjust the size according to your needs
    res = es.search(index="wazuh-monitoring-*", body=body)
    agents = res['hits']['hits']
    seen_agent_ids = set()  # Keep track of seen agent IDs

    table_data = []
    for agent in agents:
        source = agent["_source"]
        agent_id = source.get("id", "")

        if agent_id in seen_agent_ids:
            continue

        name = source.get("name", "")
        ip = source.get("ip", "")
        status = source.get("status", "")
        
        table_data.append([agent_id, name, ip, status])
        seen_agent_ids.add(agent_id)  # Mark this agent ID as seen

    df = DataFrame(table_data, columns=["Agent ID", "Name", "IP", "Status"])
    return df.to_html(index=False, classes='table table-striped')


def create_alerts_per_agent_plot():
    # Define the Elasticsearch query body
    # It includes aggregations to group data by agent.id and further group by dates
    body = {
        "size": 0,  # We set the size to 0 as we are interested in aggregation results only
        "aggs": {
            "alerts_per_agent": {
                "terms": {"field": "agent.id.keyword"},  # Grouping by agent.id
                "aggs": {
                    "alerts_over_time": {
                        "date_histogram": {"field": "@timestamp", "calendar_interval": "day"}  # Further grouping by dates
                    }
                }
            }
        }
    }
    
    # Perform the search query on the specified Elasticsearch index
    res = es.search(index="wazuh-alerts-*", body=body)
    
    # Extract the buckets from the aggregation results
    buckets = res['aggregations']['alerts_per_agent']['buckets']
    
    # Initialize data dictionary to hold agent_id, dates, and counts
    data = {
        "agent_id": [],
        "dates": [],
        "counts": []
    }
    
    # Iterate through each bucket and extract agent_id, dates, and counts
    for bucket in buckets:
        agent_id = bucket['key']  # The key of the bucket is the agent_id
        dates = [item['key_as_string'] for item in bucket['alerts_over_time']['buckets']]  # Extract dates from nested buckets
        counts = [item['doc_count'] for item in bucket['alerts_over_time']['buckets']]  # Extract document count for each nested bucket
        
        # Extend the lists in the data dictionary with the extracted data
        data["agent_id"].extend([agent_id] * len(dates))
        data["dates"].extend(dates)
        data["counts"].extend(counts)
    
    # Convert the data dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Create a line plot using plotly.express
    fig = px.line(df, x='dates', y='counts', color='agent_id', title='Number of Alerts per Agent Over Time', labels={'dates': 'Date', 'counts': 'Number of Alerts'})
    
    # Return the plot as an HTML string
    return fig.to_html(full_html=False)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test_es')
def test_es_connection():
    try:
        # This line will test the connection and return Elasticsearch info
        res = es.info()
        return jsonify(res)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(5000), debug=True)