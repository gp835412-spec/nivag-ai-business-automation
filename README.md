NIVAG AI Business Automation

A backend foundation for a multi-tenant business automation platform.

The project currently focuses on the core application architecture, including authentication, organization management, user management, database access, and tenant isolation.

The system is being designed so that additional capabilities such as AI-powered automation, workflows, integrations, and intelligent business tools can be added without changing the core architecture.


🏗️ Architecture

API Router
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database

Each layer has a specific responsibility:

🔹 API Router — Handles HTTP requests and responses.
⚙️ Service Layer — Contains application and business logic.
🗄️ Repository Layer — Handles database operations.
💾 Database Layer — Manages persistent storage.

This keeps application logic separate from HTTP handling and database implementation.

🏢 Multi-Tenant Design

The platform follows an organization-based structure.

Organization
│
├── 👑 Owner
├── 🛡️ Admin
└── 👥 Members
Users belong to an organization.
Application data is scoped to that organization.
The authenticated user context is used to enforce organization-level access.
Cross-organization data access is prevented through tenant isolation.
🛠️ Technology Stack
🐍 Python
⚡ FastAPI
🗃️ SQLAlchemy
🐘 PostgreSQL
🔄 Alembic
📦 Pydantic
🔐 JWT
🧪 Pytest
⚙️ pytest-asyncio
✨ Current Features

The current implementation includes:

🔐 JWT-based authentication
👤 User management
🏢 Organization management
🏗️ Multi-tenant access control
🔒 Organization-scoped data access
📐 Layered backend architecture
🗄️ Repository-based database access
🔄 Database migrations with Alembic
✅ Request and response validation
🧪 Automated tests
🧪 Testing

The project includes automated tests for:

API routers
Authentication workflows
Organization services
User services
Organization repositories
User repositories
Current Test Status
89 passed

Run the test suite:

pytest
🚀 Development Direction

The current backend provides the foundation for future modules such as:

🤖 AI-powered business automation
🔄 Workflow automation
🧠 AI agents
👥 CRM and customer management
🎯 Lead capture and automation
🔌 External integrations
🔔 Notification systems
📊 Business analytics
📈 Automation monitoring

These capabilities will be added as separate modules while keeping the existing application layers independent.

📌 Project Status

The core backend foundation is complete and tested.

Future development will focus on business automation, AI-powered workflows, integrations, and intelligent task execution.

🌐 Other NIVAG Projects

NIVAG is a collection of independent projects focused on AI systems, education, automation, and content production.

Some projects currently under development include:

🎓 NIVAG IAS

An AI-powered education and learning system being developed for structured learning, teaching, revision, practice, evaluation, and personalized academic support.

The system includes separate Student and Teacher modules and is designed around a dedicated academic intelligence architecture.

🎬 NIVAG Cartoon

A system for building AI-assisted animated and cartoon content workflows.

The project is focused on structured story development, character and scene planning, narrative generation, and production-oriented content workflows.

⚙️ NIVAG Automation

A broader automation initiative focused on AI-assisted workflows, business processes, task execution, and intelligent automation systems.

🧠 NIVAG AI Systems

A collection of experiments and internal systems related to AI application architecture, intelligent workflows, LLM integration, automation, and future agent-based systems.

These projects are currently under active development and are maintained in private repositories.

📄 License

This project is provided for portfolio and technical demonstration purposes.

All rights reserved.
