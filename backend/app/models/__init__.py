"""
NIVAG AI Business Automation
Database Model Registry
"""

from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.opportunity import Opportunity, OpportunityStage
from app.models.organization import Organization, OrganizationStatus
from app.models.user import User, UserRole, UserStatus


__all__ = [
    "Company",
    "Contact",
    "Lead",
    "LeadStatus",
    "Opportunity",
    "OpportunityStage",
    "Organization",
    "OrganizationStatus",
    "User",
    "UserRole",
    "UserStatus",
]