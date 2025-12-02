from __future__ import annotations

import asyncio
import logging
import os
import sys

from .etl import run_etl


def main(argv: list[str] | None = None) -> int:
    """Entry-point used by ``python -m animals_etl.main``."""

    if argv is None:
        argv = sys.argv[1:]

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    # Simple configuration surface; could be extended to argparse/typer if needed.
    base_url = os.environ.get("ANIMALS_API_BASE_URL", "http://localhost:3123")

    try:
        asyncio.run(run_etl(base_url=base_url))
    except Exception:  # pragma: no cover - top-level safeguard
        logging.exception("ETL run failed")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())

