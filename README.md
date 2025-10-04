# mDNS Publisher for Docker

This package provides a containerized solution for publishing multiple mDNS (Avahi) aliases on your local network. It's particularly useful for homelab setups where you want to access different services using `.local` domains. 

The container uses `mdns-publish-cname` to publish all your aliases simultaneously, making them resolve to your Docker host's IP address. You'll need a reverse proxy (like Traefik or nginx) to route the traffic from these `.local` domains to your actual services.

## Features

- **Environment Variable Configuration**: No config files needed - just set `MDNS_ALIASES`
- **Simple and Reliable**: Direct execution of `mdns-publish-cname` with all aliases
- **Input Validation**: Automatically trims whitespace and skips empty entries
- **Minimal Footprint**: Based on Alpine Linux for small image size
- **Host Network Integration**: Proper mDNS functionality with host networking
- **Clean Logging**: Clear output showing which aliases are being published

## Prerequisites

- Docker
- Docker Compose (optional)
- Linux host with network access

## Quick Start

Deploy using Docker Compose with environment variable configuration:

```yaml
services:
  mdns-publisher:
    build:
      # Replace with your repository path if you've forked it
      context: https://github.com/vivektiwari1986/mDNS-publisher.git#dev:src
    container_name: mdns-publisher
    network_mode: host  # Required for mDNS to work properly
    restart: unless-stopped
    environment:
      - MDNS_ALIASES=homepage.local,filebrowser.local,plex.local,dashboard.local
```

Save this as `docker-compose.yml` and run:
```bash
docker compose up -d
```

## Alternative Deployment (Docker CLI)

If you prefer using Docker directly:

```bash
# Build the image
docker build -t mdns-publisher https://github.com/vivektiwari1986/mDNS-publisher.git#dev:src

# Run the container
docker run -d \
  --name mdns-publisher \
  --network host \
  --restart unless-stopped \
  -e MDNS_ALIASES="homepage.local,filebrowser.local,plex.local,dashboard.local" \
  mdns-publisher
```

## Configuration

### Environment Variable Format
Configure your mDNS aliases using the `MDNS_ALIASES` environment variable with comma-separated values. Each hostname should end with `.local`. For example:

```bash
MDNS_ALIASES="service1.local,service2.local,dashboard.local,monitoring.local"
```

### Advanced Configuration Examples

**Basic setup:**
```yaml
environment:
  - MDNS_ALIASES=app.local,api.local
```

**Multiple services:**
```yaml
environment:
  - MDNS_ALIASES=homepage.local,portainer.local,grafana.local,prometheus.local,jellyfin.local
```

### Environment Variables

- **`MDNS_ALIASES`** (required): Comma-separated list of mDNS aliases to publish


### Verification

To verify your aliases are working:

1. Check container logs:
```bash
docker logs mdns-publisher
```

You should see output like:
```
Starting D-Bus daemon...
D-Bus daemon started successfully
Starting Avahi daemon...
Avahi daemon started successfully
Found 4 aliases to publish:
  - homepage.local
  - filebrowser.local
  - plex.local
  - dashboard.local
Executing: /opt/venv/bin/mdns-publish-cname homepage.local filebrowser.local plex.local dashboard.local
```

2. Test an alias:
```bash
ping homepage.local
```

## Troubleshooting

1. **If aliases aren't resolving:**
   - Verify the container is running: `docker ps`
   - Check container logs: `docker logs mdns-publisher`
   - Ensure host networking is enabled (`network_mode: host`)
   - Verify the `MDNS_ALIASES` environment variable is set correctly

2. **For container startup issues:**
   - Check if avahi-daemon is running in the container
   - Verify D-Bus is functioning properly
   - Ensure no port conflicts with host avahi-daemon

3. **Environment variable issues:**
   - Ensure `MDNS_ALIASES` is not empty
   - Check for proper comma separation
   - Verify all aliases end with `.local`
   - Remove any trailing commas or extra spaces

4. **Publishing issues:**
   - The container runs `mdns-publish-cname` directly with all aliases
   - If the process exits, the container will restart (with `restart: unless-stopped`)
   - Check that all aliases are valid `.local` domains


## Contributing

Feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Avahi project for providing the mDNS implementation
- Docker for containerization
- Alpine Linux for the base image
