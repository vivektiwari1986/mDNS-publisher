# Dockerfile
FROM alpine:latest

# Version and metadata labels
LABEL version="1.0.0"
LABEL description="mDNS Publisher for Docker - Publishes multiple .local aliases"
LABEL maintainer="your-email@example.com"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.title="mDNS Publisher"
LABEL org.opencontainers.image.description="Containerized solution for publishing multiple mDNS aliases"
LABEL org.opencontainers.image.source="https://github.com/vivektiwari1986/mDNS-publisher"

# Install required packages including build dependencies
RUN apk add --no-cache \
    python3 \
    py3-virtualenv \
    py3-pip \
    avahi \
    avahi-tools \
    dbus \
    bash \
    gcc \
    musl-dev \
    python3-dev \
    dbus-dev \
    glib-dev

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python mDNS publisher in virtual environment
RUN . $VIRTUAL_ENV/bin/activate && pip install mdns-publisher

# Create directory for scripts and config
RUN mkdir -p /app

# Copy scripts and version file to app directory
COPY entrypoint.sh /app/
COPY publish_aliases.py /app/
COPY VERSION /app/
RUN chmod +x /app/entrypoint.sh /app/publish_aliases.py

# Set working directory
WORKDIR /app

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
