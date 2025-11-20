#!/bin/bash

set -e

NAMESPACE="ikodio-bugbounty"
CONTEXT="${1:-}"

if [ -n "$CONTEXT" ]; then
    kubectl config use-context "$CONTEXT"
fi

echo "Deploying Beats (Filebeat and Metricbeat) to namespace: $NAMESPACE"

echo "Deploying Filebeat DaemonSet..."
kubectl apply -f k8s/filebeat-daemonset.yaml

echo "Waiting for Filebeat to be ready..."
kubectl rollout status daemonset/filebeat -n $NAMESPACE --timeout=300s

echo "Deploying Metricbeat DaemonSet..."
kubectl apply -f k8s/metricbeat-daemonset.yaml

echo "Waiting for Metricbeat to be ready..."
kubectl rollout status daemonset/metricbeat -n $NAMESPACE --timeout=300s

echo ""
echo "Beats deployment completed successfully!"
echo ""
echo "Check Filebeat status:"
echo "  kubectl get daemonset filebeat -n $NAMESPACE"
echo "  kubectl logs -l app=filebeat -n $NAMESPACE"
echo ""
echo "Check Metricbeat status:"
echo "  kubectl get daemonset metricbeat -n $NAMESPACE"
echo "  kubectl logs -l app=metricbeat -n $NAMESPACE"
echo ""
echo "Verify logs in Elasticsearch:"
echo "  kubectl port-forward svc/elasticsearch 9200:9200 -n $NAMESPACE"
echo "  curl http://localhost:9200/_cat/indices"
echo ""
echo "View logs in Kibana:"
echo "  kubectl port-forward svc/kibana 5601:5601 -n $NAMESPACE"
echo "  Open http://localhost:5601"
