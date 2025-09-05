# QR-Info-Portal Development Container
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Build tools
        build-essential \
        pkg-config \
        # Database tools
        postgresql-client \
        redis-tools \
        sqlite3 \
        # Image processing
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        # Security tools
        openssl \
        ca-certificates \
        # Monitoring & Performance
        htop \
        curl \
        wget \
        # Font support for QR generation
        fontconfig \
        fonts-dejavu-core \
        # Development tools
        git \
        vim \
        nano \
        tree \
        jq \
        # Network tools
        netcat \
        telnet \
        # Process management
        supervisor \
    && apt-get autoremove -y && apt-get clean -y

# Install additional Python tools globally
RUN pip3 install --no-cache-dir \
    # Development servers
    flask-cors \
    watchdog \
    # Security scanning
    pip-audit \
    # Performance monitoring
    py-spy \
    # Code quality
    pre-commit \
    # API testing
    httpie \
    # Database migration
    alembic

# Create workspace structure
WORKDIR /workspace
RUN mkdir -p \
    /workspace/logs \
    /workspace/data \
    /workspace/screenshots \
    /workspace/.venv \
    /workspace/tmp

# Set up non-root user permissions
RUN chown -R vscode:vscode /workspace

# Switch to vscode user
USER vscode

# Set environment variables
ENV PYTHONPATH=/workspace
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

# Create virtual environment
RUN python -m venv /workspace/.venv
ENV PATH="/workspace/.venv/bin:$PATH"

# Copy requirements first for better Docker layer caching
COPY requirements*.txt /workspace/
RUN source /workspace/.venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r /workspace/requirements.txt && \
    pip install -r /workspace/requirements-dev.txt

# Default command
CMD ["bash"]