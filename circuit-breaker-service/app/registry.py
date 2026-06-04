from app.breaker import CircuitBreaker

breakers = {
    "user-v1": CircuitBreaker(),
    "payment-v1": CircuitBreaker(),
    "order-v1": CircuitBreaker(),
}
