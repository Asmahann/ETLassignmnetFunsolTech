## Animals ETL

A reliable, production-ready ETL pipeline for the Animals API coding challenge. This project demonstrates best practices in Python async programming, error handling, type safety, and testability.

### Features

- **Extract**: Fetches all animals from paginated `/animals/v1/animals` endpoint
- **Transform**: Converts `friends` (comma-separated string → array) and `born_at` (various formats → ISO8601 UTC)
- **Load**: Posts transformed animals to `/animals/v1/home` in batches of up to 100
- **Resilience**: Handles random 5-15 second delays and transient HTTP errors (500, 502, 503, 504) with exponential backoff retries
- **Parallelism**: Fetches animal details concurrently with configurable concurrency limits
- **Type Safety**: Full type annotations with strict mypy checking
- **Testing**: Unit tests with pytest and pytest-asyncio
- **CI/CD**: GitHub Actions workflow for linting, type checking, and testing

### Architecture

The project is organized into clean, focused modules:

- **`models.py`**: Pydantic models with field validators for data transformation
- **`client.py`**: Async HTTP client with retry logic and error handling
- **`etl.py`**: ETL orchestration with parallel fetching and batching
- **`main.py`**: CLI entrypoint with proper exit codes

### Prerequisites

- Python 3.10 or higher
- Docker (for running the challenge API server)

### Setup

#### 1. Start the Animals API Server

```bash
docker run --rm -p 3123:3123 -ti lp-programming-challenge-1:latest
```

Keep this running in a separate terminal. The API will be available at `http://localhost:3123`.

#### 2. Install the Project

```bash
cd animals_etl
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### Usage

#### Running the ETL

```bash
python -m animals_etl.main
```

By default, the ETL targets `http://localhost:3123`. Override with an environment variable:

```bash
ANIMALS_API_BASE_URL="http://localhost:3123" python -m animals_etl.main
```

The command exits with:
- **Status code 0**: ETL completed successfully
- **Status code 1**: ETL failed (errors are logged)

### Data Transformations

#### `friends` Field
- **Input**: Comma-separated string (e.g., `"alice, bob, carol"`) or array
- **Output**: Array of trimmed strings (e.g., `["alice", "bob", "carol"]`)
- **Handles**: Empty strings, whitespace, null values

#### `born_at` Field
- **Input**: Unix timestamp (seconds or milliseconds), ISO8601 string, or null
- **Output**: ISO8601 UTC datetime string (e.g., `"2021-01-01T12:00:00Z"`) or null
- **Handles**: Timezone normalization, millisecond timestamps, invalid values (gracefully drops)

### Error Handling

The pipeline is designed to handle the challenge's pain points:

- **Transient HTTP Errors (500, 502, 503, 504)**: Automatic retry with exponential backoff (0.5s → 1s → 2s → 4s → 8s), up to 5 attempts
- **Random 5-15 Second Delays**: 10-second timeout with retry logic (timeouts trigger retries)
- **Network Failures**: Caught and retried with backoff
- **Individual Record Failures**: Logged with full context; ETL fails fast to prevent silent data loss

### Parallelism

- **Detail Fetching**: Uses `asyncio.Semaphore` to limit concurrent requests (default: 20)
- **Batch Processing**: Sequential batch posting to `/home` endpoint (respects 100-item limit)
- **Efficient**: Fetches all details in parallel while respecting server capacity

### Development

#### Running Tests

```bash
pytest
```

#### Linting

```bash
ruff check .
```

#### Type Checking

```bash
mypy .
```

#### All Quality Checks

```bash
pytest && ruff check . && mypy .
```

### CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs on every push and pull request:

- Python 3.11 environment setup
- Dependency installation
- Linting (ruff)
- Type checking (mypy)
- Unit tests (pytest)

### Project Structure

```
animals_etl/
├── src/
│   └── animals_etl/
│       ├── __init__.py
│       ├── models.py      # Pydantic models and transformations
│       ├── client.py       # HTTP client with retries
│       ├── etl.py          # ETL orchestration
│       └── main.py         # CLI entrypoint
├── tests/
│   ├── test_models.py      # Model transformation tests
│   └── test_batching.py    # Batching utility tests
├── .github/
│   └── workflows/
│       └── ci.yml          # CI pipeline
├── pyproject.toml          # Project metadata and dependencies
└── README.md              # This file
```

### Design Decisions

- **Async/Await**: Uses `httpx` for async HTTP requests to enable parallelism
- **Pydantic**: Type-safe data models with automatic validation and transformation
- **Exponential Backoff**: Prevents overwhelming a struggling server
- **Semaphore-based Concurrency**: Limits parallel requests to avoid server overload
- **Fail-Fast Philosophy**: Errors are logged and propagated immediately to prevent silent data loss
- **Strict Type Checking**: Full type annotations with mypy strict mode for maintainability



