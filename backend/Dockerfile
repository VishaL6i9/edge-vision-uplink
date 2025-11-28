FROM python:3.11-slim-bullseye

WORKDIR /backend_app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ffmpeg \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose ports
EXPOSE 3000
EXPOSE 8000

# Command to run the Reflex app (from /frontend context)
CMD ["bash", "-c", "cd /frontend && reflex run --env prod --backend-host 0.0.0.0"]