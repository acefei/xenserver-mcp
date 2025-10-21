FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY main.py .
COPY .env .

# Install dependencies using uv (no-install-project since we're not making it installable)
RUN uv sync --no-install-project --frozen

EXPOSE 8081

# Use uv to run the application
CMD ["uv", "run", "python", "main.py"]