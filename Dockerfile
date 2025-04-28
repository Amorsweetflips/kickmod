FROM cimg/python:3.10-browsers

# Install extra dependencies
RUN sudo apt-get update && sudo apt-get install -y \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    libasound2

# Set environment variables for Chromium
ENV CHROME_BIN="/usr/bin/google-chrome"
ENV PATH="$CHROME_BIN:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . /app
WORKDIR /app

# Run the bot
CMD ["python", "sweetflips_autoban.py"]
