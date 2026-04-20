"""
Kafka topic registry for RCKG.

Defines all Kafka topics used in the event-driven pipeline.
"""

TOPICS = [
    {
        "name": "document.ingested",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers ingestion workflow",
    },
    {
        "name": "document.converted",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers chunking workflow",
    },
    {
        "name": "document.chunked",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers bronze layer storage",
    },
    {
        "name": "document.bronzed",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers extraction workflow",
    },
    {
        "name": "extraction.completed",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers extraction validation workflow",
    },
    {
        "name": "validation.completed",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers graph build workflow",
    },
    {
        "name": "mapping.completed",
        "retention_seconds": 604800,  # 7 days
        "partitions": 3,
        "purpose": "Triggers gap detection",
    },
    {
        "name": "coverage.alert",
        "retention_seconds": 2592000,  # 30 days
        "partitions": 1,
        "purpose": "Alerting on coverage threshold breach",
    },
]
