#!/bin/bash

set -e

CHART_DIR="helm/ikodio-bugbounty"
RELEASE_NAME="ikodio-bugbounty"
NAMESPACE="ikodio-bugbounty"

echo "IKODIO BugBounty Helm Chart Installation"
echo "========================================="
echo ""

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "Error: Helm is not installed. Please install Helm 3.8+ first."
    echo "Visit: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check helm version
HELM_VERSION=$(helm version --short | grep -oE 'v[0-9]+\.[0-9]+' | cut -d'v' -f2)
HELM_MAJOR=$(echo $HELM_VERSION | cut -d'.' -f1)
HELM_MINOR=$(echo $HELM_VERSION | cut -d'.' -f2)

if [ "$HELM_MAJOR" -lt 3 ] || ([ "$HELM_MAJOR" -eq 3 ] && [ "$HELM_MINOR" -lt 8 ]); then
    echo "Error: Helm version 3.8+ is required. Current version: $HELM_VERSION"
    exit 1
fi

echo "Using Helm version: $HELM_VERSION"
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: kubectl is not configured or cluster is not accessible"
    exit 1
fi

echo "Connected to Kubernetes cluster"
echo ""

# Create namespace if it doesn't exist
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
else
    echo "Namespace $NAMESPACE already exists"
fi
echo ""

# Check if release already exists
if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
    echo "Release $RELEASE_NAME already exists"
    read -p "Do you want to upgrade it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ACTION="upgrade"
    else
        echo "Installation cancelled"
        exit 0
    fi
else
    ACTION="install"
fi

# Check if custom values file exists
CUSTOM_VALUES=""
if [ -f "helm-values-production.yaml" ]; then
    read -p "Found helm-values-production.yaml. Use it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        CUSTOM_VALUES="-f helm-values-production.yaml"
    fi
fi

# Dry run first
echo "Running dry-run to validate configuration..."
if [ "$ACTION" == "install" ]; then
    helm install $RELEASE_NAME $CHART_DIR \
        --namespace $NAMESPACE \
        --dry-run --debug \
        $CUSTOM_VALUES > /dev/null
else
    helm upgrade $RELEASE_NAME $CHART_DIR \
        --namespace $NAMESPACE \
        --dry-run --debug \
        $CUSTOM_VALUES > /dev/null
fi

if [ $? -ne 0 ]; then
    echo "Dry-run failed. Please check the configuration."
    exit 1
fi

echo "Dry-run successful"
echo ""

# Confirm installation
echo "Ready to $ACTION IKODIO BugBounty"
echo "Release name: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"
echo "Chart directory: $CHART_DIR"
[ -n "$CUSTOM_VALUES" ] && echo "Custom values: $CUSTOM_VALUES"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

# Install or upgrade
echo "Starting $ACTION..."
if [ "$ACTION" == "install" ]; then
    helm install $RELEASE_NAME $CHART_DIR \
        --namespace $NAMESPACE \
        --create-namespace \
        --wait \
        $CUSTOM_VALUES
else
    helm upgrade $RELEASE_NAME $CHART_DIR \
        --namespace $NAMESPACE \
        --wait \
        $CUSTOM_VALUES
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "Installation completed successfully!"
    echo "========================================="
    echo ""
    echo "Check status:"
    echo "  helm status $RELEASE_NAME -n $NAMESPACE"
    echo ""
    echo "View all resources:"
    echo "  kubectl get all -n $NAMESPACE"
    echo ""
    echo "Access services via port-forward:"
    echo "  kubectl port-forward svc/$RELEASE_NAME-backend 8000:8000 -n $NAMESPACE"
    echo "  kubectl port-forward svc/$RELEASE_NAME-frontend 3000:3000 -n $NAMESPACE"
    echo ""
    echo "View logs:"
    echo "  kubectl logs -l app=backend -n $NAMESPACE"
    echo "  kubectl logs -l app=frontend -n $NAMESPACE"
    echo ""
else
    echo ""
    echo "Installation failed. Check the error messages above."
    exit 1
fi
