from flask import Flask, jsonify, render_template, url_for
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from elasticsearch import Elasticsearch
import plotly.io as pio

from visualisations.alert_pie_chart import create_alert_pie_chart
from visualisations.agent_info_table import create_agent_info_table
from visualisations.auth_failure_bar_chart import create_auth_failure_bar_chart
from visualisations.alerts_per_agent_plot import create_alerts_per_agent_plot
from visualisations.bar_chart import create_bar_chart


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKey'
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


@app.route('/home') #home page
def home():
    return render_template('home.html')

#Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'


    return render_template('login.html', form=form)


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
    plot2 = create_alerts_per_agent_plot(es)
    agent_table = create_agent_info_table(es)
    alert_severity = create_alert_pie_chart(es)
    auth_failure = create_auth_failure_bar_chart(es)
    bar_chart_showing_hosts = create_bar_chart(es)
    return render_template('dashboard.html',
                           agent_table=agent_table,
                           alert_severity=alert_severity,
                           auth_failure=auth_failure,
                           plot2=plot2, bar_chart_showing_hosts = bar_chart_showing_hosts)



@app.route('/dashboard_data')
def dashboard_data():
    plot2 = create_alerts_per_agent_plot(es)
    agent_table = create_agent_info_table(es)
    return jsonify(plot2=plot2.to_html(full_html=False))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(5000), debug=True)