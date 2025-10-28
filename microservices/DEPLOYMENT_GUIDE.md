# Deployment Guide - AutoPro Microservices

## 🚀 Deployment Options

1. **Local Development** - Docker Compose
2. **Staging/Production** - Kubernetes (AWS EKS, GKE, or AKS)
3. **Hybrid** - Docker Swarm

---

## 1. Local Development Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 50GB disk space

### Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd microservices

# 2. Copy environment variables
cp .env.example .env

# 3. Edit configuration
nano .env

# Required variables:
# - DATABASE_URL
# - REDIS_URL
# - RABBITMQ_URL
# - External API keys (optional for testing)

# 4. Build and start all services
docker-compose up --build -d

# 5. Verify services
docker-compose ps

# Expected output: All services "Up" and "healthy"

# 6. Check logs
docker-compose logs -f

# 7. Test endpoints
curl http://localhost:8001/health  # Lead Service
curl http://localhost:8000/api/leads  # Via Kong Gateway

# 8. Access monitoring
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:16686  # Jaeger

# 9. Stop services
docker-compose down

# 10. Clean up (including volumes)
docker-compose down -v
```

### Troubleshooting

#### Services won't start

```bash
# Check logs
docker-compose logs <service-name>

# Check resource usage
docker stats

# Restart specific service
docker-compose restart lead-service
```

#### Port conflicts

```bash
# Check what's using port
lsof -i :8001

# Change port in docker-compose.yml
# ports:
#   - "8101:8001"  # External:Internal
```

#### Database connection errors

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U postgres -d autopro -c "SELECT 1;"

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres psql -U postgres -d autopro -f /docker-entrypoint-initdb.d/init-db.sql
```

---

## 2. Kubernetes Deployment (Production)

### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- 16GB RAM per node minimum
- Storage class for persistent volumes

### Option A: AWS EKS

```bash
# 1. Create EKS cluster
eksctl create cluster \
  --name autopro-prod \
  --region eu-west-1 \
  --nodegroup-name standard-workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --managed

# 2. Configure kubectl
aws eks update-kubeconfig --name autopro-prod --region eu-west-1

# 3. Verify connection
kubectl get nodes
```

### Option B: Google GKE

```bash
# 1. Create GKE cluster
gcloud container clusters create autopro-prod \
  --zone europe-west1-b \
  --machine-type n1-standard-2 \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10

# 2. Get credentials
gcloud container clusters get-credentials autopro-prod --zone europe-west1-b

# 3. Verify
kubectl get nodes
```

### Deploy to Kubernetes

```bash
# 1. Create namespace
kubectl apply -f k8s/base/namespace.yaml

# 2. Create secrets
kubectl create secret generic autopro-secrets \
  --from-env-file=.env \
  -n autopro

# 3. Apply ConfigMap
kubectl apply -f k8s/base/configmap.yaml

# 4. Deploy infrastructure
kubectl apply -f k8s/base/postgres.yaml
kubectl apply -f k8s/base/redis.yaml
kubectl apply -f k8s/base/rabbitmq.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n autopro --timeout=300s

# 5. Deploy all microservices
kubectl apply -f k8s/base/lead-service.yaml
kubectl apply -f k8s/base/video-service.yaml
kubectl apply -f k8s/base/social-service.yaml
kubectl apply -f k8s/base/financial-service.yaml
kubectl apply -f k8s/base/referral-service.yaml
kubectl apply -f k8s/base/automation-service.yaml
kubectl apply -f k8s/base/notification-service.yaml
kubectl apply -f k8s/base/analytics-service.yaml
kubectl apply -f k8s/base/whatsapp-service.yaml
kubectl apply -f k8s/base/mcp-service.yaml

# 6. Deploy Kong Gateway & Ingress
kubectl apply -f k8s/base/kong.yaml
kubectl apply -f k8s/base/ingress.yaml

# 7. Verify deployment
kubectl get pods -n autopro
kubectl get services -n autopro
kubectl get ingress -n autopro

# 8. Check rollout status
kubectl rollout status deployment/lead-service -n autopro

# 9. View logs
kubectl logs -f deployment/lead-service -n autopro

# 10. Get external IP
kubectl get ingress autopro-ingress -n autopro
```

### Configure DNS

```bash
# Get Kong Gateway LoadBalancer IP
KONG_IP=$(kubectl get service kong -n autopro -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Create DNS A record
# api.autopro.ro → $KONG_IP
```

### SSL/TLS Certificate

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer (Let's Encrypt)
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: tech@autopro.ro
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: kong
EOF

# Update Ingress with TLS
kubectl patch ingress autopro-ingress -n autopro --type=json -p='[
  {
    "op": "add",
    "path": "/spec/tls",
    "value": [{
      "hosts": ["api.autopro.ro"],
      "secretName": "autopro-tls"
    }]
  },
  {
    "op": "add",
    "path": "/metadata/annotations/cert-manager.io~1cluster-issuer",
    "value": "letsencrypt-prod"
  }
]'
```

---

## 3. Blue-Green Deployment

### Setup

```bash
# Create blue (current) and green (new) namespaces
kubectl create namespace autopro-blue
kubectl create namespace autopro-green

# Deploy current version to blue
kubectl apply -f k8s/base/ -n autopro-blue

# Deploy new version to green
kubectl apply -f k8s/base/ -n autopro-green
```

### Switch Traffic

```bash
# Test green environment
curl https://api-green.autopro.ro/health

# Switch Ingress to green
kubectl patch ingress autopro-ingress \
  -p '{"spec":{"rules":[{"host":"api.autopro.ro","http":{"paths":[{"backend":{"service":{"name":"lead-service","namespace":"autopro-green"}}}]}}]}}'

# Verify traffic switched
curl https://api.autopro.ro/health

# Rollback if needed
kubectl patch ingress autopro-ingress \
  -p '{"spec":{"rules":[{"host":"api.autopro.ro","http":{"paths":[{"backend":{"service":{"name":"lead-service","namespace":"autopro-blue"}}}]}}]}}'
```

---

## 4. Canary Deployment

### Using Flagger (Istio/Linkerd)

```bash
# Install Flagger
kubectl apply -f https://raw.githubusercontent.com/fluxcd/flagger/main/artifacts/flagger/crd.yaml

# Create Canary resource
cat <<EOF | kubectl apply -f -
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: lead-service
  namespace: autopro
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lead-service
  service:
    port: 8001
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
EOF

# Deploy new version
kubectl set image deployment/lead-service \
  lead-service=ghcr.io/autopro/lead-service:v2.0.0 \
  -n autopro

# Flagger will automatically:
# 1. Deploy canary with 10% traffic
# 2. Monitor metrics for 1 minute
# 3. Gradually increase to 50% if healthy
# 4. Promote or rollback based on metrics
```

---

## 5. Database Migrations

### Using Alembic

```bash
# Generate migration
cd lead-service
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View history
alembic history
```

### In Production

```bash
# Run migrations as Kubernetes Job
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: lead-service-migration
  namespace: autopro
spec:
  template:
    spec:
      containers:
      - name: migration
        image: ghcr.io/autopro/lead-service:latest
        command: ["alembic", "upgrade", "head"]
        envFrom:
        - secretRef:
            name: autopro-secrets
      restartPolicy: Never
  backoffLimit: 3
EOF

# Check migration status
kubectl logs job/lead-service-migration -n autopro
```

---

## 6. Monitoring Setup

### Prometheus

```bash
# Install Prometheus Operator
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Create ServiceMonitor for services
kubectl apply -f monitoring/service-monitors.yaml

# Access Prometheus
kubectl port-forward -n autopro svc/prometheus 9090:9090
open http://localhost:9090
```

### Grafana

```bash
# Install Grafana
kubectl apply -f monitoring/grafana.yaml

# Get admin password
kubectl get secret grafana -n autopro -o jsonpath='{.data.admin-password}' | base64 -d

# Access Grafana
kubectl port-forward -n autopro svc/grafana 3000:3000
open http://localhost:3000

# Import dashboards
# Upload monitoring/grafana/dashboards/*.json
```

### Jaeger

```bash
# Install Jaeger Operator
kubectl create namespace observability
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.49.0/jaeger-operator.yaml

# Create Jaeger instance
kubectl apply -f monitoring/jaeger.yaml

# Access UI
kubectl port-forward -n observability svc/jaeger-query 16686:16686
open http://localhost:16686
```

---

## 7. Backup & Restore

### Database Backup

```bash
# Create backup Job
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: autopro
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - pg_dump -h postgres -U postgres autopro | gzip > /backups/backup-\$(date +%Y%m%d-%H%M%S).sql.gz
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: postgres-backups
          restartPolicy: OnFailure
EOF
```

### Restore from Backup

```bash
# Copy backup to pod
kubectl cp backup.sql.gz autopro/postgres-0:/tmp/

# Restore
kubectl exec -it postgres-0 -n autopro -- bash
gunzip -c /tmp/backup.sql.gz | psql -U postgres autopro
```

---

## 8. Scaling

### Manual Scaling

```bash
# Scale specific service
kubectl scale deployment lead-service --replicas=5 -n autopro

# Scale all services
for svc in lead-service video-service social-service; do
  kubectl scale deployment $svc --replicas=3 -n autopro
done
```

### Auto-Scaling (HPA)

```bash
# Already configured in manifests
# View HPA status
kubectl get hpa -n autopro

# Manually adjust HPA
kubectl patch hpa lead-service-hpa -n autopro -p '{"spec":{"maxReplicas":20}}'
```

### Cluster Auto-Scaling

**AWS EKS:**

```bash
# Install Cluster Autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

# Configure
kubectl -n kube-system annotate deployment.apps/cluster-autoscaler \
  cluster-autoscaler.kubernetes.io/safe-to-evict="false"
```

---

## 9. Security Hardening

### Network Policies

```bash
# Restrict traffic between services
kubectl apply -f k8s/security/network-policies.yaml
```

### Pod Security

```bash
# Enable Pod Security Standards
kubectl label namespace autopro \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

### Secrets Encryption

```bash
# AWS: Use KMS
# GCP: Use Cloud KMS
# Azure: Use Key Vault

# Encrypt secrets at rest
kubectl create secret generic autopro-secrets \
  --from-env-file=.env \
  -n autopro \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

kubectl apply -f sealed-secret.yaml
```

---

## 10. Performance Tuning

### Resource Optimization

```bash
# Monitor resource usage
kubectl top pods -n autopro
kubectl top nodes

# Adjust resource requests/limits
kubectl set resources deployment lead-service \
  --requests=cpu=200m,memory=256Mi \
  --limits=cpu=500m,memory=512Mi \
  -n autopro
```

### Database Tuning

```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Enable query caching
ALTER SYSTEM SET shared_buffers = '2GB';

-- Optimize for SSD
ALTER SYSTEM SET random_page_cost = 1.1;

-- Reload configuration
SELECT pg_reload_conf();
```

---

## ✅ Post-Deployment Checklist

- [ ] All pods running and healthy
- [ ] Health checks passing (/health/ready, /health/live)
- [ ] Metrics being scraped by Prometheus
- [ ] Grafana dashboards showing data
- [ ] SSL certificate valid
- [ ] DNS resolving correctly
- [ ] Database migrations applied
- [ ] Backups configured
- [ ] Auto-scaling enabled
- [ ] Monitoring alerts configured
- [ ] Load testing passed
- [ ] Security scan completed
- [ ] Documentation updated

---

**For support**: tech@autopro.ro
**Last Updated**: 2025-10-28
