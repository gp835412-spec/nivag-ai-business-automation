"""
NIVAG AI Business Automation

Opportunity API module.
"""

from app.api.v1.opportunities.opportunity_route import (
    get_opportunity_service,
    router,
)


__all__ = [
    "get_opportunity_service",
    "router",
]