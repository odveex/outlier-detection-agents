# Use Python 3.11 slim-bookworm as the base image
FROM python:3.11-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    git \
    # Dependencies for numpy, pandas, scikit-learn
    libopenblas-dev \
    gfortran \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt /app/
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim-bookworm AS runner

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime dependencies for scientific packages
    libopenblas0 \
    # Bookworm has SQLite 3.40+ which meets the 3.35+ requirement
    # Add other runtime dependencies as needed
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels and install dependencies
COPY --from=builder /app/wheels /app/wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /app/wheels/* \
    && pip install --no-cache-dir uvicorn

# Copy project
COPY . /app/

# Expose the port the app runs in
EXPOSE 8000

# Define the command to start the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]