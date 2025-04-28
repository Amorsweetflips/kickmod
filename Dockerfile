FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libglib2.0-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir playwright

# Install browsers and their deps
RUN playwright install --with-deps chromium

# Set workdir
WORKDIR /app

# Copy all project files
COPY . /app

# Run
CMD ["python", "sweetflips_autoban.py"]
