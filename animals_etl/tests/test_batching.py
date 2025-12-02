from __future__ import annotations

from animals_etl.etl import chunked
from animals_etl.models import AnimalDetail


def make_animal(i: int) -> AnimalDetail:
    return AnimalDetail(id=i, name=f"Animal {i}")


def test_chunked_splits_into_batches() -> None:
    animals = [make_animal(i) for i in range(10)]
    batches = list(chunked(animals, 3))
    lengths = [len(b) for b in batches]
    assert lengths == [3, 3, 3, 1]
