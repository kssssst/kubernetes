#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Checking forbidden archive/key files ==="

if find "$ROOT" \
  -type f \
  \( -name '*.tar' \
     -o -name '*.pem' \
     -o -name '*.key' \
     -o -name 'admin.conf' \
     -o -name 'kubeconfig' \) \
  -print | grep -q .; then

    echo "ERROR: forbidden or sensitive files found"
    find "$ROOT" \
      -type f \
      \( -name '*.tar' \
         -o -name '*.pem' \
         -o -name '*.key' \
         -o -name 'admin.conf' \
         -o -name 'kubeconfig' \) \
      -print

    exit 1
fi

echo "OK"

echo
echo "=== Checking latest image tag ==="

if grep -Rni \
  --exclude-dir=.git \
  --exclude='*.md' \
  ':latest' \
  "$ROOT"; then

    echo "ERROR: latest tag found"
    exit 1
fi

echo "OK: latest tag is not used"

echo
echo "=== Checking Kubernetes manifests ==="

for file in "$ROOT"/k8s/*.yaml; do
  echo "Checking: $file"
  kubectl apply --dry-run=client -f "$file" >/dev/null
done

echo
echo "Repository validation completed successfully."
