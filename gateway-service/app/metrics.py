from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter("gateway_requests_total", "Total gateway requests", ["route"])
ERRORS_TOTAL = Counter("gateway_errors_total", "Total gateway errors", ["route"])
FAILOVER_EVENTS_TOTAL = Counter("gateway_failover_events_total", "Total failovers")
REQUEST_DURATION = Histogram("gateway_request_duration_seconds", "Request duration", ["route"])
