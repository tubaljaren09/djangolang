# Use the official Python base image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and to ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Selenium, Chromium, and headless browsing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    unzip \
    wget \
    gnupg \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    xvfb \
    chromium \
    chromium-driver \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Set the display environment variable for the headless browser
ENV DISPLAY=:99

# Create and set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Expose port 8000 (or whichever port your Django app uses)
EXPOSE 8000

# Use Gunicorn to run the Django app
# Replace 'djangoapp.wsgi:application' with the appropriate WSGI path for your project
CMD ["gunicorn", "djangolang.wsgi:application", "--bind", "0.0.0.0:8000"]
