#!/bin/bash
# Helper script to test the Ingestion API

# 1. Create a dummy CSV file
echo "Creating dummy_uat.csv..."
echo "nist_ctrl_id,ctrl_grp,ctrl_txt" > dummy_uat.csv
echo "UAT-001,User Acceptance,This is a test control created during UAT to verify ingestion." >> dummy_uat.csv

# 2. calling the API
echo "Uploading dummy_uat.csv to http://localhost:8000/api/ingest/ ..."
response=$(curl -s -X POST "http://localhost:8000/api/ingest/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@dummy_uat.csv;type=text/csv")

# 3. Print response
echo "Response:"
echo $response

# 4. Clean up
rm dummy_uat.csv
