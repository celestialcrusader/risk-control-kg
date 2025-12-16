#!/bin/bash
# Check ALL Framework nodes
echo "Checking Frameworks:"
curl -s -X POST http://localhost:7474/db/neo4j/tx/commit \
  -H "Authorization: Basic bmVvNGo6cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"statements": [{"statement": "MATCH (f:Framework) RETURN f.id, f.title, f.name LIMIT 10"}]}'
echo ""
echo "Checking Requirements count:"
curl -s -X POST http://localhost:7474/db/neo4j/tx/commit \
  -H "Authorization: Basic bmVvNGo6cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"statements": [{"statement": "MATCH (r:Requirement) RETURN count(r)"}]}'
