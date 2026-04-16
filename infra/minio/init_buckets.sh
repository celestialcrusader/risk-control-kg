#!/bin/bash
# MinIO Bucket Initialization Script
#
# This script creates and configures all MinIO buckets for the RCKG platform.
# Run this after MinIO is running to ensure all buckets are properly configured.

set -e

# Configuration
MINIO_HOST="${MINIO_HOST:-localhost:9000}"
MINIO_ROOT_USER="${MINIO_ROOT_USER:-rckg_admin}"
MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-rckg_secret_password}"
MINIO_ALIAS="rckg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for MinIO to be ready
wait_for_minio() {
    log_info "Waiting for MinIO to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "http://${MINIO_HOST}/minio/health/live" > /dev/null 2>&1; then
            log_info "MinIO is ready"
            return 0
        fi
        echo -ne "\r  Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done

    log_error "MinIO did not become ready within timeout"
    return 1
}

# Configure MinIO CLI
configure_mc() {
    log_info "Configuring MinIO CLI..."
    mc alias set "${MINIO_ALIAS}" "http://${MINIO_HOST}" "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
    log_info "MinIO CLI configured"
}

# Create buckets
create_buckets() {
    log_info "Creating buckets..."

    # source-regulations bucket (WORM policy)
    log_info "Creating 'source-regulations' bucket (WORM policy)..."
    mc mb "${MINIO_ALIAS}"/source-regulations || log_warn "Bucket 'source-regulations' may already exist"

    # minio-data bucket (no WORM policy)
    log_info "Creating 'minio-data' bucket..."
    mc mb "${MINIO_ALIAS}"/minio-data || log_warn "Bucket 'minio-data' may already exist"

    # markdown-conversions bucket
    log_info "Creating 'markdown-conversions' bucket..."
    mc mb "${MINIO_ALIAS}"/markdown-conversions || log_warn "Bucket 'markdown-conversions' may already exist"

    # evidence-artifacts bucket
    log_info "Creating 'evidence-artifacts' bucket..."
    mc mb "${MINIO_ALIAS}"/evidence-artifacts || log_warn "Bucket 'evidence-artifacts' may already exist"

    log_info "All buckets created"
}

# Enable versioning on all buckets
enable_versioning() {
    log_info "Enabling versioning on all buckets..."

    local buckets=("source-regulations" "minio-data" "markdown-conversions" "evidence-artifacts")

    for bucket in "${buckets[@]}"; do
        log_info "Enabling versioning on '${bucket}'..."
        mc version enable "${MINIO_ALIAS}/${bucket}"
    done

    log_info "Versioning enabled on all buckets"
}

# Apply WORM policy to source-regulations bucket
apply_worm_policy() {
    log_info "Applying WORM policy to 'source-regulations' bucket..."

    # Create WORM policy configuration
    local worm_policy_json='{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PreventDeleteAndOverwrite",
                "Effect": "Deny",
                "Principal": {"AWS": ["*"]},
                "Action": [
                    "s3:DeleteObject",
                    "s3:PutObjectVersion"
                ],
                "Resource": [
                    "arn:aws:s3:::source-regulations/*"
                ]
            }
        ]
    }'

    # Write policy to temp file
    local policy_file=$(mktemp)
    echo "$worm_policy_json" > "$policy_file"

    # Apply policy
    mc anonymous set "${MINIO_ALIAS}/source-regulations" < "$policy_file"

    # Cleanup
    rm -f "$policy_file"

    log_info "WORM policy applied to 'source-regulations'"
}

# Verify configuration
verify_configuration() {
    log_info "Verifying configuration..."

    local buckets=("source-regulations" "minio-data" "markdown-conversions" "evidence-artifacts")

    for bucket in "${buckets[@]}"; do
        if mc ls "${MINIO_ALIAS}/${bucket}" > /dev/null 2>&1; then
            log_info "Bucket '${bucket}' is accessible"
        else
            log_error "Bucket '${bucket}' is not accessible"
            return 1
        fi
    done

    log_info "All buckets verified"
}

# Print current bucket status
show_bucket_status() {
    log_info "Current bucket status:"
    mc ls "${MINIO_ALIAS}"
}

# Main execution
main() {
    log_info "Starting MinIO bucket initialization..."
    echo ""

    # Wait for MinIO
    wait_for_minio || exit 1

    # Configure MC
    configure_mc

    # Create buckets
    create_buckets

    # Enable versioning
    enable_versioning

    # Apply WORM policy (optional, requires admin access)
    apply_worm_policy

    # Verify
    verify_configuration

    echo ""
    log_info "MinIO bucket initialization complete!"
    echo ""

    show_bucket_status
}

# Run main
main "$@"
