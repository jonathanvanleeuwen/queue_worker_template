FROM python:3.12-slim

ENV APP_NAME="{{cookiecutter.project_name}}"
ENV UVICORN_ENTRYPOINT="{{cookiecutter.project_name}}.main:app"

EXPOSE 8000

# Copy dependency files
COPY src /opt/app-root/src
COPY pyproject.toml /opt/app-root/
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Install Git (required for uv to install lib_auth from GitHub)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /opt/app-root/

# Install dependencies
RUN uv pip install --system -e .

# Create logs directory
RUN mkdir -p /opt/app-root/logs

ENTRYPOINT ["/entrypoint.sh"]

# docker build -t {{cookiecutter.project_name}}:latest .
