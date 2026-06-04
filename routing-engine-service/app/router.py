import json
from app.registry import SERVICE_REGISTRY
from app.redis_client import redis_client
from app.metrics import FAILOVER_EVENTS_TOTAL

counters = {}


def get_healthy_instances(service_name):
    instances = SERVICE_REGISTRY.get(service_name, [])
    healthy = []

    for instance in instances:
        # Key must match what health-monitor writes: "service_status:<name>"
        health_data = redis_client.get(f"service_status:{instance}")
        if not health_data:
            FAILOVER_EVENTS_TOTAL.inc()
            continue

        health = json.loads(health_data)
        if health.get("status") != "healthy":
            FAILOVER_EVENTS_TOTAL.inc()
            continue

        # Circuit breaker state is written by circuit-breaker-service
        circuit_data = redis_client.get(f"circuit:{instance}")
        if circuit_data:
            circuit = json.loads(circuit_data)
            if circuit.get("state") == "OPEN":
                FAILOVER_EVENTS_TOTAL.inc()
                continue

        healthy.append(instance)

    return healthy


def get_destination(service_name):
    healthy = get_healthy_instances(service_name)
    if not healthy:
        return None

    counters.setdefault(service_name, 0)
    index = counters[service_name] % len(healthy)
    counters[service_name] += 1
    return healthy[index]
