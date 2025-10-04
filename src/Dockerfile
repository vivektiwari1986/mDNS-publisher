# Dockerfile
FROM alpine:latest

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

# Copy scripts to app directory
COPY entrypoint.sh /app/
COPY publish_aliases.py /app/
COPY mdns_publisher.py /app/
RUN chmod +x /app/entrypoint.sh /app/publish_aliases.py /app/mdns_publisher.py

# Set working directory
WORKDIR /app

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
