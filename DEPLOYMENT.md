# WebAI Deployment Guide

This guide covers the complete deployment process for the WebAI application with claude-code-api integration.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- Domain name (e.g., your-domain.com) with DNS configured
- Anthropic account for OAuth authentication

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd webai

# Copy environment template
cp .env.sample .env

# Edit environment variables
nano .env

# Run OAuth setup
./setup-oauth.sh

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Detailed Setup Steps

### 1. Environment Configuration

Create `.env` file from template:

```bash
cp .env.sample .env
```

Edit `.env` with your configuration:

```env
# Required configurations
SECRET_KEY=<generate-secure-random-key>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<your-secure-password>
DOMAIN_NAME=your-domain.com
LETSENCRYPT_EMAIL=admin@your-domain.com
```

Generate secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. OAuth Authentication Setup

The application uses OAuth authentication for claude-code-api. Run the setup script:

```bash
./setup-oauth.sh
```

Follow the prompts:
1. Open the provided URL in your browser
2. Log in with your Anthropic account
3. Copy the authorization code
4. Paste it when prompted

The authentication token will be saved to `./claude-config/claude_config.json`

### 3. SSL Certificate Setup

#### For Production (with Let's Encrypt)

First-time setup:
```bash
# Create required directories
mkdir -p certbot/conf certbot/www

# Get initial certificate
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@your-domain.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com \
  -d www.your-domain.com
```

#### For Development (self-signed)

```bash
# Install mkcert
sudo apt install mkcert

# Generate certificates
mkcert -install
mkcert localhost 127.0.0.1 ::1

# Move certificates
mkdir -p certbot/conf/live/localhost
mv localhost+2.pem certbot/conf/live/localhost/fullchain.pem
mv localhost+2-key.pem certbot/conf/live/localhost/privkey.pem
```

### 4. Docker Deployment

#### Development Environment

```bash
# Use development nginx config
mv nginx/conf.d/webai.conf nginx/conf.d/webai.conf.prod
mv nginx/conf.d/webai-dev.conf nginx/conf.d/webai.conf

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Production Environment

```bash
# Ensure production config is active
mv nginx/conf.d/webai-dev.conf nginx/conf.d/webai-dev.conf.bak
mv nginx/conf.d/webai.conf.prod nginx/conf.d/webai.conf

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 5. Verify Deployment

1. **Check container status:**
   ```bash
   docker-compose ps
   ```
   All containers should be "Up"

2. **Check OAuth authentication:**
   ```bash
   docker-compose exec claude-api ls -la /home/app/.config/claude/
   ```
   Should show `claude_config.json`

3. **Test web interface:**
   - Open https://your-domain.com
   - Log in with admin credentials
   - Send a test message

4. **Monitor logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f webapp
   ```

## Maintenance

### Certificate Renewal

Certificates are automatically renewed by the certbot container. To manually renew:

```bash
docker-compose exec certbot certbot renew
```

### Backup

Important data to backup:
- `.env` file
- `./claude-config/` directory (OAuth tokens)
- `./certbot/conf/` directory (SSL certificates)

```bash
# Create backup
tar -czf webai-backup-$(date +%Y%m%d).tar.gz \
  .env \
  claude-config/ \
  certbot/conf/
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f webapp
docker-compose logs -f claude-api
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 webapp
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check OAuth token exists: `ls -la ./claude-config/`
   - Re-run `./setup-oauth.sh`
   - Check claude-api logs: `docker-compose logs claude-api`

2. **WebSocket Connection Failed**
   - Check nginx configuration
   - Verify webapp is running: `docker-compose ps webapp`
   - Check browser console for errors

3. **SSL Certificate Issues**
   - Verify DNS is pointing to server
   - Check certbot logs: `docker-compose logs certbot`
   - Ensure ports 80/443 are open

4. **Container Won't Start**
   - Check logs: `docker-compose logs <service-name>`
   - Verify file permissions
   - Check disk space: `df -h`

### Debug Mode

Run in debug mode:
```bash
# Stop production
docker-compose down

# Run with debug output
FLASK_ENV=development docker-compose up
```

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes auth data)
docker-compose down -v

# Clean Docker system
docker system prune -a

# Start fresh
./setup-oauth.sh
docker-compose up -d
```

## Security Considerations

1. **Firewall Configuration**
   ```bash
   # Allow SSH, HTTP, HTTPS
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **File Permissions**
   ```bash
   # Secure sensitive files
   chmod 600 .env
   chmod 700 claude-config/
   ```

3. **Regular Updates**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade
   
   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

## Performance Tuning

1. **Adjust Worker Processes**
   
   Edit `.env`:
   ```env
   GUNICORN_WORKERS=4  # Adjust based on CPU cores
   GUNICORN_THREADS=2
   ```

2. **Monitor Resource Usage**
   ```bash
   # Container stats
   docker stats
   
   # System resources
   htop
   ```

3. **Log Rotation**
   
   Logs are automatically rotated by Docker. Configure in `docker-compose.yml`:
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

## Support

For issues or questions:
1. Check application logs
2. Review this documentation
3. Check CLAUDE.md for requirements
4. Contact support with relevant log excerpts