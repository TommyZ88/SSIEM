from flask import Flask, jsonify, render_template
from elasticsearch import Elasticsearch
import plotly.express as px
import plotly.io as pio
from pandas import DataFrame
import pandas as pd
from datetime import datetime, timedelta

from visualisations import (agent_info_table, alert_pie_chart,
    auth_failure_bar_chart, alerts_per_agent_plot
)

app = Flask(__name__)

es = Elasticsearch(['elasticsearch:9200'], # ES Connection To elastic DB
                   use_ssl=True,    
                   verify_certs=False,
                   scheme="https", 
                   http_auth=('admin', 'admin'))

pio.renderers.default = 'browser'  # set the default renderer to browser

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test_es')
def test_es_connection():
    try:
        res = es.info()
        return jsonify(res)
    except Exception as e:
        return str(e)

@app.route('/management') #account management page
def management():
    return render_template('management.html')

@app.route('/dashboard')
def dashboard():
    plot2 = alerts_per_agent_plot.create_alerts_per_agent_plot(es)
    agent_table = agent_info_table.create_agent_info_table(es)
    alert_severity = alert_pie_chart.create_alert_pie_chart(es)
    auth_failure = auth_failure_bar_chart.create_auth_failure_bar_chart(es)
    return render_template('dashboard.html',
                           agent_table=agent_table,
                           alert_severity=alert_severity,
                           auth_failure=auth_failure,
                           plot2=plot2)


@app.route('/dashboard_data')
def dashboard_data():
    plot2 = alerts_per_agent_plot.create_alerts_per_agent_plot(es)
    agent_table = agent_table = agent_info_table.create_agent_info_table(es)
    return jsonify(plot2=plot2.to_html(full_html=False))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(5000), debug=True)