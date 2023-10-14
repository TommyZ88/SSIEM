#!/bin/bash

until curl -s elasticsearch:9200 -o /dev/null; do
    echo "Waiting for Elasticsearch..."
    sleep 10
done

echo "Creating the index..."
curl -X PUT "elasticsearch:9200/login-management" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "username": { "type": "keyword" },
      "password": { "type": "keyword" }
    }
  }
}'


echo "Creating Admin..."
curl -X POST "elasticsearch:9200/login-management/_doc/admin" -H 'Content-Type: application/json' -d'
{
  "username": "admin",
  "password": "admin"
}'

echo "Creating Owner..."
curl -X POST "elasticsearch:9200/login-management/_doc/owner" -H 'Content-Type: application/json' -d'
{
  "username": "owner",
  "password": "owner"
}'