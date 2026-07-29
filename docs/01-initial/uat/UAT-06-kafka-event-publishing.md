# UAT-06: Kafka Event Publishing

**Covers**: INGEST-5
**Type**: Event Flow Integration Test
**Effort**: ~10 minutes

## Objective

Verify that Kafka events are published when documents are ingested, including retry and DLQ (Dead Letter Queue) behavior.

## Prerequisites

- UAT-02 passes (document upload works)
- Kafka service is running and accessible

## Steps

### Step 1: Verify Kafka Topics Exist

```bash
docker exec $(docker-compose ps -q kafka) kafka-topics.sh \
  --list --bootstrap-server localhost:9092
```

**Expected**: Topics listed include:
- `document.ingested` — main ingestion event stream
- `dlq` — dead letter queue for failed events

### Step 2: Start a Kafka Consumer

```bash
# In Terminal A — start a consumer for the ingestion topic
docker exec -it $(docker-compose ps -q kafka) kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic document.ingested \
  --from-beginning \
  --property print.key=true \
  --property print.value=true \
  --property print.timestamp=true
```

### Step 3: Trigger an Upload Event

```bash
# In Terminal B — upload a document to trigger the event
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@tests/test_data/sample_regulation.pdf" | python3 -m json.tool
```

### Step 4: Verify Event in Consumer Output

The consumer in Terminal A should receive a JSON event like:
```json
key: <document-uuid>
value: {
  "document_id": "<uuid>",
  "hash": "<sha256>",
  "source_path": "documents/<sha256>/sample_regulation.pdf",
  "filename": "sample_regulation.pdf",
  "content_type": "application/pdf",
  "file_size": 12345,
  "requestor_id": null,
  "event_type": "document.ingested",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Step 5: Verify Event Publisher Service

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.event_publisher import PipelinePublisher

try:
    publisher = PipelinePublisher()

    # Verify producer is connected
    health = publisher.health()
    print(f"Producer status: {health}")

    # Try publishing a test event
    result = publisher.publish_ingestion_event(
        document_id="test-uuid",
        hash="abc123",
        source_path="documents/test/sample.pdf",
        filename="sample.pdf",
    )
    print(f"Publish result: {result}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
PYEOF
```

### Step 6: Verify DLQ Topics

```bash
# Check DLQ topic exists
docker exec $(docker-compose ps -q kafka) kafka-topics.sh \
  --describe --bootstrap-server localhost:9092 \
  --topic dlq
```

**Expected**: DLQ topic with proper partition and replication configuration.

### Step 7: Verify DLQ on Kafka Failure (Service-Level)

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.kafka.producer import KafkaProducer

producer = KafkaProducer()

# Verify producer configuration
print(f"Bootstrap servers: {producer.brokers}")
print(f"Retry config: {producer.retry_config}")

# Verify DLQ topic name
print(f"DLQ topic: {producer.dlq_topic}")

# Health check
try:
    status = producer.health()
    print(f"Health: {status}")
except Exception as e:
    print(f"Health check (expected if Kafka not available): {e}")
PYEOF
```

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Topic listing | `kafka-topics.sh --list` | `document.ingested` and `dlq` topics exist |
| 2 | Consumer output | Event received after upload | JSON event with all required fields |
| 3 | Event fields | Event structure | document_id, hash, source_path, filename, content_type, file_size |
| 4 | Publisher service | `PipelinePublisher` instantiation | Producer connected, health OK |
| 5 | DLQ topic | Topic exists | DLQ topic with partitions configured |
| 6 | Producer config | Retry + DLQ settings | Retry configured, DLQ topic name set |

## Verification

- [ ] Kafka `document.ingested` topic exists and accepts messages
- [ ] Publishing a document produces a visible Kafka event
- [ ] Event JSON contains all required fields (document_id, hash, source_path, filename, content_type, file_size)
- [ ] DLQ topic exists for failed event handling
- [ ] PipelinePublisher can be instantiated and produces events successfully

## Pass/Fail Criteria

- **PASS**: Steps 1-6 all succeed — topics exist, events are published and consumed with correct structure
- **FAIL**: Topics missing, events not produced, or event structure incomplete

## Notes

- The Kafka consumer in Step 2 must be started BEFORE the upload in Step 3, otherwise the event may be missed
- If Kafka is not available during testing, Steps 5-6 verify the producer configuration without requiring live connectivity
