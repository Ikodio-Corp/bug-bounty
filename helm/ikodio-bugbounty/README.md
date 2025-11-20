# IKODIO BugBounty Helm Chart

This Helm chart deploys the complete IKODIO BugBounty platform on Kubernetes.

## Prerequisites

- Kubernetes 1.24+
- Helm 3.8+
- PV provisioner support in the underlying infrastructure
- Ingress controller (NGINX recommended)
- cert-manager (optional, for automatic SSL/TLS)

## Installing the Chart

### Quick Start

```bash
# Add the chart repository (if using a chart repository)
helm repo add ikodio https://charts.ikodio.com
helm repo update

# Install the chart with the release name ikodio-bugbounty
helm install ikodio-bugbounty ikodio/ikodio-bugbounty
```

### From Local Directory

```bash
# Install from local directory
helm install ikodio-bugbounty ./helm/ikodio-bugbounty

# Install with custom values
helm install ikodio-bugbounty ./helm/ikodio-bugbounty -f custom-values.yaml

# Install in a specific namespace
helm install ikodio-bugbounty ./helm/ikodio-bugbounty --namespace ikodio --create-namespace
```

## Uninstalling the Chart

```bash
helm uninstall ikodio-bugbounty
```

## Configuration

The following table lists the configurable parameters of the IKODIO BugBounty chart and their default values.

### Global Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace | `ikodio-bugbounty` |
| `global.environment` | Environment name | `production` |
| `global.releaseVersion` | Application version | `1.0.0` |

### Backend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicaCount` | Number of backend replicas | `3` |
| `backend.image.repository` | Backend image repository | `ikodio/bugbounty-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.resources.requests.memory` | Memory request | `512Mi` |
| `backend.resources.requests.cpu` | CPU request | `500m` |
| `backend.resources.limits.memory` | Memory limit | `2Gi` |
| `backend.resources.limits.cpu` | CPU limit | `2000m` |
| `backend.autoscaling.enabled` | Enable HPA | `true` |
| `backend.autoscaling.minReplicas` | Minimum replicas | `3` |
| `backend.autoscaling.maxReplicas` | Maximum replicas | `10` |

### Frontend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `ikodio/bugbounty-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.autoscaling.enabled` | Enable HPA | `true` |
| `frontend.autoscaling.minReplicas` | Minimum replicas | `2` |
| `frontend.autoscaling.maxReplicas` | Maximum replicas | `5` |

### Database Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL | `true` |
| `postgresql.persistence.size` | PostgreSQL PVC size | `50Gi` |
| `postgresql.auth.database` | Database name | `ikodio_bugbounty` |
| `postgresql.auth.username` | Database username | `ikodio_user` |

### Redis Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis | `true` |
| `redis.persistence.size` | Redis PVC size | `10Gi` |
| `redis.config.maxmemory` | Max memory | `2gb` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `ingress.tls` | TLS configuration | See values.yaml |

### Monitoring Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `monitoring.prometheus.enabled` | Enable Prometheus | `true` |
| `monitoring.grafana.enabled` | Enable Grafana | `true` |

### Logging Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `logging.elasticsearch.enabled` | Enable Elasticsearch | `true` |
| `logging.logstash.enabled` | Enable Logstash | `true` |
| `logging.kibana.enabled` | Enable Kibana | `true` |
| `logging.filebeat.enabled` | Enable Filebeat | `true` |
| `logging.metricbeat.enabled` | Enable Metricbeat | `true` |

### Sentry Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `sentry.enabled` | Enable Sentry | `true` |
| `sentry.tracesSampleRate` | Traces sample rate | `0.1` |

## Custom Values File

Create a `custom-values.yaml` file to override default values:

```yaml
# custom-values.yaml
global:
  environment: staging

backend:
  replicaCount: 2
  autoscaling:
    maxReplicas: 5

postgresql:
  persistence:
    size: 100Gi

secrets:
  postgresPassword: "my-secure-password"
  secretKey: "my-secret-key"
  openaiApiKey: "sk-..."
  githubClientId: "Iv1..."
  githubClientSecret: "..."
  stripeSecretKey: "sk_..."
```

Install with custom values:

```bash
helm install ikodio-bugbounty ./helm/ikodio-bugbounty -f custom-values.yaml
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade ikodio-bugbounty ./helm/ikodio-bugbounty -f custom-values.yaml

# Upgrade with new image tag
helm upgrade ikodio-bugbounty ./helm/ikodio-bugbounty --set backend.image.tag=1.1.0
```

## Rollback

```bash
# List releases
helm history ikodio-bugbounty

# Rollback to previous version
helm rollback ikodio-bugbounty

# Rollback to specific revision
helm rollback ikodio-bugbounty 2
```

## Accessing Services

### Port Forwarding

```bash
# Backend API
kubectl port-forward svc/ikodio-bugbounty-backend 8000:8000

# Frontend
kubectl port-forward svc/ikodio-bugbounty-frontend 3000:3000

# Grafana
kubectl port-forward svc/ikodio-bugbounty-grafana 3000:3000

# Kibana
kubectl port-forward svc/ikodio-bugbounty-kibana 5601:5601
```

### Ingress

If ingress is enabled and configured correctly:

- Frontend: https://ikodio.com or https://app.ikodio.com
- Backend API: https://api.ikodio.com

## Production Deployment Checklist

1. **Update Secrets**
   - Set strong passwords for all services
   - Configure API keys for all integrations
   - Store secrets in external secret management (e.g., HashiCorp Vault)

2. **Configure DNS**
   - Point domains to ingress controller
   - Configure SSL/TLS certificates

3. **Storage**
   - Configure appropriate storage classes
   - Set up backup solutions

4. **Monitoring**
   - Configure Prometheus alerts
   - Set up Grafana dashboards
   - Configure Sentry alerts

5. **Security**
   - Enable network policies
   - Configure RBAC
   - Enable pod security policies

6. **Scaling**
   - Adjust resource limits based on load
   - Configure autoscaling parameters
   - Set up cluster autoscaling

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n ikodio-bugbounty
```

### View Pod Logs

```bash
# Backend logs
kubectl logs -l app=backend -n ikodio-bugbounty

# Frontend logs
kubectl logs -l app=frontend -n ikodio-bugbounty
```

### Describe Resources

```bash
# Describe deployment
kubectl describe deployment ikodio-bugbounty-backend -n ikodio-bugbounty

# Describe pod
kubectl describe pod <pod-name> -n ikodio-bugbounty
```

### Common Issues

**Pods not starting**: Check resource limits and node capacity
**Database connection errors**: Verify PostgreSQL is running and accessible
**Ingress not working**: Check ingress controller and DNS configuration
**Out of memory**: Increase memory limits or add more nodes

## Support

For issues and questions:
- Documentation: https://docs.ikodio.com
- GitHub Issues: https://github.com/ikodio/bugbounty/issues
- Email: support@ikodio.com
