# ADR-042: Caching Strategy for Microservices Platform

## Status

Accepted — 2024-03-15

## Context

Our platform consists of five microservices: UserService, OrderService, ProductCatalog, NotificationService, and AnalyticsEngine. Each service needs fast access to shared reference data (user profiles, product metadata, feature flags) and must coordinate distributed state (session tokens, rate-limit counters, idempotency keys).

## Decision

All five services will use a single shared Redis 7.x instance (`cache-primary.internal:6379`) for:

- Session token storage (UserService)
- Shopping cart state (OrderService)
- Product catalog cache (ProductCatalog)
- Notification deduplication keys (NotificationService)
- Real-time metrics aggregation (AnalyticsEngine)

Redis is deployed on a dedicated m5.2xlarge instance with 32GB RAM. This provides sub-millisecond reads and simplifies our operational footprint by having one cache layer to monitor.

## Service Discovery

Services locate each other via Consul-based service discovery with health checks. Each service registers itself on startup and deregisters on graceful shutdown. Consul health checks run every 10 seconds with a 30-second deregister-critical timeout. Failed instances are automatically removed from the service mesh, and traffic is rerouted to healthy instances within one health check interval.

## Consequences

- Reduced operational complexity: one Redis instance to back up and monitor
- Consistent caching behavior across all services
- Lower infrastructure cost compared to per-service cache instances
- Redis is always available so services can rely on cache reads succeeding
- Key namespace collisions are prevented by prefixing keys with the service name
