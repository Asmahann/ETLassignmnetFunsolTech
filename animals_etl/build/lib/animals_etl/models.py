from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AnimalSummary(BaseModel):
    id: int
    name: str


class AnimalDetail(BaseModel):
    id: int
    name: str
    friends: List[str] = Field(default_factory=list)
    born_at: Optional[datetime] = None

    @field_validator("friends", mode="before")
    @classmethod
    def split_friends(cls, value: object) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [v for v in value if isinstance(v, str) and v.strip()]
        if isinstance(value, str):
            return [friend.strip() for friend in value.split(",") if friend.strip()]
        return []

    @field_validator("born_at", mode="before")
    @classmethod
    def parse_born_at(cls, value: object) -> Optional[datetime]:
        if value in (None, "", 0):
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        if isinstance(value, str):
            # Let pydantic / stdlib handle most formats, then normalise to UTC.
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        return None

    def to_load_payload(self) -> dict:
        """Return a JSON-serialisable representation for the /home endpoint."""

        born_at_str = (
            self.born_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            if self.born_at
            else None
        )

        return {
            "id": self.id,
            "name": self.name,
            "friends": self.friends,
            "born_at": born_at_str,
        }


