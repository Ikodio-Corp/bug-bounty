#!/bin/bash

set -e

echo "Deploying IKODIO BugBounty Platform to Kubernetes"
echo "================================================="

NAMESPACE="ikodio-bugbounty"
CONTEXT=${1:-"production"}

echo "Using context: $CONTEXT"
kubectl config use-context $CONTEXT

echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "Creating secrets and configmaps..."
kubectl apply -f k8s/configmap.yaml

echo "Deploying PostgreSQL..."
kubectl apply -f k8s/postgres-statefulset.yaml
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

echo "Deploying Redis..."
kubectl apply -f k8s/redis-deployment.yaml
echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=180s

echo "Deploying Backend..."
kubectl apply -f k8s/backend-deployment.yaml
echo "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=300s

echo "Deploying Celery Workers..."
kubectl apply -f k8s/celery-deployment.yaml

echo "Deploying Frontend..."
kubectl apply -f k8s/frontend-deployment.yaml
echo "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=180s

echo "Setting up monitoring..."
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml

echo "Configuring Ingress..."
kubectl apply -f k8s/ingress.yaml

echo ""
echo "Deployment Status:"
echo "=================="
kubectl get pods -n $NAMESPACE
echo ""
kubectl get services -n $NAMESPACE
echo ""
kubectl get ingress -n $NAMESPACE

echo ""
echo "================================================="
echo "Deployment completed successfully!"
echo ""
echo "Access URLs:"
echo "  API: https://api.ikodio.com"
echo "  App: https://app.ikodio.com"
echo "  Grafana: https://grafana.ikodio.com"
echo ""
echo "To check pod status:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "To view logs:"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
echo ""
echo "To scale deployments:"
echo "  kubectl scale deployment/backend --replicas=5 -n $NAMESPACE"
echo "================================================="
