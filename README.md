# queue_worker_template
A cookiecutter template for queue worker applications with FastAPI, RQ, and Redis.

## Features
* FastAPI application with dual authentication (API Keys + OAuth 2.0) via [lib_auth](https://github.com/jonathanvanleeuwen/lib_auth)
* Built-in support for GitHub, Google, Microsoft, GitLab, LinkedIn, and Discord OAuth providers
* Role-based access control with granular permissions
* Redis-backed job queue with RQ (Redis Queue)
* RQ Dashboard for monitoring jobs and workers
* Worker pattern for clean separation between routes and business logic
* Structured JSON logging with request tracking
* Docker and Docker Compose setup for easy deployment
* Automated testing with pytest and fakeredis
* Pre-commit hooks for code quality (ruff, isort, trailing whitespace, etc.)
* Semantic release using GitHub Actions
* Automatic code coverage report in README
* Automatic wheel build and GitHub Release publishing
* Modern Python packaging with pyproject.toml

*Notes*
Workflows trigger when a branch is merged into main!
To install, please follow all the instructions in this readme.
The workflows require a PAT set as secret (see GitHub Repository Setup section for instructions).
See the notes on how to create semantic releases at the bottom of the README.

If you followed all the steps, whenever a PR is merged into `main`, the workflows are triggered and should:
* Run pre-commit checks (fail fast on code quality issues)
* Ensure that tests pass (before merge)
* Create a code coverage report and commit that to the bottom of the README
* Create a semantic release (if you follow the semantic release pattern) and automatically update the version number of your code
* Build a wheel and publish it as a GitHub Release asset


# Install
Cookiecutter template:
* Cd to your new queue worker application location
  * `cd /your/new/application/path/`
* Install cookiecutter using uv (or pip)
  * `uv pip install cookiecutter` (or `pip install cookiecutter`)
* Run the cookiecutter template from this GitHub repo
  * `cookiecutter https://github.com/YOUR_USERNAME/queue_worker_template`
* Fill in your new application values (including your GitHub username for CODEOWNERS)
* Create new virtual environment
  *  `uv venv .venv` (or `python -m venv .venv`)
* Activate the environment and install application with dev dependencies
  *  `uv pip install -e ".[dev]"` (or `pip install -e ".[dev]"`)
* Install pre-commit hooks
  * `pre-commit install`
* **Run pre-commit on all files** (important for initial commit!)
  * `pre-commit run --all-files`
* Copy the .env.example file to .env and configure your settings
  * `cp .env.example .env`
* Check proper install by running tests
  * `pytest`

## Authentication Configuration

The template uses [lib_auth](https://github.com/jonathanvanleeuwen/lib_auth) for authentication, supporting both API keys and OAuth 2.0.

### API Keys

API keys are stored in base64-encoded JSON in the `API_KEYS` environment variable (see `settings.py`). The template includes a default configuration for testing.

**To generate your own API keys:**

Use the included script in `src/{project_name}/auth/secrets_b64.py`:

```python
from your_project.auth.secrets_b64 import encode_secrets, decode_secrets

# Create your API keys
api_keys = {
    "your-secret-admin-key": {"username": "admin", "roles": ["admin", "user"]},
    "your-secret-user-key": {"username": "user", "roles": ["user"]},
}

# Encode for environment variable
encoded = encode_secrets(api_keys)
print(f"API_KEYS={encoded}")

# Decode to verify
decoded = decode_secrets(encoded)
print(decoded)
```

### OAuth 2.0

Configure OAuth in your `.env` file:

```env
OAUTH_PROVIDER=github  # or google, microsoft, gitlab, linkedin, discord
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_SECRET_KEY=your-jwt-secret-key-min-32-chars
```

**OAuth Setup:**
- **GitHub**: [Create OAuth App](https://github.com/settings/developers)
- **Google**: [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
- For other providers, see the [lib_auth documentation](https://github.com/jonathanvanleeuwen/lib_auth)

---

## Running with Docker Compose

The template includes a complete Docker Compose setup with FastAPI app, Redis, RQ workers, and RQ Dashboard.

**Quick start:**

```bash
docker-compose up --build
```

This starts:
- **FastAPI API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RQ Dashboard**: http://localhost:9181

**Stop services:**

```bash
docker-compose down
```

---

## Project Structure

```
{{cookiecutter.project_name}}/
├── src/
│   └── {{cookiecutter.project_name}}/
│       ├── auth/              # Authentication utilities
│       ├── custom_logger/      # JSON logging setup
│       ├── models/             # Pydantic models
│       ├── queue/              # RQ queue utilities
│       ├── routers/            # FastAPI route handlers
│       ├── workers/            # Background task functions
│       ├── main.py             # FastAPI app initialization
│       └── settings.py         # Pydantic settings
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   └── unit/                   # Unit tests
├── logs/                       # Application logs (JSONL)
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # API container
├── Dockerfile.worker           # Worker container
├── dev_server.py               # Local development server
└── pyproject.toml              # Python package config
```

---

## Development Workflow

**Local development:**

```bash
python dev_server.py  # Runs on http://localhost:8000
```

**Run tests:**

```bash
pytest                          # Run all tests with coverage
pytest -v tests/unit/           # Verbose unit tests only
pytest -k "test_pattern"        # Run specific test pattern
```

**Code quality:**

```bash
ruff format .                   # Format all code
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix issues
```

---

## Turn the new local cookiecutter code into a git repo

Open git bash
```bash
cd C:/your/code/directory
```
To init the repository, add all files and commit
```bash
git init
git add *
git add .github
git add .gitignore
git add .pre-commit-config.yaml
git add .dockerignore
git add .env.example
git commit -m "fix: Initial commit"
```

To add the new git repository to your GitHub:
*  Go to [github](https://github.com/).
-  Log in to your account.
-  Click the [new repository](https://github.com/new) button in the top-right. You'll have an option there to initialize the repository with a README file, but don't. Leave the repo empty
- Give the new repo the same name you gave your repo with the cookiecutter
-  Click the "Create repository" button.

Now we want to make sure we are using `main` as main branch name and push the code to GitHub
```bash
git remote add origin https://github.com/username/new_repo_name.git
git branch -M main
git push -u origin main
```

---

# 🔒 GitHub Repository Setup

Complete these steps in order to enable the CI/CD pipeline.

## Step 1: Create the Release Token (PAT)

The workflow needs a Personal Access Token to push to the protected `main` branch.

### Create a Fine-Grained PAT (Recommended - More Secure)

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. Click **"Generate new token"**
3. Configure the token:
   - **Token name:** `RELEASE_TOKEN_YOUR_REPO_NAME`
   - **Expiration:** Choose an appropriate duration (recommend 90 days, set a reminder to rotate)
   - **Repository access:** Select "Only select repositories" → choose your repository
   - **Permissions:**
     - **Contents:** Read and write (for pushing commits and tags)
     - **Metadata:** Read-only (automatically selected)
4. Click **"Generate token"**
5. **Copy the token immediately** - you won't see it again!

### Alternative: Classic PAT (Less Secure, Not Recommended)

If fine-grained tokens are not available:

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Select scopes:
   - **repo** (all sub-scopes)
4. Click **"Generate token"**
5. **Copy the token immediately**

---

## Step 2: Add the Token as a Repository Secret

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **"New repository secret"**
4. Configure:
   - **Name:** `RELEASE_TOKEN`
   - **Secret:** Paste the token you just created
5. Click **"Add secret"**

---

## Step 3: Configure Branch Protection (Optional but Recommended)

Protect the `main` branch to enforce quality gates:

1. Go to **Settings → Branches**
2. Click **"Add rule"** under "Branch protection rules"
3. Configure:
   - **Branch name pattern:** `main`
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1 (or more)
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Search for and select: `test` (once it runs the first time)
   - ✅ **Require conversation resolution before merging**
   - ✅ **Do not allow bypassing the above settings**
4. Click **"Create"**

---

## Step 4: Enable Renovate (Optional but Recommended)

Renovate keeps your dependencies up to date automatically.

1. Install the [Renovate GitHub App](https://github.com/apps/renovate)
2. Grant access to your repository
3. Renovate will create a PR to configure itself
4. Merge the configuration PR
5. Renovate will automatically create PRs for dependency updates

---

## CI/CD Pipeline Overview

### On Pull Request to `main`
- Pre-commit hooks run (ruff, isort, trailing-whitespace, etc.)
- All tests run with pytest
- Coverage report generated

### On Merge to `main`
1. Coverage report updated and committed to README
2. Semantic version determined from commit messages:
   - `fix:` → patch (0.0.x)
   - `feat:` → minor (0.x.0)
   - `BREAKING CHANGE:` → major (x.0.0)
3. Wheel built
4. GitHub Release created with wheel as asset

---

## Semantic Release - Commit Message Format

To trigger semantic releases, use this commit message format:

```
<type>: <description>

[optional body]

[optional footer]
```

### Types
- `fix:` - Bug fix (triggers patch release: 1.0.x)
- `feat:` - New feature (triggers minor release: 1.x.0)
- `docs:` - Documentation only
- `chore:` - Maintenance tasks
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `ci:` - CI/CD changes

### Breaking Changes
Add `BREAKING CHANGE:` in the footer to trigger a major version bump:

```
feat: redesign API endpoints

BREAKING CHANGE: API endpoints have been restructured
```

### Examples

```bash
# Patch release (1.0.0 → 1.0.1)
git commit -m "fix: resolve redis connection timeout"

# Minor release (1.0.0 → 1.1.0)
git commit -m "feat: add job cancellation endpoint"

# Major release (1.0.0 → 2.0.0)
git commit -m "feat: redesign queue system

BREAKING CHANGE: Queue names must now use snake_case"
```

---

## Queue Worker Architecture

### Components

**API (FastAPI)**
- Handles job submission via REST endpoints
- Authentication and authorization
- Job status queries
- Queue statistics

**Workers (RQ)**
- Process background jobs asynchronously
- Multiple workers can run in parallel
- Automatic retry on failure
- Job result persistence

**Redis**
- Job queue storage
- Job metadata
- Worker coordination
- Result caching

**RQ Dashboard**
- Web UI for monitoring
- View job status, failures, and successes
- Worker management
- Queue statistics

### Adding New Tasks

1. Create task function in `src/{project_name}/workers/tasks.py`:

```python
def my_new_task(param1: str, param2: int) -> dict:
    """
    Brief description of what this task does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dict with task results
    """
    # Your task logic here
    result = do_something(param1, param2)
    return {"result": result}
```

2. Task is automatically discovered and available via `/api/jobs/enqueue`

3. Test the task:

```python
# tests/unit/test_tasks.py
def test_my_new_task():
    result = my_new_task("test", 42)
    assert result["result"] == expected_value
```

---

## License

MIT License - see LICENSE file for details
