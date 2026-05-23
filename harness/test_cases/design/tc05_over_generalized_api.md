# API Design: Document Processing Service

## Overview

The Document Processing Service provides a unified API for managing documents across all product lines. It supports the full document lifecycle from creation through archival.

## Authentication

All requests must include a Bearer token in the Authorization header. Tokens are issued by the central auth service and scoped to the requesting service account. Tokens expire after 1 hour and must be refreshed via the `/auth/refresh` endpoint.

Role-based access control is enforced at the gateway level:
- `doc:read` — read any document
- `doc:write` — create or update documents
- `doc:admin` — delete, export, and manage retention policies

## Core Endpoint

### POST /api/v1/process

All document operations go through a single endpoint. The `type` field in the request body determines the operation:

```json
{
  "type": "create | read | update | delete | validate | export | archive | bulk_import",
  "document_id": "optional, required for read/update/delete",
  "payload": { },
  "options": {
    "format": "pdf | docx | html",
    "validated": true
  }
}
```

The `type` field selects the operation. When `type` is `validate`, the server checks the document against the configured schema. Clients that have already validated locally can set `options.validated: true` to skip server-side validation on create and update operations.

### Response

All operations return a uniform envelope:

```json
{
  "status": "ok | error",
  "data": { },
  "request_id": "uuid"
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes (400, 401, 403, 404, 500) and a machine-readable `error_code` field inside the response body.

## Rate Limiting

Each service account is limited to 1000 requests per minute. Exceeding this limit returns HTTP 429 with a `Retry-After` header.
