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

# Make sure the D-Bus directory exists
mkdir -p /var/run/dbus

# Start the D-Bus daemon
dbus-daemon --system --fork

# Wait a moment for D-Bus to start
sleep 2

# Start the Avahi daemon
/usr/sbin/avahi-daemon --daemonize

# Wait a moment for Avahi to start
sleep 2

# Activate virtual environment and run the publisher script with CSV string
. /opt/venv/bin/activate
exec python3 /app/publish_aliases.py "$MDNS_ALIASES"
