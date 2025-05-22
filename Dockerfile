# ──────────────── Stage 1: Build wheels ────────────────
FROM python:3.10-slim AS builder

WORKDIR /wheels

# Install only build-time deps, with no extra recommends
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libffi-dev \
      libssl-dev \
      curl \
      unzip \
      gnupg \
 && rm -rf /var/lib/apt/lists/*

# Copy and build wheels
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ──────────────── Stage 2: Runtime ────────────────
FROM python:3.10-slim

# Prevent python from writing pyc’s & buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99

WORKDIR /app

# Install only runtime deps (no build tools)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      chromium \
      chromium-driver \
      ca-certificates \
      fonts-liberation \
      libnss3 \
      libxss1 \
      libasound2 \
      libatk-bridge2.0-0 \
      libgtk-3-0 \
      libx11-xcb1 \
      xvfb \
 && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index \
      --find-links=/wheels \
      -r requirements.txt \
 && rm -rf /wheels

# Copy app sources
COPY . .

# Expose your Django port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "djangolang.wsgi:application", "--bind", "0.0.0.0:8000"]
