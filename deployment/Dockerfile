FROM python:3.10-slim

# Install system dependencies for OpenCV and GL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and configs
COPY src/ /app/src/
COPY configs/ /app/configs/
COPY models/ /app/models/
COPY deployment/api/ /app/deployment/api/

EXPOSE 8000

CMD ["uvicorn", "deployment.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
