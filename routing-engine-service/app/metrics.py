from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter("requests_total", "Total requests handled")
ERRORS_TOTAL = Counter("errors_total", "Total errors")
FAILOVER_EVENTS_TOTAL = Counter("failover_events_total", "Total failover events")
REQUEST_DURATION = Histogram("request_duration_seconds", "Request latency")
