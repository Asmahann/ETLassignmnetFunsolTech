from __future__ import annotations

from datetime import datetime, timezone

from animals_etl.models import AnimalDetail


def test_friends_parsing_from_string() -> None:
    animal = AnimalDetail(id=1, name="Test", friends="alice, bob , ,carol")
    assert animal.friends == ["alice", "bob", "carol"]


def test_born_at_parsing_to_utc() -> None:
    dt = datetime(2020, 1, 1, 12, 0, 0)
    animal = AnimalDetail(id=1, name="Test", born_at=dt)
    assert animal.born_at is not None
    assert animal.born_at.tzinfo == timezone.utc


def test_to_load_payload_formats_timestamp() -> None:
    dt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    animal = AnimalDetail(id=1, name="Test", born_at=dt, friends=["alice"])
    payload = animal.to_load_payload()
    assert payload["born_at"] == "2020-01-01T12:00:00Z"
    assert payload["friends"] == ["alice"]
