from flask import Flask, jsonify, render_template, url_for, redirect, flash, session
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from elasticsearch import Elasticsearch
from flask_session import Session

import plotly.io as pio

from visualisations.alert_pie_chart import create_alert_pie_chart
from visualisations.agent_info_table import create_agent_info_table
from visualisations.auth_failure_bar_chart import create_auth_failure_bar_chart
from visualisations.alerts_per_agent_line_chart import create_alerts_per_agent_line_chart
from visualisations.bar_chart import create_bar_chart
from visualisations.distribution_of_alert_severity_plot import create_distribution_of_alert_severity_plot
from visualisations.event_logs_table import create_event_logs_table
from data.login_data import authenticate_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKey'
app.config['SECRET_KEY'] = 'SecretKey'
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem session
app.config['SESSION_PERMANENT'] = False
Session(app)
Bootstrap(app)

es = Elasticsearch(['elasticsearch:9200'], # ES Connection To elastic DB
                   use_ssl=True,    
                   verify_certs=False,
                   scheme="https", 
                   http_auth=('admin', 'admin'))

pio.renderers.default = 'browser'  # set the default renderer to browser


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = StringField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

#Home page
@app.route('/home') 
def home():
    return render_template('home.html')


#Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate_user(es, username, password):
            session['username'] = username
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/test_es')
def test_es_connection():
    try:
        res = es.info()
        return jsonify(res)
    except Exception as e:
        return str(e)


#Account management page
@app.route('/management') 
def management():
    return render_template('management.html')


@app.route('/dashboard')
def dashboard():
    agent_table = create_agent_info_table(es)
    alerts_per_agent = create_alerts_per_agent_line_chart(es)  
    alert_severity = create_alert_pie_chart(es)
    auth_failure = create_auth_failure_bar_chart(es)
    bar_chart_showing_hosts = create_bar_chart(es)
    distribution_alert_severity = create_distribution_of_alert_severity_plot(es)
    event_logs_table = create_event_logs_table(es)
    return render_template('dashboard.html',
                           agent_table=agent_table,
                           alerts_per_agent=alerts_per_agent, 
                           alert_severity=alert_severity,
                           auth_failure=auth_failure,
                           bar_chart_showing_hosts = bar_chart_showing_hosts,
                           distribution_alert_severity = distribution_alert_severity,
                           event_logs_table = event_logs_table)

#Dashboard page
@app.route('/dashboard_data')
def dashboard_data():
    agent_table = create_agent_info_table(es)
    alert_severity = create_alert_pie_chart(es)
    event_logs_table = create_event_logs_table(es)
    return jsonify(agent_table=agent_table, 
                   alert_severity=alert_severity,
                   event_logs_table = event_logs_table)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(5000), debug=True)