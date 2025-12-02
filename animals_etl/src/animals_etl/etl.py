from __future__ import annotations

import asyncio
import logging
from typing import Iterable, List

from .client import AnimalsClient
from .models import AnimalDetail

logger = logging.getLogger(__name__)


def chunked(items: Iterable[AnimalDetail], size: int) -> Iterable[List[AnimalDetail]]:
    batch: List[AnimalDetail] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


async def run_etl(base_url: str, *, batch_size: int = 100) -> None:
    client = AnimalsClient(base_url=base_url)

    logger.info("Fetching animal summaries...")
    summaries = await client.list_all_summaries()
    logger.info("Fetched %d summaries", len(summaries))

    logger.info("Fetching animal details in parallel...")
    semaphore = asyncio.Semaphore(20)

    async def fetch_one(animal_id: int) -> AnimalDetail:
        async with semaphore:
            return await client.fetch_animal_detail(animal_id)

    tasks = [asyncio.create_task(fetch_one(summary.id)) for summary in summaries]
    details: List[AnimalDetail] = [await task for task in asyncio.as_completed(tasks)]
    logger.info("Fetched %d details", len(details))

    logger.info("Posting animals to /home in batches of %d...", batch_size)
    for batch in chunked(details, batch_size):
        await client.post_home_batch(batch)
        logger.info("Posted batch of %d animals", len(batch))

    logger.info("ETL completed successfully.")

