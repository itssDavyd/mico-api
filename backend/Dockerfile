FROM python:3.13-slim

RUN apt-get update && apt-get install -y ffmpeg fonts-dejavu && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock* ./

RUN pip install --no-cache-dir uv
RUN uv sync

COPY . .
RUN mkdir -p ./audio ./pdfs ./assets

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "python", "main.py"]
