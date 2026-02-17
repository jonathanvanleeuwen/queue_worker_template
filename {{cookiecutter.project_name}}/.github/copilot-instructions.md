# {{cookiecutter.project_name}} - AI Coding Agent Instructions

---
## 📋 Generic Code Standards (Reusable Across All Projects)

### Code Quality Principles

**DRY (Don't Repeat Yourself)**
- No duplicate code - extract common logic into reusable functions/classes
- If you copy-paste code, you're doing it wrong
- Shared utilities belong in `utils/` or helper modules

**CLEAN Code**
- **C**lear: Code intent is obvious from reading it
- **L**ogical: Functions do one thing, follow single responsibility principle
- **E**asy to understand: Junior developers should be able to review it
- **A**ccessible: Avoid clever tricks; prefer explicit over implicit
- **N**ecessary: Every line serves a purpose; no dead code

**Production-Grade Simplicity**
- Code must be production-ready (robust, tested, maintainable)
- Use the simplest solution that solves the problem completely
- Complexity is a last resort, not a goal
- **Target audience**: Code should be readable by junior software developers/data scientists

### Comments & Documentation Philosophy

**No Commented-Out Code**
- Never commit commented code blocks - use version control instead
- Delete unused code; git history preserves it if needed

**Docstrings: Only When Necessary**
- If code requires a docstring to be understood, it's probably too complex
- Refactor for clarity first, document as a last resort
- When used, docstrings explain **WHY**, not **HOW**
- Good function/variable names eliminate most documentation needs

**Comment Guidelines**
- Explain business logic rationale, not implementation mechanics
- Document non-obvious constraints or requirements
- If a comment explains what code does, rewrite the code to be self-explanatory
- Example:
  ```python
  # ❌ BAD: Explains what (obvious from code)
  # Loop through users and add to list
  for user in users:
      result.append(user)

  # ✅ GOOD: Explains why (non-obvious business rule)
  # OAuth tokens expire after 24h, but we refresh at 23h to prevent edge cases
  refresh_threshold = timedelta(hours=23)
  ```

### Code Organization Standards

**Function Design**
- Functions should do **one thing** and do it well
- If a function has "and" in its description, it likely does too much
- Keep functions short (aim for <20 lines when possible)

**Import Management**
- Keep `__init__.py` files minimal - only version info and essential public API
- Prefer explicit imports: `from module.submodule import specific_function`
- Avoid importing from `__init__.py` in application code
- Long import statements are fine; they show dependencies clearly

**Separation of Concerns**
- Each module/class has a single, well-defined responsibility
- Business logic separated from I/O, API layers, and presentation
- Configuration separated from implementation

**Readability First**
- Variable names should be descriptive: `user_count` not `uc`
- Consistent naming conventions throughout the project
- Code is read 10x more than written - optimize for reading

### Development Tooling Standards

**Python Version**
- Follow Python syntax for the version specified in `pyproject.toml` (currently >=3.12)
- Backwards compatibility is NOT required - use modern Python features

**Package & Environment Management**
- Use `uv` for all virtual environment operations
- Always create venvs with: `uv venv .venv`
- Install dependencies with: `uv pip install -e ".[dev]"`

**Code Quality Tools**
- **ruff**: Primary linter and formatter (replaces black, isort, flake8)
  - Format code: `ruff format .`
  - Check code: `ruff check .`
  - Fix issues: `ruff check --fix .`
- Follow ruff's formatting style (no manual formatting needed)

**Testing**
- **pytest**: Only testing framework to use
- Always run tests in the `.venv` environment
- Execute with: `.\.venv\Scripts\python.exe -m pytest -v` (picks up config from pyproject.toml)
- Coverage reports generated in `reports/htmlcov/`

### Documentation Requirements

**Always Update README.md**
- When adding new features, **immediately update README.md** with:
  - Usage examples showing the new functionality
  - Configuration options if applicable
  - Output/artifact descriptions
  - Integration instructions if needed
- When changing how artifacts are generated (models, figures, metrics):
  - Update the "Generated Outputs" section
  - Include directory structure examples
  - Document file formats and contents
- README must stay synchronized with code - outdated docs are worse than no docs

**Documentation Standards**
- Examples must be runnable (copy-paste should work)
- Include both CLI and programmatic usage where applicable
- Show realistic use cases, not toy examples
- Explain WHY features exist, not just HOW to use them

### Meta-Instruction
**Keep these instructions updated** based on chat interactions when patterns emerge or decisions are made that should guide future development.

---

## Project Architecture

**Application Pattern: Router → Worker Separation**
- **Routers** ([routers/](routers/)): Handle HTTP layer, request validation, authentication, and response formatting
- **Workers** ([workers/](workers/)): Pure business logic functions (no HTTP dependencies)
- **Why**: Enables unit testing business logic without HTTP mocking; clear separation of concerns

**Authentication Flow**
- Dual authentication system in [auth/dependencies.py](auth/dependencies.py):
  1. **API Keys**: SHA256-hashed keys stored in base64-encoded JSON via environment variable `API_KEYS`
  2. **OAuth 2.0**: GitHub/Google providers with JWT tokens
- Authentication tries API key first, then OAuth (see `create_auth()` factory pattern)
- On auth failure: 307 redirect to `/static/` (authentication frontend)
- **Access user info** in routes: `request.state.user_info` (populated by auth middleware)

**Configuration Management**
- Uses Pydantic Settings ([settings.py](settings.py)) with `.env` file support
- API keys are decoded and hashed at startup (see `process_api_keys()` validator)
- Settings cached with `@lru_cache` - **must clear cache in tests** (see `conftest.py`)

**Logging System**
- Structured JSON logging to `logs/{project_name}.log.jsonl`
- Queue-based async handler (see [custom_logger/setup/setup_logger.py](custom_logger/setup/setup_logger.py))
- **File logging auto-disabled during pytest** (detects `PYTEST_CURRENT_TEST` env var)

## Development Workflow

**Initial Setup**
```bash
uv venv .venv                    # Create virtual environment with uv
uv pip install -e ".[dev]"      # Install package and dev dependencies
pre-commit install              # Install pre-commit hooks
pre-commit run --all-files      # Run hooks on all files (REQUIRED before first commit)
```

**Code Quality**
```bash
ruff format .                   # Format all code
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix issues
```

**Running Locally**
```bash
python dev_server.py            # Runs on http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Testing**
```bash
pytest                          # Run all tests with coverage (reports/htmlcov/)
pytest -v tests/unit/           # Verbose unit tests only
pytest -k "test_add"            # Run specific test pattern
```

**Test Patterns** (see [tests/conftest.py](tests/conftest.py))
- Override `get_settings()` dependency with test settings
- Always use fixtures: `client`, `admin_headers`, `user_headers`
- Settings cache must be cleared: `get_settings.cache_clear()`
- Test API with `TestClient(app)` - no real HTTP server needed

## Code Conventions

**File Organization**
```
src/{{cookiecutter.project_name}}/
├── main.py           # FastAPI app initialization, router includes
├── settings.py       # Pydantic settings (all env vars here)
├── routers/          # HTTP endpoints (one file per resource)
├── workers/          # Business logic (pure functions)
├── queue/            # RQ queue utilities
├── models/           # Pydantic request/response models
├── custom_logger/    # Logging configuration
└── utils/            # Shared utilities
```

**Dependency Injection Pattern**
- Module-level singletons for repeated dependencies (avoids B008 linter):
  ```python
  _security_bearer = Security(bearer_scheme)
  _depends_settings = Depends(get_settings)

  def endpoint(credentials = _security_bearer, settings = _depends_settings):
      pass
  ```

**Adding New Authenticated Endpoints**
1. Create worker function in `workers/` (business logic only)
2. Create router in `routers/` with dependency: `dependencies=[Depends(auth_dependency)]`
3. Access user: `user_info = request.state.user_info`
4. Include router in `main.py`: `app.include_router(your_router, dependencies=[...])`

**API Keys Management**
- Use `src/{{cookiecutter.project_name}}/auth/secrets_b64.py` to encode/decode API keys
- Format: `{"key": {"username": "name", "roles": ["admin", "user"]}}`

## CI/CD Pipeline

**On Pull Request to main**
- Pre-commit hooks (ruff, isort, trailing-whitespace, etc.)
- pytest with coverage

**On Merge to main** (requires `RELEASE_TOKEN` secret)
1. Coverage report generated and committed to README
2. Semantic versioning based on commit messages:
   - `fix:` → patch (1.0.x)
   - `feat:` → minor (1.x.0)
   - `BREAKING CHANGE:` → major (x.0.0)
3. Build wheel and publish to GitHub Releases

**Commit Message Format** (for semantic release)
```
<type>: <description>

[optional body]
```
Types: `fix`, `feat`, `docs`, `chore`, `test`, `refactor`

## Common Pitfalls

- **Don't commit directly to main** - pre-commit hook will block it
- **Settings cache** - Always clear in tests: `get_settings.cache_clear()`
- **Authentication testing** - Use fixtures, don't hardcode tokens
- **Worker functions** - Must be pure, no FastAPI dependencies
- **Role checks** - Roles are arrays, use `any(role in user_roles for role in allowed_roles)`
