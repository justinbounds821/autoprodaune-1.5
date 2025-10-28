"""
Generate Kubernetes manifests for all microservices
"""
from pathlib import Path

SERVICES = {
    "lead-service": 8001,
    "video-service": 8002,
    "social-service": 8003,
    "financial-service": 8004,
    "referral-service": 8005,
    "automation-service": 8006,
    "notification-service": 8007,
    "analytics-service": 8008,
    "whatsapp-service": 8009,
    "mcp-service": 8010,
}


def generate_k8s_manifest(service_name: str, port: int) -> str:
    """Generate complete K8s manifest for a service"""
    return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: autopro
  labels:
    app: {service_name}
    tier: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
        tier: backend
    spec:
      containers:
      - name: {service_name}
        image: ghcr.io/autopro/{service_name}:latest
        imagePullPolicy: Always
        ports:
        - containerPort: {port}
          name: http
          protocol: TCP
        envFrom:
        - configMapRef:
            name: autopro-config
        - secretRef:
            name: autopro-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: {port}
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: {port}
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: autopro
  labels:
    app: {service_name}
spec:
  type: ClusterIP
  ports:
  - port: {port}
    targetPort: {port}
    protocol: TCP
    name: http
  selector:
    app: {service_name}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {service_name}-hpa
  namespace: autopro
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {service_name}
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""


def create_ingress_manifest() -> str:
    """Create Ingress manifest for Kong"""
    routes = "\\n".join([
        f'  - path: /api/{service.replace("-service", "")}'
        f'\\n    pathType: Prefix'
        f'\\n    backend:'
        f'\\n      service:'
        f'\\n        name: {service}'
        f'\\n        port:'
        f'\\n          number: {port}'
        for service, port in SERVICES.items()
    ])
    
    return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: autopro-ingress
  namespace: autopro
  annotations:
    kubernetes.io/ingress.class: kong
    konghq.com/strip-path: "true"
    konghq.com/plugins: rate-limiting, cors
spec:
  rules:
  - host: api.autopro.ro
    http:
      paths:
{routes}
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: rate-limiting
  namespace: autopro
plugin: rate-limiting
config:
  minute: 100
  policy: local
---
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: cors
  namespace: autopro
plugin: cors
config:
  origins:
  - "*"
  methods:
  - GET
  - POST
  - PUT
  - DELETE
  - OPTIONS
  headers:
  - Authorization
  - Content-Type
  credentials: true
"""


# Generate manifests
base_path = Path("/workspace/microservices/k8s/base")

for service_name, port in SERVICES.items():
    manifest_path = base_path / f"{service_name}.yaml"
    manifest_path.write_text(generate_k8s_manifest(service_name, port))
    print(f"✅ Generated {service_name}.yaml")

# Generate ingress
ingress_path = base_path / "ingress.yaml"
ingress_path.write_text(create_ingress_manifest())
print(f"✅ Generated ingress.yaml")

print(f"\\n🎉 All Kubernetes manifests generated successfully!")
