"""
audit_service.py - Tamper-evident audit logging for FinPilot AI.
"""

from __future__ import annotations

import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import AuditEvent


async def record_audit_event(
    session: AsyncSession,
    business_id: uuid.UUID,
    action: str,
    actor: str,
    entity_type: str,
    entity_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
) -> AuditEvent:
    """Record an immutable audit event in the database."""
    event = AuditEvent(
        id=uuid.uuid4(),
        business_id=business_id,
        action=action,
        actor=actor,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
    )
    session.add(event)
    return event
