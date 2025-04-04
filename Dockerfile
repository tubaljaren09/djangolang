# Use the official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    unzip \
    wget \
    gnupg \
    fonts-liberation \
    libnss3 \
    libxss1 \
    # Removed: libappindicator1, libindicator7 (if not needed)
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    xvfb \
    chromium \
    chromium-chromedriver \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set display port for headless browser
ENV DISPLAY=:99

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port (typically 8000 for Django)
EXPOSE 8000

# Run the application (adjust the command if needed)
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]
