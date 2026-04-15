#!/bin/bash
curl -s -X POST http://localhost:7474/db/neo4j/tx/commit \
  -H "Authorization: Basic bmVvNGo6cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"statements": [{"statement": "MATCH (f:Framework {id: \"IMPORTED-PDF:-NIST.AI.600-1.PDF\"})-[:DEFINES]->(r:Requirement) RETURN count(r)"}]}'
