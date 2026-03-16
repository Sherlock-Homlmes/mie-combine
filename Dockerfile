FROM python:3.14-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

ENTRYPOINT [ "uv", "run" ]
CMD [ "python", "main.py" ]
