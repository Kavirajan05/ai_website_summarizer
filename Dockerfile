FROM python:3.11-slim

# Install wget and unzip
RUN apt-get update && apt-get install -y wget unzip gnupg2 curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install Google Chrome automatically resolving dependencies
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set up the entrypoint script to parse Railway's custom commands
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# Let Railway pass the PORT environment variable natively
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
