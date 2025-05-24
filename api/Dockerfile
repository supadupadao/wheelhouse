FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONPATH=/app
ENV UV_PROJECT=/app/api
WORKDIR /app

COPY ./api /app/api
COPY ./libs /app/libs
RUN uv sync --locked

CMD ["uv", "run", "fastapi", "run", "./api/main.py"]