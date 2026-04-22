FROM ghcr.io/astral-sh/uv:python3.14-alpine

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ src/

RUN uv sync --frozen --no-dev

# Make port 7100 available to the world outside this container
EXPOSE 7100

ENTRYPOINT ["uv", "run", "--no-sync", "python", "-um", "scraparr.scraparr"]
