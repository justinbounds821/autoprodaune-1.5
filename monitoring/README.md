# AutoPro Daune Monitoring Setup

## Grafana Quick Import

1. Add Prometheus datasource -> URL: http://localhost:9090
2. Import `monitoring/grafana-dashboard.json`
3. Verify panel "API Health Status" uses query from `/metrics`

## Services

- **Prometheus**: Metrics collection at http://localhost:9090
- **Grafana**: Dashboards at http://localhost:3001 (admin/admin)
- **AlertManager**: Alerts at http://localhost:9093

## API Endpoints

- **Health Check**: http://localhost:8001/health
- **Metrics**: http://localhost:8001/metrics
- **API Docs**: http://localhost:8001/docs

