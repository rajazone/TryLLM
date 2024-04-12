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

# Install PyTorch and torchvision (replace torch==x.x.x and torchvision==x.x.x with your desired versions)
RUN pip install torch==1.10.0+cpu torchvision==0.11.1+cpu torchaudio==0.10.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install gunicorn
# Set up a working directory
WORKDIR /app

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