FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN poetry install --no-dev --no-root --no-interaction --no-ansi

EXPOSE 8877

CMD ["poetry", "run", "jupyter", "lab", "--allow-root", "--ip=0.0.0.0", "--no-browser", "--port=8877", "--NotebookApp.token=''", "--NotebookApp.password=''"]
