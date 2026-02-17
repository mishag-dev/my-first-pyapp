# Use a modern, stable Python slim image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all scripts into the container
# This ensures both satcom-statgen.py and satcom-consumer.py are available
COPY . .

# Python unbuffered ensures logs are sent to stdout immediately
ENV PYTHONUNBUFFERED=1

# We remove the hardcoded CMD so we can specify which script to run 
# in the Kubernetes 'command' field. 
# Providing a default just in case:
CMD ["python", "satcom-statgen.py"]