# WebAI Troubleshooting Guide

## Common Issues and Solutions

### 1. Docker Not Installed

**Error:** `docker: command not found`

**Solution:**
```bash
sudo ./install-docker.sh
# Log out and log back in, or run:
newgrp docker
```

### 2. Docker Daemon Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. Permission Denied Errors

**Error:** `Permission denied while trying to connect to the Docker daemon socket`

**Solution:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 4. Port Already in Use

**Error:** `bind: address already in use`

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :5000

# Stop the conflicting service or change ports in docker-compose.yml
```

### 5. Container Build Failures

**Error:** Build errors during `docker-compose build`

**Solution:**
```bash
# Clean Docker cache
docker system prune -a
docker-compose build --no-cache
```

### 6. WebSocket Connection Failed

**Symptoms:** Chat messages don't send, "Disconnected" status

**Solution:**
1. Check if all containers are running:
   ```bash
   docker-compose ps
   ```

2. Check nginx logs:
   ```bash
   docker-compose logs nginx
   ```

3. Verify WebSocket upgrade headers in nginx config

### 7. Login Failed

**Error:** "Invalid credentials"

**Solution:**
1. Check `.env` file for correct credentials:
   ```bash
   cat .env | grep ADMIN
   ```

2. Restart the webapp container:
   ```bash
   docker-compose restart webapp
   ```

### 8. Claude API Not Responding

**Symptoms:** No response from AI, errors in chat

**Solution:**
1. Check claude-api container:
   ```bash
   docker-compose logs claude-api
   ```

2. Verify OAuth configuration:
   ```bash
   ls -la claude-config/
   ```

3. Re-run OAuth setup:
   ```bash
   ./setup-oauth.sh
   ```

### 9. SSL Certificate Issues (Production)

**Error:** SSL certificate errors

**Solution:**
```bash
# For Let's Encrypt
docker-compose exec certbot certbot renew --force-renewal

# For self-signed (development)
./setup-dev.sh
```

### 10. Container Crashes

**Symptoms:** Container exits immediately after starting

**Solution:**
1. Check logs for the specific container:
   ```bash
   docker-compose logs [container-name]
   ```

2. Check resource limits:
   ```bash
   docker system df
   df -h
   ```

3. Increase Docker resources if needed

## Debugging Commands

### View All Logs
```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f webapp
docker-compose logs -f claude-api
docker-compose logs -f nginx
```

### Container Shell Access
```bash
# Access webapp container
docker-compose exec webapp /bin/bash

# Access claude-api container
docker-compose exec claude-api /bin/bash
```

### Check Container Status
```bash
# Basic status
docker-compose ps

# Detailed status
docker ps -a

# Container resource usage
docker stats
```

### Network Debugging
```bash
# List networks
docker network ls

# Inspect network
docker network inspect webai_webai-network

# Test connectivity between containers
docker-compose exec webapp ping claude-api
```

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down -v

# Remove all Docker data (WARNING: affects all Docker projects)
docker system prune -a

# Start fresh
./quick-start.sh
```

## Health Checks

### Test Endpoints
```bash
# Nginx health
curl http://localhost/health

# API health
docker-compose exec webapp curl http://claude-api:8000/health

# WebApp health
curl http://localhost/api/health
```

### Performance Issues

If the application is slow:

1. Check container resources:
   ```bash
   docker stats
   ```

2. Check disk space:
   ```bash
   df -h
   ```

3. Restart containers:
   ```bash
   docker-compose restart
   ```

4. Scale workers (production):
   ```bash
   # Edit .env
   GUNICORN_WORKERS=4
   GUNICORN_THREADS=2
   ```

## Getting Help

1. **Check Logs First**
   Always check logs before trying other solutions:
   ```bash
   docker-compose logs -f --tail=50
   ```

2. **Run Diagnostics**
   ```bash
   ./test-setup.sh
   ```

3. **Verify Configuration**
   - Check `.env` file
   - Verify OAuth setup
   - Confirm all directories exist

4. **Clean Start**
   If all else fails:
   ```bash
   docker-compose down -v
   rm -rf claude-config/
   ./quick-start.sh
   ```