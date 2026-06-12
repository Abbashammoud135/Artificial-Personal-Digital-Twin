FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configure APT retries, timeouts, and disable pipelining/caching to prevent "Hash Sum mismatch"
RUN echo 'Acquire::Retries "10";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "300";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Pipeline-Depth "0";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::No-Cache "true";' >> /etc/apt/apt.conf.d/80-retries

# Install system dependencies
# 1. gnupg, curl, build-essential, unixodbc, unixodbc-dev (for pyodbc)
# 2. ghostscript, python3-tk (for camelot table parsing)
RUN apt-get clean && apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    curl \
    gnupg2 \
    build-essential \
    unixodbc \
    unixodbc-dev \
    ghostscript \
    python3-tk \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first for Docker caching
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for uploads if it doesn't exist
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Command to run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
