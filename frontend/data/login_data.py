from elasticsearch import Elasticsearch

def authenticate_user(es: Elasticsearch, username: str, password: str) -> bool:
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"username": username}},
                    {"match": {"password": password}}
                ]
            }
        }
    }
    res = es.search(index="login-management", body=body)
    return res['hits']['total']['value'] > 0  # returns True if user found else False