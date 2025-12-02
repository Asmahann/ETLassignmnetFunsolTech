## Animals ETL

This project implements a small, reliable ETL pipeline against the Animals API provided in the
coding challenge. It:

- Fetches all animals from `/animals/v1/animals` and `/animals/v1/animals/{id}`
- Transforms `friends` and `born_at` fields
- Loads animals into `/animals/v1/home` in batches of up to 100
- Handles random delays and transient 5xx errors with retries and backoff
- Uses type annotations, linting, and tests

### Prerequisites

- Python 3.10+
- Docker running the challenge image, for example:

```bash
docker run --rm -p 3123:3123 -ti lp-programming-challenge-1:latest
```

### Installation

```bash
cd animals_etl
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running the ETL

```bash
python -m animals_etl.main
```

By default the ETL targets `http://localhost:3123`. You can override this with:

```bash
ANIMALS_API_BASE_URL="http://localhost:3123" python -m animals_etl.main
```

The command exits with status code `0` on success and `1` if the ETL run fails.

### Testing & Linting

```bash
pytest
ruff check .
mypy .
```



