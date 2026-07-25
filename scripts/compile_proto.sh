#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="proto"
GEN_PY="proto/gen/python"
GEN_GO="proto/gen/go"

mkdir -p "$GEN_PY" "$GEN_GO"

# Python
python -m grpc_tools.protoc \
  -I "$PROTO_DIR" \
  --python_out="$GEN_PY" \
  --grpc_python_out="$GEN_PY" \
  "$PROTO_DIR"/*.proto

# Go
protoc \
  -I "$PROTO_DIR" \
  --go_out="$GEN_GO" \
  --go_opt=paths=source_relative \
  --go-grpc_out="$GEN_GO" \
  --go-grpc_opt=paths=source_relative \
  "$PROTO_DIR"/*.proto

echo "Proto compilation done"
