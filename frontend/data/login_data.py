from elasticsearch import Elasticsearch

def login_data(es: Elasticsearch):

  res = es.search(index="login-management-*")
  buckets = res['username']['password']

  labels = [str(bucket['key']) for bucket in buckets]
  values = [bucket['doc_count'] for bucket in buckets]

  return(labels, values)



    