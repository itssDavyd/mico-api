FROM python:alpine

RUN apk add --no-cache ttf-dejavu

WORKDIR /app
COPY pyproject.toml uv.lock* ./

RUN pip install --no-cache-dir uv
RUN uv sync

COPY . .
RUN mkdir -p ./audio ./pdfs ./assets

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
