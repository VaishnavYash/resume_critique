FROM python:3.11-slim

#Install CA Certificates
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

EXPOSE 8080

# Cloud Run listens on port 8080
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080","--timeout-keep-alive","120"]
