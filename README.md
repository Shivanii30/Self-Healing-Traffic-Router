Self-Healing Microservice Traffic Router

A fault-tolerant traffic routing platform designed for microservice environments. 
The system continuously monitors backend service health, automatically routes traffic to healthy instances, prevents requests from reaching
failing services using circuit breakers, and restores traffic when services recover.

The project demonstrates key distributed systems and reliability engineering concepts including health monitoring, service failover, 
circuit breakers, traffic routing, observability, and containerized deployment.

## Tech Stack
### Backend
Python
FastAPI
AsyncIO
### Data Layer
Redis
### Monitoring
Prometheus
Grafana
### Infrastructure
Docker
Docker Compose
### Load Testing
k6
