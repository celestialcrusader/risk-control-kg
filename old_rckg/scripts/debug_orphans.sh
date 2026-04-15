#!/bin/bash
curl -s -X POST http://localhost:7474/db/neo4j/tx/commit \
  -H "Authorization: Basic bmVvNGo6cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"statements": [{"statement": "MATCH (r:Requirement) WHERE NOT (r)<-[:DEFINES]-(:Framework) RETURN r.id, r.title, r.description LIMIT 5"}]}'
