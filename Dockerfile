FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Set workdir
WORKDIR /app

# Copy project files
COPY . /app

# Install Python libraries (if needed)
RUN pip install -r requirements.txt

# Run the script
CMD ["python", "sweetflips_autoban.py"]
