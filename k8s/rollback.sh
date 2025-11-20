#!/bin/bash

set -e

echo "Rolling Back IKODIO BugBounty Platform"
echo "======================================"

NAMESPACE="ikodio-bugbounty"
DEPLOYMENT=${1:-"backend"}

echo "Rolling back deployment: $DEPLOYMENT"

kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE

echo "Checking rollback status..."
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE

echo ""
echo "Rollback completed!"
echo ""
echo "Current revision:"
kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE
