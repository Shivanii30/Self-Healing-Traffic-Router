import os

SERVICES = {
    "user-v1": "http://user-service:8001",
    "payment-v1": "http://payment-service:8002",
    "order-v1": "http://order-service:8003",
}

# Circuit-breaker service URL (internal Docker network)
CIRCUIT_BREAKER_URL = os.environ.get(
    "CIRCUIT_BREAKER_URL", "http://circuit-breaker-service:9200"
)
