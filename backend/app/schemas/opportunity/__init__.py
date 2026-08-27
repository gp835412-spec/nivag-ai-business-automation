"""
==========================================================
NIVAG AI Business Automation

Opportunity Schema Package

Public exports for Opportunity request and response schemas.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from app.schemas.opportunity.create import OpportunityCreate
from app.schemas.opportunity.response import OpportunityResponse
from app.schemas.opportunity.update import OpportunityUpdate


__all__ = [
    "OpportunityCreate",
    "OpportunityResponse",
    "OpportunityUpdate",
]