FROM python:3.11-slim AS backend-base

WORKDIR /app/backend

# Install OS deps needed by spaCy / pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY backend/ .

# Ensure the sample data directory is present in the image so the container
# starts in "sample" mode on a clean clone without any host volume mount.
RUN mkdir -p data/sample

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
