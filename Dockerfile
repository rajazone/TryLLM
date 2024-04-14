# Stage 1: Build stage
FROM python:3.9 AS builder

# Install git and git-lfs
RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y software-properties-common && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install -y git-lfs && \
    git lfs install

# Clone the public GitHub repository
RUN git clone https://huggingface.co/KoalaAI/Text-Moderation /app

# Stage 2: Final stage
FROM python:3.9

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Install system dependencies for PyTorch
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

RUN pip install gunicorn

# Set up a working directory
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip install torch torchvision torchaudio

# Copy the cloned repository from the builder stage
COPY --from=builder /app /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the Flask port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]