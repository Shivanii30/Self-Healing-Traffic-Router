from prometheus_client import Counter

SERVICE_CHECKS_TOTAL = Counter("service_checks_total", "Total health checks")
UNHEALTHY_SERVICES_TOTAL = Counter("unhealthy_services_total", "Total unhealthy detections")
