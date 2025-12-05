# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y ...

# Copy the requirements file into the container at /app
# Copy the backend requirements file
COPY backend/requirements.txt .

# Install any needed packages specified in requirements.txt
# Use a mirror for faster installation in China (optional but recommended for Aliyun)
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy the entire project
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose port 8000
EXPOSE 8000

# Run start.sh when the container launches
CMD ["./start.sh"]
