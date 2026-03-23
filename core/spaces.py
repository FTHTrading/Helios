"""
Spaces Engine — Rooms, Events, Access Keys
═══════════════════════════════════════════════════════════════════════
Spaces are community containers. Operator credential required to create.
Events are ticketed or free. Platform take on revenue.
"""

import uuid
from datetime import datetime, timezone
from config import HeliosConfig
from models.space import Space, SpaceEvent
from models.credential import Credential


class SpaceEngine:
    """Community spaces with rooms and events."""

    def __init__(self, db_session):
        self.db = db_session

    def create_space(self, owner_id: str, name: str,
                     description: str = None, is_public: bool = True,
                     entry_fee_usd: float = 0.0, max_members: int = 500) -> dict:
        """
        Create a new space. Owner must hold an operator or host credential.
        """
        # Verify credential
        cred = self.db.query(Credential).filter(
            Credential.holder_id == owner_id,
            Credential.credential_type.in_(["operator", "host"]),
            Credential.is_active == True
        ).first()

        if not cred:
            raise ValueError(f"Node {owner_id} does not hold an active operator or host credential")

        space_id = f"SP-{uuid.uuid4().hex[:12].upper()}"

        space = Space(
            space_id=space_id,
            name=name,
            description=description,
            owner_id=owner_id,
            is_public=is_public,
            max_members=max_members,
            entry_fee_usd=entry_fee_usd
        )

        self.db.add(space)
        self.db.commit()

        return space.to_dict()

    def create_event(self, space_id: str, host_id: str, title: str,
                     description: str = None, event_type: str = "general",
                     ticket_price_usd: float = 0.0, max_attendees: int = 100,
                     starts_at: str = None, ends_at: str = None) -> dict:
        """Create an event within a space."""
        space = self.db.query(Space).filter_by(space_id=space_id, is_active=True).first()
        if not space:
            raise ValueError(f"Space {space_id} not found or inactive")

        if ticket_price_usd > 0:
            if ticket_price_usd < HeliosConfig.SPACE_EVENT_FEE_MIN_USD:
                raise ValueError(f"Minimum event fee: ${HeliosConfig.SPACE_EVENT_FEE_MIN_USD}")
            if ticket_price_usd > HeliosConfig.SPACE_EVENT_FEE_MAX_USD:
                raise ValueError(f"Maximum event fee: ${HeliosConfig.SPACE_EVENT_FEE_MAX_USD}")

        event_id = f"EV-{uuid.uuid4().hex[:12].upper()}"

        event = SpaceEvent(
            event_id=event_id,
            space_id=space_id,
            host_id=host_id,
            title=title,
            description=description,
            event_type=event_type,
            ticket_price_usd=ticket_price_usd,
            max_attendees=max_attendees,
            starts_at=datetime.fromisoformat(starts_at) if starts_at else None,
            ends_at=datetime.fromisoformat(ends_at) if ends_at else None,
        )

        self.db.add(event)
        space.room_count += 1
        self.db.commit()

        return event.to_dict()

    def list_spaces(self, is_public: bool = None, limit: int = 50, offset: int = 0) -> list:
        """List spaces with optional filters."""
        query = self.db.query(Space).filter_by(is_active=True)
        if is_public is not None:
            query = query.filter_by(is_public=is_public)
        return [s.to_dict() for s in query.order_by(Space.created_at.desc()).offset(offset).limit(limit).all()]

    def get_space(self, space_id: str) -> dict:
        """Get space details."""
        space = self.db.query(Space).filter_by(space_id=space_id).first()
        if not space:
            raise ValueError(f"Space {space_id} not found")
        return space.to_dict()

    def list_events(self, space_id: str = None, limit: int = 50, offset: int = 0) -> list:
        """List events, optionally filtered by space."""
        query = self.db.query(SpaceEvent).filter_by(is_active=True)
        if space_id:
            query = query.filter_by(space_id=space_id)
        return [e.to_dict() for e in query.order_by(SpaceEvent.created_at.desc()).offset(offset).limit(limit).all()]
