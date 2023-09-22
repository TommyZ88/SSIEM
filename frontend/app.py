from flask import Flask, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)

es = Elasticsearch(['elasticsearch:9200'], 
                   use_ssl=True, 
                   verify_certs=False, 
                   scheme="https", 
                   http_auth=('admin', 'admin'))

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