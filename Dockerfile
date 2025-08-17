FROM python:3.12-bullseye AS builder

RUN pip install uv

WORKDIR /workspace

COPY pyproject.toml /workspace
COPY uv.lock /workspace

RUN uv export --format requirements.txt --output-file requirements.txt && \
    pip wheel -w /wheels -r requirements.txt

FROM python:3.12-bullseye AS runtime

ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000

WORKDIR /workspace
COPY --from=builder /wheels /wheels
COPY --from=builder /workspace/requirements.txt /workspace

RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY main.py /workspace

CMD ["sh", "-c", "fastapi run --host ${FASTAPI_HOST} --port ${FASTAPI_PORT}"]