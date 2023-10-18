 #!/bin/bash

echo "
Creating the index..."
docker exec -it elasticsearch curl -k -u "admin:admin" -X PUT "https://localhost:9200/login-management" -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "username": { "type": "text" },
      "password": { "type": "text" }
    }
  }
}'

sleep 2

echo "
Creating Admin..."
docker exec -it elasticsearch curl -k -u "admin:admin" -X POST "https://localhost:9200/login-management/_doc" -H 'Content-Type: application/json' -d '{
  "username": "admin",
  "password": "admin"
}'

sleep 2

echo "
Creating Owner..."
docker exec -it elasticsearch curl -k -u "admin:admin" -X POST "https://localhost:9200/login-management/_doc" -H 'Content-Type: application/json' -d '{
  "username": "owner",
  "password": "owner"
}'