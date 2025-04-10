FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt update && apt install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all the files from application folder
COPY ["app", "."]
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the necessary port for FastAPI
EXPOSE 8081

# Command to run FastAPI using Uvicorn
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
