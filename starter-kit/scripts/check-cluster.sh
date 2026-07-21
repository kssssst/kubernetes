#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${1:-homework}"

echo "=== NODES ==="
kubectl get nodes -o wide

echo
echo "=== APPLICATION WORKLOADS ==="
kubectl get deployment,statefulset -n "$NAMESPACE"

echo
echo "=== APPLICATION PODS ==="
kubectl get pods -n "$NAMESPACE" -o wide

echo
echo "=== SERVICES ==="
kubectl get svc -n "$NAMESPACE"

echo
echo "=== ENDPOINT SLICES ==="
kubectl get endpointslice -n "$NAMESPACE"

echo
echo "=== STORAGE ==="
kubectl get pvc -n "$NAMESPACE"
kubectl get pv

echo
echo "=== INGRESS ==="
kubectl get ingress -n "$NAMESPACE"

echo
echo "=== NETWORK POLICIES ==="
kubectl get networkpolicy -n "$NAMESPACE"

echo
echo "=== NON-RUNNING PODS ==="
kubectl get pods -A \
  | grep -v Running \
  | grep -v Completed \
  || true
