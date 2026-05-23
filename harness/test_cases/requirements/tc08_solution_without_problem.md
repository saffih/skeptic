# Requirements: Order Management Platform

## Background

The company is growing and needs a modern platform to handle orders at scale. This document defines the requirements for the new system.

## Requirements

### R-1: Architecture
The system shall use a microservice architecture with at least 6 separate services. Each service shall be deployed as a Docker container orchestrated by Kubernetes.

### R-2: Event Processing
We need Apache Kafka for event processing. All inter-service communication shall go through Kafka topics. The cluster shall have a minimum of 3 brokers with replication factor 3.

### R-3: Data Storage
All application data shall be stored in a single PostgreSQL 15 database with logical partitioning per service schema.

### R-4: Password Reset
Users must be able to reset their password via email. The reset link shall expire after 24 hours and be single-use.

### R-5: Frontend
The frontend shall be built using React 18 with TypeScript and Next.js for server-side rendering.

### R-6: Monitoring
The system shall use Prometheus for metrics collection, Grafana for dashboards, and Jaeger for distributed tracing.

### R-7: Service Autonomy
Each service must own its data and shall not share database tables with other services. Services communicate only through published APIs and events.

### R-8: Caching
Redis 7.x shall be used for all caching needs with a minimum of 16GB allocated memory.
