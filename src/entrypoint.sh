#!/bin/bash

# Environment variable validation
if [ -z "$MDNS_ALIASES" ]; then
    echo "Error: MDNS_ALIASES environment variable is not set or empty"
    echo "Please provide aliases in comma-separated format via MDNS_ALIASES environment variable"
    exit 1
fi

echo "Using environment variable configuration for mDNS aliases"
echo "MDNS_ALIASES content:"
echo "$MDNS_ALIASES"

# Pass the raw CSV string to Python for parsing
echo "Passing aliases to Python for parsing and publishing"

# Make sure the D-Bus directory exists and clean up any stale files
mkdir -p /var/run/dbus

# Remove any existing D-Bus PID file to prevent startup conflicts
rm -f /run/dbus/dbus.pid /var/run/dbus/dbus.pid

# Start the D-Bus daemon
echo "Starting D-Bus daemon..."
if dbus-daemon --system --fork; then
    echo "D-Bus daemon started successfully"
else
    echo "Failed to start D-Bus daemon"
    exit 1
fi

# Wait a moment for D-Bus to start
sleep 2

# Remove any existing Avahi PID file to prevent startup conflicts
rm -f /run/avahi-daemon/pid /var/run/avahi-daemon/pid

# Start the Avahi daemon
echo "Starting Avahi daemon..."
if /usr/sbin/avahi-daemon --daemonize; then
    echo "Avahi daemon started successfully"
else
    echo "Failed to start Avahi daemon"
    exit 1
fi

# Wait a moment for Avahi to start
sleep 2

# Activate virtual environment and run the publisher script with CSV string
. /opt/venv/bin/activate
exec python3 -u /app/publish_aliases.py "$MDNS_ALIASES"
