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
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install playwright
RUN pip install playwright && playwright install chromium

# Set workdir
WORKDIR /app

# Copy files
COPY . /app

# Run
CMD ["python", "sweetflips_autoban.py"]
