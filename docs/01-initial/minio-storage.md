# INFRA-3: MinIO Object Storage Configuration

This document describes the MinIO object storage configuration for the RCKG platform.

## Overview

MinIO is an S3-compatible object storage service used for:
- Regulatory documents (PDFs, policies)
- Markdown conversions
- Evidence artifacts
- Temporary/unstructured data

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MinIO Object Storage                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │   source-regulations │  │        minio-data            │ │
│  │   (WORM policy)      │  │    (temporary storage)       │ │
│  │                      │  │                              │ │
│  │  - Regulatory PDFs   │  │  - Processing intermediates  │ │
│  │  - Policy documents  │  │  - Test data                 │ │
│  │  - Evidence          │  │  - Unstructured files        │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ markdown-conversions │  │    evidence-artifacts        │ │
│  │                      │  │                              │ │
│  │  - Parsed documents  │  │  - Control evidence          │ │
│  │  - Markdown files    │  │  - Audit artifacts           │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Bucket Configuration

### source-regulations (WORM)

| Property | Value |
|----------|-------|
| **Purpose** | Regulatory documents that must not be tampered with |
| **WORM Policy** | Yes - Delete and overwrite operations denied |
| **Versioning** | Enabled - Full audit trail |
| **Access** | Read-only after upload |

**Use Cases:**
- Original regulatory PDFs
- Policy documents
- Evidence artifacts that must be immutable

### minio-data (Temporary)

| Property | Value |
|----------|-------|
| **Purpose** | Temporary and unstructured storage |
| **WORM Policy** | No - Normal read/write/delete allowed |
| **Versioning** | Enabled - Backup capability |
| **Access** | Full CRUD operations |

**Use Cases:**
- Processing intermediates
- Test data
- Temporary file storage

### markdown-conversions

| Property | Value |
|----------|-------|
| **Purpose** | Parsed Markdown document storage |
| **WORM Policy** | No - May need updates |
| **Versioning** | Enabled |
| **Access** | Full CRUD operations |

**Use Cases:**
- MinerU/PDF-to-Markdown output
- Preprocessed documents for ingestion

### evidence-artifacts

| Property | Value |
|----------|-------|
| **Purpose** | Control evidence documentation |
| **WORM Policy** | No - May need updates |
| **Versioning** | Enabled |
| **Access** | Full CRUD operations |

**Use Cases:**
- Control test evidence
- Audit artifacts
- Compliance documentation

## Access Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ROOT_USER` | `rckg_admin` | Access key |
| `MINIO_ROOT_PASSWORD` | `rckg_secret_password` | Secret key |
| `MINIO_PORT` | `9000` | API port |
| `MINIO_CONSOLE_PORT` | `9001` | Web console port |
| `MINIO_ENDPOINT_URL` | `http://localhost:9000` | API endpoint |

### API Endpoints

| Service | URL | Authentication |
|---------|-----|----------------|
| **S3 API** | `http://localhost:9000` | Access key / Secret key |
| **Web Console** | `http://localhost:9001` | Browser login |

### Web Console Access

1. Navigate to `http://localhost:9001`
2. Login with:
   - **Username:** `rckg_admin`
   - **Password:** `rckg_secret_password`
3. View buckets, upload/download files, configure policies

## WORM (Write-Once-Read-Many) Policy

The `source-regulations` bucket enforces WORM compliance:

### What WORM Means

- **Write:** Files can be uploaded once
- **Read:** Files can be downloaded any number of times
- **No Modify:** Files cannot be overwritten
- **No Delete:** Files cannot be deleted

### Enforcement Mechanism

WORM is enforced via MinIO bucket policy that denies:
- `s3:DeleteObject` - Prevents file deletion
- `s3:PutObjectVersion` - Prevents file overwrite

### Verification

```bash
# Check bucket policy
mc admin policy info rckg-source-worm

# Attempt to delete (should fail)
mc rm rckg/source-regulations/document.pdf
# Error: Method Not Allowed
```

## Bucket Initialization

### Automated (Docker Compose)

Buckets are automatically created by the `minio-init` service in `docker-compose.yml`:

```yaml
minio-init:
  image: minio/mc:latest
  depends_on:
    minio:
      condition: service_healthy
  entrypoint: >
    /bin/sh -c "
    until mc config host add rckg http://minio:9000 rckg_admin rckg_secret_password; do
      echo 'Waiting for MinIO...' && sleep 2;
    done;
    mc mb rckg/source-regulations --ignore-existing;
    mc mb rckg/minio-data --ignore-existing;
    mc mb rckg/markdown-conversions --ignore-existing;
    mc mb rckg/evidence-artifacts --ignore-existing;
    echo 'MinIO buckets initialized';
    "
```

### Manual Initialization

```bash
# Navigate to infra directory
cd /home/zackchow/coding/rckg/infra/minio

# Run initialization script
./init_buckets.sh
```

### Using MinIO CLI (mc)

```bash
# Configure MinIO CLI
mc alias set rckg http://localhost:9000 rckg_admin rckg_secret_password

# Create buckets
mc mb rckg/source-regulations
mc mb rckg/minio-data
mc mb rckg/markdown-conversions
mc mb rckg/evidence-artifacts

# Enable versioning
mc version enable rckg/source-regulations
mc version enable rckg/minio-data
mc version enable rckg/markdown-conversions
mc version enable rckg/evidence-artifacts

# List buckets
mc ls rckg

# Upload file
mc upload document.pdf rckg/source-regulations/

# Download file
mc download rckg/source-regulations/document.pdf

# List files
mc ls rckg/source-regulations
```

## Python SDK Usage

### Basic Usage

```python
from backend.app.storage import get_minio_storage

# Get storage instance
storage = get_minio_storage()

# Upload a file
with open("regulation.pdf", "rb") as f:
    storage.upload_file(
        bucket="source-regulations",
        key="2024/dora/regulation.pdf",
        file_obj=f,
        content_type="application/pdf"
    )

# Download a file
content = storage.download_file(
    bucket="source-regulations",
    key="2024/dora/regulation.pdf"
)

# List files
files = storage.list_files(
    bucket="source-regulations",
    prefix="2024/dora/"
)

# Check if file exists
if storage.file_exists("source-regulations", "2024/dora/regulation.pdf"):
    print("File exists")

# Get file metadata
metadata = storage.get_file_metadata(
    bucket="source-regulations",
    key="2024/dora/regulation.pdf"
)
print(f"Size: {metadata['size']} bytes")
```

### Presigned URLs

```python
# Generate presigned URL for temporary access
url = storage.get_presigned_url(
    bucket="source-regulations",
    key="2024/dora/regulation.pdf",
    expires_in=3600  # 1 hour
)
print(f"Download URL: {url}")
```

### Direct Bucket Operations

```python
from backend.app.storage import MinIOStorage

# Create storage instance
storage = MinIOStorage(
    endpoint_url="http://localhost:9000",
    access_key="rckg_admin",
    secret_key="rckg_secret_password"
)

# Create a new bucket
storage.create_bucket("custom-bucket")

# Delete a bucket (must be empty)
storage.delete_bucket("custom-bucket")

# List all buckets
buckets = storage.list_buckets()
print(f"Available buckets: {buckets}")
```

## Security Considerations

### Production Deployment

1. **Use strong passwords:** Generate random strings for `MINIO_ROOT_PASSWORD`
2. **Enable TLS:** Configure HTTPS for both API and console
3. **Network isolation:** Restrict access to internal networks only
4. **Audit logging:** Enable MinIO audit logs for access tracking
5. **Backup strategy:** Implement regular backups of MinIO data

### WORM Enforcement Limitations

- WORM policy is applied at the bucket level
- MinIO admin can bypass WORM with admin credentials
- For true audit compliance, combine with IAM restrictions

## Testing

### Run Integration Tests

```bash
cd /home/zackchow/coding/rckg/backend
pytest tests/test_infra_3_minio_storage.py -v
```

### Manual Verification

```bash
# Test S3 API
curl -i -X PUT http://localhost:9000/test-bucket \
  -H "Authorization: AWS4-HMAC-SHA256 ..."

# Test WORM policy
mc rm rckg/source-regulations/test-file.txt
# Should fail with "Method Not Allowed"
```

## See Also

- [TRD Section 4.2: Infrastructure Services](./master_tech_req.md)
- [TRD Section 11.3: MinIO Configuration](./master_tech_req.md)
- [Docker Compose Configuration](../../docker-compose.yml)
