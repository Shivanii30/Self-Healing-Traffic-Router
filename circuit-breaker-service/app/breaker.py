import json
import time
from app.models import CircuitState
from app.redis_client import redis_client

FAILURE_THRESHOLD = 5
OPEN_TIMEOUT = 30
HALF_OPEN_REQUESTS = 10


class CircuitBreaker:
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self.half_open_requests = 0
        self.half_open_successes = 0

    def allow_request(self):
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if (time.time() - (self.last_failure_time or 0)) >= OPEN_TIMEOUT:
                self.state = CircuitState.HALF_OPEN
                self.half_open_requests = 0
                self.half_open_successes = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_requests < HALF_OPEN_REQUESTS:
                self.half_open_requests += 1
                return True
            return False

        return False

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            if self.half_open_successes >= HALF_OPEN_REQUESTS:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.half_open_requests = 0
                self.half_open_successes = 0
        elif self.state == CircuitState.CLOSED:
            self.failures = 0

    def record_failure(self):
        self.failures += 1
        if self.state == CircuitState.CLOSED:
            if self.failures >= FAILURE_THRESHOLD:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            self.half_open_successes = 0

    def recover(self):
        if self.state == CircuitState.OPEN:
            self.state = CircuitState.HALF_OPEN
            self.half_open_requests = 0
            self.half_open_successes = 0

    def status(self):
        return {
            "state": self.state,
            "failures": self.failures,
            "half_open_requests": self.half_open_requests,
            "half_open_successes": self.half_open_successes,
        }

    def save_to_redis(self, service_name: str):
        """Persist circuit state so the routing engine can read it."""
        redis_client.set(
            f"circuit:{service_name}",
            json.dumps({"state": self.state})
        )
