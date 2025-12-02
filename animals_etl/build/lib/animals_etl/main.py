from __future__ import annotations

import asyncio
import logging
import os

from .etl import run_etl


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    base_url = os.environ.get("ANIMALS_API_BASE_URL", "http://localhost:3123")
    asyncio.run(run_etl(base_url=base_url))


if __name__ == "__main__":  # pragma: no cover - manual entry point
    main()

