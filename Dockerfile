# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    unzip \
    ffmpeg \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose ports for the frontend and backend
EXPOSE 3000
EXPOSE 8000

# Run the app.
# By default, `reflex run` starts the frontend on port 3000 and the backend on port 8000.
# We use --frontend-host and --backend-host to make the app accessible from outside the container.
CMD ["reflex", "run", "--backend-host", "0.0.0.0"]
