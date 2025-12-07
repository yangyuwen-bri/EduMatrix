# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y ...

# Copy the requirements file into the container at /app
# Copy the backend requirements file
COPY backend/requirements.txt .

# Install dependencies
# Use a mirror for faster installation in China
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Install huggingface_hub to download models
RUN pip install --no-cache-dir huggingface_hub -i https://pypi.tuna.tsinghua.edu.cn/simple

# Build argument for HF Mirror (can be overridden at build time)
ARG HF_ENDPOINT=https://hf-mirror.com
ENV HF_ENDPOINT=${HF_ENDPOINT}

# Copy the locally downloaded model directory to the container
# This requires running 'python download_model.py' first on the host
COPY models /app/models

# Set the MODEL_PATH environment variable for the application to use
ENV MODEL_PATH=/app/models/text2vec-base-chinese

# Copy the entire project
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose port 8000
EXPOSE 8000

# Run start.sh when the container launches
CMD ["./start.sh"]
