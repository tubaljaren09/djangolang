# Use the official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for Selenium, Chromium, and Xvfb
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
    libappindicator1 \
    libindicator7 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set display port for headless browser
ENV DISPLAY=:99

# Create and set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .  
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the project files into the container
COPY . .

# Expose port (typically 8000 for Django)
EXPOSE 8000

# Run the application using Gunicorn (for production)
CMD ["gunicorn", "djangolang.wsgi:application", "--bind", "0.0.0.0:8000"]
