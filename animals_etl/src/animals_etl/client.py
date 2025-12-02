from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Mapping, MutableMapping, Sequence

import httpx

from .models import AnimalDetail, AnimalSummary

logger = logging.getLogger(__name__)


TRANSIENT_STATUS_CODES: tuple[int, ...] = (500, 502, 503, 504)


@dataclass(slots=True)
class AnimalsClient:
    """Async client for talking to the Animals API with retry semantics."""

    base_url: str
    timeout_seconds: float = 10.0
    max_retries: int = 5
    initial_backoff_seconds: float = 0.5

    def _new_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds)

    async def _request_with_retries(
        self,
        method: str,
        url: str,
        *,
        expected_status: int | None = None,
        **kwargs: Mapping[str, object] | MutableMapping[str, object],
    ) -> httpx.Response:
        """Issue an HTTP request with simple exponential backoff on transient failures."""

        backoff = self.initial_backoff_seconds
        attempt = 0
        while True:
            attempt += 1
            try:
                async with self._new_client() as client:
                    response = await client.request(method, url, **kwargs)
                if response.status_code in TRANSIENT_STATUS_CODES:
                    raise httpx.HTTPStatusError(
                        "transient error", request=response.request, response=response
                    )
                response.raise_for_status()
                if expected_status is not None and response.status_code != expected_status:
                    logger.error(
                        "Unexpected status %s from %s %s (expected %s)",
                        response.status_code,
                        method,
                        url,
                        expected_status,
                    )
                return response
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                if attempt > self.max_retries:
                    logger.error(
                        "Giving up after %s attempts to %s %s: %s", attempt, method, url, exc
                    )
                    raise
                logger.warning(
                    "Error on %s %s attempt %s (will retry in %.1fs): %s",
                    method,
                    url,
                    attempt,
                    backoff,
                    exc,
                )
                await asyncio.sleep(backoff)
                backoff *= 2

    async def list_animals_page(self, page: int) -> List[AnimalSummary]:
        response = await self._request_with_retries(
            "GET", f"/animals/v1/animals?page={page}", expected_status=200
        )
        data = response.json()
        items = data.get("items", data)
        return [AnimalSummary.model_validate(item) for item in items]

    async def fetch_animal_detail(self, animal_id: int) -> AnimalDetail:
        response = await self._request_with_retries(
            "GET", f"/animals/v1/animals/{animal_id}", expected_status=200
        )
        data = response.json()
        return AnimalDetail.model_validate(data)

    async def post_home_batch(self, animals: Sequence[AnimalDetail]) -> None:
        if not animals:
            return
        payload: List[dict] = [animal.to_load_payload() for animal in animals]
        await self._request_with_retries(
            "POST", "/animals/v1/home", json=payload, expected_status=200
        )

    async def list_all_summaries(self) -> List[AnimalSummary]:
        page = 1
        result: List[AnimalSummary] = []
        while True:
            page_items = await self.list_animals_page(page)
            if not page_items:
                break
            result.extend(page_items)
            page += 1
        return result

