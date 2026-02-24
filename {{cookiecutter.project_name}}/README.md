# {{cookiecutter.project_name}}

{{cookiecutter.app_description}}

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

<!-- Pytest Coverage Comment:Begin -->
<!-- Pytest Coverage Comment:End -->

## Features

- ✅ **FastAPI REST API** for job management (enqueue, status, results)
- ✅ **Redis Queue (RQ)** for reliable job processing
- ✅ **Docker Compose** setup with Redis, API, workers, and monitoring dashboard
- ✅ **Multiple worker processes** with configurable scaling
- ✅ **Authentication system** (API keys + OAuth 2.0)
- ✅ **RQ Dashboard** for real-time monitoring
- ✅ **Structured JSON logging** with async handlers
- ✅ **Comprehensive test suite** with pytest and coverage
- ✅ **CI/CD workflows** with GitHub Actions
- ✅ **Example worker tasks** (data transformation, CSV processing)

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI API │─────▶│    Redis    │
│             │◀─────│  (Port 8000) │      │  (Queue)    │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                   │
                                                   │ Dequeue
                                                   ▼
                                            ┌──────────────┐
                                            │  RQ Workers  │
                                            │  (x2 default)│
                                            └──────┬───────┘
                                                   │
                                                   │ Store Result
                                                   ▼
                                            ┌──────────────┐
                                            │    Redis     │
                                            │  (Results)   │
                                            └──────────────┘
```

## Process flow
```
┌──────────────────────────────────────────────────────────────┐
│  CLIENT                                                      │
└────┬─────────────────────────────────────────────────────────┘
     │ 1. POST /api/jobs/enqueue
     │    {task_name: "transform_data", task_args: {...}}
     ▼
┌──────────────────────────────────────────────────────────────┐
│  FASTAPI API (Runs in "api" container)                       │
│  - Validates task exists in TASK_REGISTRY                    │
│  - Calls enqueue_job(transform_data_function, **args)        │
└────┬─────────────────────────────────────────────────────────┘
     │ 2. Serializes function + args to JSON
     ▼
┌──────────────────────────────────────────────────────────────┐
│  REDIS (Queue Storage)                                       │
│  ┌────────────────────────────────────┐                      │
│  │ Queue: "default"                   │                      │
│  │ ┌────────────────────────────────┐ │                      │
│  │ │ Job: abc123                    │ │                      │
│  │ │ func: "...tasks.transform_data"│ │← Stores module path │
│  │ │ kwargs: {data: {...}, op: ...} │ │                      │
│  │ └────────────────────────────────┘ │                      │
│  └────────────────────────────────────┘                      │
└────┬─────────────────────────────────────────────────────────┘
     │ 3. Worker polls Redis continuously
     ▼
┌──────────────────────────────────────────────────────────────┐
│  RQ WORKER PROCESS (Runs in "worker" container)              │
│  Started by: `rq worker --url redis://... default`           │
│                                                              │
│  INFINITE LOOP:                                              │
│    while True:                                               │
│      job = redis.get_next_job(['default', 'high', 'low'])   │← Blocking!
│      if job:                                                 │
│        - import {{cookiecutter.project_name}}.workers.tasks  │
│        - func = tasks.transform_data                         │
│        - result = func(**job.kwargs)      ← EXECUTES HERE! │
│        - redis.store_result(job.id, result)                  │
└────┬─────────────────────────────────────────────────────────┘
     │ 4. Stores result back in Redis
     ▼
┌──────────────────────────────────────────────────────────────┐
│  REDIS (Result Storage)                                      │
│  Job abc123: status="finished", result={...}                 │
└────┬─────────────────────────────────────────────────────────┘
     │ 5. Client polls for result
     ▼
┌──────────────────────────────────────────────────────────────┐
│  CLIENT                                                      │
│  GET /api/jobs/abc123/result                                 │
│  ← Returns: {"status": "finished", "result": {...}}        │
└──────────────────────────────────────────────────────────────┘
```
## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Git

### Run with Docker Compose

1. **Clone and navigate to the project:**
   ```bash
   cd {{cookiecutter.project_name}}
   ```
2. **Create .env file**
    * Rename the `.env.example` to `.env`
3. **Start all services:**
   ```bash
   docker-compose up --build -d
   ```

4. **Access the services:**
   - **API Swagger UI:** http://localhost:8000/docs
   - **RQ Dashboard:** http://localhost:9181
   - **Health Check:** http://localhost:8000/health

5. **Test job submission** (using default API key `test`):
   ```bash
   curl -X POST "http://localhost:8000/api/jobs/enqueue" \
     -H "Authorization: Bearer test" \
     -H "Content-Type: application/json" \
     -d '{
       "task_name": "transform_data",
       "task_args": {
         "data": {"name": "John", "age": 30},
         "operation": "uppercase_keys"
       }
     }'
   ```

6. **Check job status:**
   ```bash
   curl -X GET "http://localhost:8000/api/jobs/{job_id}/status" \
     -H "Authorization: Bearer test"
   ```

7. **Get job result:**
   ```bash
   curl -X GET "http://localhost:8000/api/jobs/{job_id}/result" \
     -H "Authorization: Bearer test"
   ```

## Local Development

### Setup

1. **Create virtual environment:**
   ```bash
   uv venv .venv
   source .venv/bin/activate  # Linux/Mac
   # OR
   .venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

4. **Start local Redis:**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

5. **Run development server** (terminal 1):
   ```bash
   python dev_server.py
   ```

6. **Run the worker** (terminal 2) to process enqueued jobs:
   ```bash
   python dev_worker.py
   ```

   The worker imports task functions directly from the installed package
   (`{{cookiecutter.project_name}}.workers.tasks`). It connects to the same local Redis
   instance and continuously polls for new jobs.

   Open additional terminals and repeat the command to run multiple workers in
   parallel.

### Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_tasks.py

# Run with verbose output
pytest -v

# View coverage report
open reports/htmlcov/index.html  # Mac
start reports/htmlcov/index.html  # Windows
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .
```

## Available Tasks

The example includes three worker tasks demonstrating different patterns:

### 1. `transform_data`

Transform dictionary data with various operations.

**Operations:**
- `uppercase_keys`: Convert all keys to uppercase
- `lowercase_keys`: Convert all keys to lowercase
- `filter_nulls`: Remove keys with null values
- `sum_values`: Sum all numeric values
- `count_keys`: Count dictionary keys
- `double_values`: Double all numeric values

**Example:**
```json
{
  "task_name": "transform_data",
  "task_args": {
    "data": {"name": "John", "age": 30, "city": null},
    "operation": "filter_nulls"
  }
}
```

### 2. `process_csv`

Process CSV data with various operations.

**Operations:**
- `to_json`: Convert CSV to list of dictionaries
- `count_rows`: Count number of rows
- `column_stats`: Get statistics for numeric columns
- `get_headers`: Return column headers
- `first_n_rows`: Return first 10 rows

**Example:**
```json
{
  "task_name": "process_csv",
  "task_args": {
    "csv_string": "name,age,score\nAlice,25,95.5\nBob,30,87.2",
    "operation": "column_stats"
  }
}
```

### 3. `long_running_task`

Simulates a long-running task for testing purposes.

**Example:**
```json
{
  "task_name": "long_running_task",
  "task_args": {
    "duration": 5
  }
}
```

## Adding New Tasks

1. **Define task function** in `src/{{cookiecutter.project_name}}/workers/tasks.py`:
   ```python
   def my_new_task(param1: str, param2: int) -> dict:
       \"\"\"Task description.\"\"\"
       try:
           # Your processing logic here
           result = process(param1, param2)
           return {
               "status": "success",
               "result": result,
               "metadata": {"processing_time": ...}
           }
       except Exception as e:
           return {
               "status": "error",
               "error": str(e),
               "error_type": type(e).__name__
           }
   ```

2. **Register task** in `src/{{cookiecutter.project_name}}/routers/jobs.py`:
   ```python
   TASK_REGISTRY = {
       "transform_data": transform_data,
       "process_csv": process_csv,
       "my_new_task": my_new_task,  # Add here
   }
   ```

3. **Task is now available** via API:
   ```bash
   curl -X POST "http://localhost:8000/api/jobs/enqueue" \
     -H "Authorization: Bearer test" \
     -H "Content-Type: application/json" \
     -d '{"task_name": "my_new_task", "task_args": {"param1": "value", "param2": 42}}'
   ```

## Configuration

All configuration via environment variables (see `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | API server port |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number |
| `QUEUE_NAMES` | `default high low` | Space-separated queue names |
| `WORKER_COUNT` | `2` | Number of worker replicas |
| `RESULT_TTL` | `3600` | Result TTL in seconds (1 hour) |
| `JOB_TIMEOUT` | `600` | Job timeout in seconds (10 minutes) |
| `API_KEYS` | `(base64)` | Base64-encoded API keys JSON |
| `LOG_LEVEL_CONSOLE` | `INFO` | Console log level |
| `LOG_LEVEL_FILE` | `DEBUG` | File log level |

### API Keys

API keys are stored as base64-encoded JSON:

```json
{
  "key1": {"username": "user1", "roles": ["admin", "user"]},
  "key2": {"username": "user2", "roles": ["user"]}
}
```

Default test keys:
- `test` (admin + user roles)
- `test2` (user role only)

## Scaling Workers

### Docker Compose

Modify `docker-compose.yml`:
```yaml
worker:
  deploy:
    replicas: 4  # Increase worker count
```

Or use environment variable:
```bash
WORKER_COUNT=4 docker-compose up --scale worker=4
```

### Manual Scaling

```bash
docker-compose up -d --scale worker=4
```

## Monitoring

### RQ Dashboard

Access at http://localhost:9181

Features:
- View all queues and workers
- Monitor job status (queued, started, finished, failed)
- Inspect job details and results
- Retry failed jobs
- Clear queues

### Logs

Structured JSON logs in `logs/{{cookiecutter.project_name}}.log.jsonl`:
```json
{"message": "Enqueued job abc123", "timestamp": "2024-01-01 12:00:00", "level": "INFO", ...}
```

View logs:
```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f worker

# All logs
docker-compose logs -f
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | API information | No |
| `GET` | `/health` | Health check | No |
| `GET` | `/docs` | Swagger UI | No |
| `POST` | `/api/jobs/enqueue` | Enqueue new job | Yes |
| `GET` | `/api/jobs/{job_id}/status` | Get job status | Yes |
| `GET` | `/api/jobs/{job_id}/result` | Get job result | Yes |
| `DELETE` | `/api/jobs/{job_id}` | Cancel job | Yes |
| `GET` | `/api/jobs/tasks/available` | List available tasks | Yes |
| `GET` | `/api/jobs/queues/{queue}/stats` | Get queue statistics | Yes |

## Testing

### Unit Tests

Located in `tests/unit/`:
- `test_tasks.py`: Worker task tests
- `test_jobs_router.py`: API endpoint tests

### Coverage

Coverage reports generated in `reports/htmlcov/`. Current coverage shown in badge at top of README.

## CI/CD

This project uses **reusable GitHub Actions workflows** from the public [`jonathanvanleeuwen/cicd_github`](https://github.com/jonathanvanleeuwen/cicd_github) repository for automated testing, versioning, and releases.

### What Happens on Merge to Main

When you merge a PR into `main`, the following automated workflows execute:
1. **Pre-commit checks**: Ruff formatting, trailing whitespace, YAML validation
2. **Linting**: Ruff linter with strict settings
3. **Testing**: Full pytest suite with coverage reporting
4. **Coverage update**: Coverage badge and report committed to this README
5. **Semantic release**: Automatic version bump based on commit message (feat → minor, fix → patch, BREAKING CHANGE → major)
6. **Build & publish**: Wheel file built and attached to GitHub Release

### GitHub Repository Setup

To enable CI/CD, you must configure your GitHub repository with a Personal Access Token.

> **⚠️ Important: Run Pre-commit Locally First!**
>
> Before creating your first PR, install and run pre-commit locally to avoid CI failures:
> ```bash
> uv pip install --system pre-commit
> pre-commit install
> pre-commit run --all-files  # This will auto-fix formatting issues
> git add -u && git commit -m "chore: apply pre-commit fixes"
> ```
>
> **Why:** Cookiecutter templates may have trailing whitespace or missing EOF newlines. Pre-commit auto-fixes these, but if not run locally first, your initial CI run will fail.

#### Step 1: Create the Release Token (PAT)

The workflow needs a Personal Access Token (PAT) to push commits, tags, and releases to your protected `main` branch.

**Create a Fine-Grained PAT (Recommended):**

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. Click **"Generate new token"**
3. Configure the token:
   - **Token name:** `RELEASE_TOKEN_{{cookiecutter.project_name}}`
   - **Expiration:** 90 days (set a reminder to rotate)
   - **Repository access:** Select "Only select repositories" → Choose:
     - ✅ `{{cookiecutter.github_username}}/{{cookiecutter.project_name}}` (this repository)
   - **Permissions:**
     - **Contents:** Read and write (for pushing commits, tags, and releases)
     - **Metadata:** Read-only (automatically selected)
4. Click **"Generate token"**
5. **Copy the token immediately** - you won't see it again!

**Alternative: Classic PAT**

1. Go to [GitHub Settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Configure:
   - **Note:** `RELEASE_TOKEN_{{cookiecutter.project_name}}`
   - **Expiration:** Set an appropriate duration
   - **Scopes:** Select `repo` (full control of private repositories)
4. Click **"Generate token"** and copy it

#### Step 2: Add Token as Repository Secret

1. Go to your repository → **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. Configure:
   - **Name:** `RELEASE_TOKEN`
   - **Secret:** Paste your copied PAT
4. Click **"Add secret"**

#### Step 3: Configure Branch Protection with Rulesets

1. Go to your repository → **Settings → Rules → Rulesets**
2. Click **"New ruleset"** → **"New branch ruleset"**
3. Configure the ruleset:
   - **Ruleset name:** `Protect main`
   - **Enforcement status:** Active
   - **Target branches:** Click "Add target" → "Include by pattern" → enter `main`

4. Enable these rules:
   - ✅ **Restrict deletions** - Prevent branch deletion
   - ✅ **Require a pull request before merging**
     - Required approvals: `1` (or more)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
     - ✅ Require conversation resolution before merging
   - ✅ **Require status checks to pass**
     - ✅ Require branches to be up to date before merging
     - Add status checks (these come from the reusable CI workflow):
       - `ci / Run Pre-commit Checks` - Pre-commit hooks
       - `ci / Lint with Ruff` - Ruff linting
       - `ci / Run Tests with Pytest` - Pytest test suite
   - ✅ **Block force pushes**

5. Click **"Create"**

> **Note:** The checks appear as `ci / <job-name>` because they run inside the reusable workflow. You may need to run the workflow once before these checks appear in the dropdown.

### Commit Message Format

For semantic versioning:
- `fix:` → patch version (0.0.x)
- `feat:` → minor version (0.x.0)
- `BREAKING CHANGE:` → major version (x.0.0)

Example:
```bash
git commit -m "feat: add support for priority queues"
```

## Project Structure

```
{{cookiecutter.project_name}}/
├── src/{{cookiecutter.project_name}}/  # Application code
│   ├── custom_logger/         # JSON logging setup
│   ├── models/                # Pydantic models
│   ├── queue/                 # Redis/RQ integration
│   │   ├── connection.py      # Redis connection
│   │   ├── enqueue.py         # Job enqueueing
│   │   └── status.py          # Job status/results
│   ├── routers/               # FastAPI routers
│   │   └── jobs.py            # Job management endpoints
│   ├── workers/               # Worker tasks
│   │   └── tasks.py           # Task definitions
│   ├── main.py                # FastAPI app
│   └── settings.py            # Pydantic settings
├── tests/                     # Test suite
│   ├── conftest.py            # Pytest fixtures
│   └── unit/                  # Unit tests
├── logs/                      # Application logs
├── .github/workflows/         # CI/CD pipelines
├── docker-compose.yml         # Multi-container setup
├── Dockerfile                 # API container
├── Dockerfile.worker          # Worker container
├── dev_server.py              # Local development API server
├── dev_worker.py              # Local development worker process
├── pyproject.toml             # Dependencies & config
├── .env                       # Environment variables
└── README.md                  # This file
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and pre-commit hooks
5. Submit a pull request

Ensure all tests pass and coverage remains high.

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [RQ (Redis Queue)](https://python-rq.org/) - Simple job queues
- [Redis](https://redis.io/) - In-memory data store
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [lib_auth](https://github.com/jonathanvanleeuwen/lib_auth) - Authentication library
