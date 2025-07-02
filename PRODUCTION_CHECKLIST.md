# WebAI Production Deployment Checklist

## 🚀 Pre-Deployment

### DNS & Infrastructure
- [ ] DNS A records configured for your-domain.com
  ```bash
  dig your-domain.com
  dig www.your-domain.com
  ```
- [ ] Server ports 80, 443 open
- [ ] Sufficient disk space (>10GB free)
- [ ] Sufficient RAM (>2GB available)

### Software Requirements
- [ ] Ubuntu 20.04+ LTS
- [ ] Docker installed
  ```bash
  docker --version  # Should be 20.10+
  ```
- [ ] Docker Compose installed
  ```bash
  docker-compose --version  # Should be 1.27+
  ```

## 🔧 Configuration

### Environment Setup
- [ ] `.env` file created from `.env.sample`
- [ ] Strong `SECRET_KEY` generated
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Strong `ADMIN_PASSWORD` set
- [ ] `DOMAIN_NAME=your-domain.com` configured
- [ ] `LETSENCRYPT_EMAIL` set

### OAuth Authentication
- [ ] Run OAuth setup
  ```bash
  ./setup-oauth.sh  # Choose option 1 for production
  ```
- [ ] Verify configuration exists
  ```bash
  ls -la claude-config/claude_config.json
  ```

## 🔒 Security

### File Permissions
- [ ] Secure sensitive files
  ```bash
  chmod 600 .env
  chmod 700 claude-config/
  ```

### Security Hardening
- [ ] Run security hardening script
  ```bash
  sudo ./harden-security.sh
  ```
- [ ] Review security report
- [ ] Firewall configured (ports 22, 80, 443 only)
- [ ] Fail2ban installed and configured

## 📦 Deployment

### SSL Certificate
- [ ] Obtain SSL certificate
  ```bash
  docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@your-domain.com \
    --agree-tos \
    --no-eff-email \
    -d your-domain.com \
    -d www.your-domain.com
  ```

### Deploy Application
- [ ] Build containers
  ```bash
  docker-compose -f docker-compose.prod.yml build
  ```
- [ ] Start services
  ```bash
  docker-compose -f docker-compose.prod.yml up -d
  ```
- [ ] Verify all containers running
  ```bash
  docker-compose -f docker-compose.prod.yml ps
  ```

## ✅ Post-Deployment Verification

### Service Health
- [ ] Check Nginx
  ```bash
  curl -I https://your-domain.com
  ```
- [ ] Check WebApp
  ```bash
  curl https://your-domain.com/api/health
  ```
- [ ] Check Claude API
  ```bash
  docker-compose -f docker-compose.prod.yml exec webapp curl http://claude-api:8000/health
  ```

### Functionality Tests
- [ ] Access https://your-domain.com
- [ ] Login with admin credentials
- [ ] Send test message
- [ ] Verify response streaming works
- [ ] Check WebSocket connection

### SSL Verification
- [ ] Check certificate validity
  ```bash
  echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
  ```
- [ ] Test SSL configuration
  - Visit: https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com

## 🔄 Monitoring & Maintenance

### Setup Monitoring
- [ ] Start health monitor
  ```bash
  ./monitor.sh --daemon
  ```
- [ ] Install as systemd service
  ```bash
  sudo cp systemd/webai-monitor.service /etc/systemd/system/
  sudo systemctl enable webai-monitor
  sudo systemctl start webai-monitor
  ```

### Configure Backups
- [ ] Test backup script
  ```bash
  ./backup.sh
  ```
- [ ] Setup cron for automated backups
  ```bash
  crontab -e
  # Add: 0 2 * * * /home/ubuntu/webai/backup.sh
  ```

### Log Management
- [ ] Verify log rotation
  ```bash
  ls -la logs/
  ```
- [ ] Check log sizes
  ```bash
  du -sh logs/*
  ```

## 📊 Performance Optimization

### Resource Monitoring
- [ ] Check container resources
  ```bash
  docker stats
  ```
- [ ] Monitor disk usage
  ```bash
  df -h
  ```
- [ ] Check memory usage
  ```bash
  free -h
  ```

### Optimization
- [ ] Adjust worker processes if needed
  ```bash
  # Edit .env
  GUNICORN_WORKERS=4  # Based on CPU cores
  GUNICORN_THREADS=2
  ```

## 🆘 Troubleshooting Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f webapp
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f claude-api
```

### Restart Services
```bash
# Single service
docker-compose -f docker-compose.prod.yml restart webapp

# All services
docker-compose -f docker-compose.prod.yml restart
```

### Emergency Recovery
```bash
# Full restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Restore from backup
./restore.sh /path/to/backup.tar.gz
```

## 📝 Final Checks

- [ ] Document admin credentials securely
- [ ] Save backup of `.env` file
- [ ] Test restore procedure
- [ ] Set up monitoring alerts
- [ ] Schedule regular maintenance window

## 🎉 Launch

Once all items are checked:

1. Announce service availability
2. Monitor closely for first 24 hours
3. Check logs regularly
4. Be ready to scale if needed

---

**Production URL:** https://your-domain.com

**Support Contacts:**
- System Admin: [Your contact]
- Technical Support: [Support contact]

**Documentation:**
- Deployment Guide: `DEPLOYMENT.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- Architecture: `ARCHITECTURE.md`