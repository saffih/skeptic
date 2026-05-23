# Requirements: Customer Portal v2.0

## Purpose

Define the functional and non-functional requirements for the next generation customer self-service portal.

## Functional Requirements

### FR-1: Authentication
The system shall authenticate users via OAuth 2.0 with support for Google and Microsoft identity providers. Failed login attempts shall be logged with timestamp and source IP.

### FR-2: Performance
The system should be fast. Pages must load quickly and the system should handle many users.

### FR-3: User Experience
User experience must be intuitive. The interface should be clean and modern. Users should find what they need without training.

### FR-4: Dashboard
The system shall display a personalized dashboard showing the user's recent orders, open support tickets, and account balance.

### FR-5: Notifications
The system should send appropriate notifications. Users should be kept informed of important events.

## Non-Functional Requirements

### NFR-1: Availability
The system should be highly available and reliable.

### NFR-2: Security
The system must be secure and protect user data.
