#!/bin/bash
# Create Kafka topics for RCKG event-driven pipeline
# Run after Kafka container is healthy:
#   docker exec rckg-kafka /bin/bash /tmp/create-topics.sh
set -euo pipefail

BOOTSTRAP="localhost:9092"

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
until echo | nc -w 2 localhost 9092 2>/dev/null; do
    echo "  Kafka not ready yet..."
    sleep 2
done
echo "Kafka is ready."

TOPICS=(
    "document.ingested:604800:3"
    "extraction.completed:604800:3"
    "validation.completed:604800:3"
    "mapping.completed:604800:3"
    "coverage.alert:2592000:1"
)

for entry in "${TOPICS[@]}"; do
    IFS=':' read -r name retention partitions <<< "$entry"
    if kafka-topics.sh --bootstrap-server "$BOOTSTRAP" --list 2>/dev/null | grep -q "^${name}$"; then
        echo "Topic '$name' already exists, skipping."
    else
        echo "Creating topic '$name' (partitions=$partitions, retention=$retention seconds)..."
        kafka-topics.sh --bootstrap-server "$BOOTSTRAP" \
            --create \
            --topic "$name" \
            --partitions "$partitions" \
            --config retention.ms=$((retention * 1000)) \
            --if-not-exists
    fi
done

echo "All topics created."
