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

# Bake the sentence-transformers model into the image.  Without this the model
# is fetched from Hugging Face on the first /api/readiness call, adding a ~90MB
# download to the very first user request.  HF_HOME is set explicitly (rather
# than relying on ~/.cache) so the weights live under /app and stay readable
# when the platform runs the container as a non-root user.
ENV HF_HOME=/app/hf_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
    && chmod -R a+rX /app/hf_cache

COPY backend/ .

# Ensure the sample data directory is present in the image so the container
# starts in "sample" mode on a clean clone without any host volume mount.
RUN mkdir -p data/sample

EXPOSE 8000

# Shell form so $PORT expands at runtime.  Railway, Render, Fly and HF Spaces
# all inject the port to bind as $PORT; a hardcoded port makes the container
# unreachable on those platforms.  Falls back to 8000 for local docker runs.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
