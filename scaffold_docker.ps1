$BaseDir = "c:\Users\User\projects\Agent-to-Agent Financial Collaboration\docker"
$ProjectRoot = "c:\Users\User\projects\Agent-to-Agent Financial Collaboration"

$Files = @{}

$Files["Dockerfile.api"] = @'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ .
COPY data/ /data/

# Run FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
'@

$Files["Dockerfile.worker"] = @'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ .
COPY data/ /data/

# In a real app, this would start Celery or a background task processor.
# For MVP, it just keeps the container alive.
CMD ["tail", "-f", "/dev/null"]
'@

$Files.Keys | ForEach-Object {
    $filePath = Join-Path $BaseDir $_
    $dirPath = Split-Path $filePath
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Force -Path $dirPath | Out-Null
    }
}

foreach ($key in $Files.Keys) {
    Set-Content -Path (Join-Path $BaseDir $key) -Value $Files[$key] -Encoding UTF8
}

$Compose = @'
version: '3.8'

services:
  api:
    build: 
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - mongo
      - qdrant

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    environment:
      - MONGODB_URI=mongodb://mongo:27017
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - mongo
      - qdrant
      - redis

  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
'@

Set-Content -Path (Join-Path $ProjectRoot "docker-compose.yml") -Value $Compose -Encoding UTF8

Write-Host "Docker files scaffolded successfully."
