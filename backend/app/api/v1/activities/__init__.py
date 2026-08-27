"""
==========================================================
NIVAG AI Business Automation

Activities API Package

Exports the tenant-scoped CRM activity API router.

Author:
NIVAG

License:
Proprietary
==========================================================
"""

from app.api.v1.activities.activity_router import router


__all__ = [
    "router",
]