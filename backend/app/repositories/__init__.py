"""
NIVAG AI Business Automation
Repository Package
"""

from app.repositories.company_repository import CompanyRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    "CompanyRepository",
    "ContactRepository",
    "LeadRepository",
    "OrganizationRepository",
    "UserRepository",
]