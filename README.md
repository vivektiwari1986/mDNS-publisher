# mDNS Publisher for Docker

This package provides a containerized solution for publishing multiple mDNS (Avahi) aliases on your local network. It's particularly useful for homelab setups where you want to access different services using `.local` domains. Note: You must have a reverse proxy solution (Traefik, nginx) that points the xyz.local domain to the IP address and port of the hosted service. mDNS publisher will only publish DNS records for pointing xyz.local to the docker host port 80.

## Features

- **Environment Variable Configuration**: No config files needed - just set `MDNS_ALIASES`
- **Parallel Processing**: All aliases are published simultaneously for faster startup
- **Robust Error Handling**: Individual alias failures don't stop other aliases from publishing
- **Comprehensive Logging**: Detailed output showing success/failure status for each alias
- **Graceful Shutdown**: Handles interrupts cleanly with proper cleanup
- **Input Validation**: Automatically trims whitespace and skips empty entries
- **Minimal Footprint**: Based on Alpine Linux for small image size
- **Host Network Integration**: Proper mDNS functionality with host networking

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

**With custom timeout and failure behavior:**
```yaml
environment:
  - MDNS_ALIASES=service1.local,service2.local
  - MDNS_TIMEOUT=180  # 3 minutes timeout per alias (default: 120)
  - EXIT_ON_FAILURE=false  # Keep retrying on failure (default: true)
```

### Environment Variables

- **`MDNS_ALIASES`** (required): Comma-separated list of mDNS aliases to publish
- **`MDNS_TIMEOUT`** (optional): Timeout in seconds for each alias publishing attempt (default: 120)


### Verification

To verify your aliases are working:

1. Check container logs:
```bash
docker logs mdns-publisher
```

You should see output like:
```
Found 4 aliases to publish:
  - homepage.local
  - filebrowser.local
  - plex.local
  - dashboard.local

Starting parallel alias publishing...
SUCCESS: homepage.local published successfully
SUCCESS: filebrowser.local published successfully
SUCCESS: plex.local published successfully
SUCCESS: dashboard.local published successfully

=== Alias Publishing Summary ===
Total aliases processed: 4
Successful: 4
Failed: 0

At least one alias published successfully. Service will continue running...
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

4. **Parallel publishing failures:**
   - Check logs for individual alias failures
   - Some aliases may succeed while others fail
   - The service continues running if at least one alias succeeds


## Contributing

Feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Avahi project for providing the mDNS implementation
- Docker for containerization
- Alpine Linux for the base image
