# NIVAG AI Business Automation

A production-oriented multi-tenant backend for an AI-powered business automation platform.

Built with FastAPI, SQLAlchemy, PostgreSQL, Alembic, JWT authentication, and a clean layered architecture.

## Features

- Multi-tenant organization architecture
- Organization registration and management
- Owner and user management
- JWT-based authentication
- Secure password hashing and verification
- Role-based authorization
- Organization-scoped data isolation
- Repository and service layer architecture
- Database migrations with Alembic
- Automated API, service, and repository testing

## Architecture

```text
API Router
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database Layer


The architecture separates HTTP handling, business logic, database access, and security responsibilities.

Multi-Tenant Design

Each user belongs to an organization.

Organization
│
├── Owner
├── Admin
└── Members

Organization-scoped access is enforced through the authenticated user context to prevent cross-organization data access.

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
Testing

The backend currently includes automated tests for:

API routers
Authentication workflows
Organization services
User services
Organization repositories
User repositories

Current test status:

89 passed

Run all tests:

pytest
Project Status

The core backend foundation is complete and tested.

Future development will extend the platform with AI-powered business automation, workflow automation, integrations, CRM capabilities, lead management, and intelligent business tools.

License

This project is provided as a portfolio and technical demonstration project.

All rights reserved.