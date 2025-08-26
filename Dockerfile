FROM python:3.12-slim-bullseye AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml /app
COPY uv.lock /app

RUN uv export --format requirements-txt --output-file requirements.txt && \
    pip install --no-cache-dir --prefix /install -r requirements.txt

FROM python:3.12-slim-bullseye AS runtime

ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000

WORKDIR /app
COPY --from=builder /install /usr/local

COPY main.py /app
COPY static /app/static

CMD ["sh", "-c", "fastapi run --host ${FASTAPI_HOST} --port ${FASTAPI_PORT}"]
