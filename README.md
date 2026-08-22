NIVAG AI Business Automation

A backend foundation for a multi-tenant business automation platform.

The project currently focuses on the core application architecture, including authentication, organization management, user management, database access, and tenant isolation.

The system is being designed so that additional capabilities such as AI-powered automation, workflows, integrations, and intelligent business tools can be added without changing the core architecture.

Architecture
API Router
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database

Each layer has a specific responsibility:

API Router handles HTTP requests and responses.
Service Layer contains application and business logic.
Repository Layer handles database operations.
Database Layer manages persistent storage.

This keeps application logic separate from HTTP handling and database implementation.

Multi-Tenant Design

The platform follows an organization-based structure.

Organization
│
├── Owner
├── Admin
└── Members

Users belong to an organization, and application data is scoped to that organization.

The authenticated user context is used to enforce organization-level access and prevent cross-organization data access.

Technology Stack
Python
FastAPI
SQLAlchemy
PostgreSQL
Alembic
Pydantic
JWT
Pytest
pytest-asyncio
Current Features

The current implementation includes:

JWT-based authentication
User management
Organization management
Multi-tenant access control
Organization-scoped data access
Layered backend architecture
Repository-based database access
Database migrations with Alembic
Request and response validation
Automated tests
Testing

The project includes automated tests for:

API routers
Authentication workflows
Organization services
User services
Organization repositories
User repositories

Current test status:

89 passed

Run the test suite:

pytest
Development Direction

The current backend provides the foundation for future modules such as:

AI-powered business automation
Workflow automation
AI agents
CRM and customer management
Lead capture and automation
External integrations
Notification systems
Business analytics
Automation monitoring

These capabilities will be added as separate modules while keeping the existing application layers independent.

Project Status

The core backend foundation is complete and tested.

Future development will focus on business automation, AI-powered workflows, integrations, and intelligent task execution.

License

This project is provided for portfolio and technical demonstration purposes.

All rights reserved.
