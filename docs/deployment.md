# Deployment Guide

## Overview

This guide covers deploying the Project Manager AI Assistant from local development to production.

## Local Development

### Quick Start

1. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/project-manager-assistant.git
   cd project-manager-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

5. **Start services**
   ```bash
   # Terminal 1: Backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Frontend
   streamlit run streamlit_app/app.py --server.port 8501
   ```

6. **Access application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## Docker Deployment

### Single Container

1. **Build image**
   ```bash
   docker build -t project-manager-ai .
   ```

2. **Run container**
   ```bash
   docker run -p 8000:8000 -p 8501:8501 \
     -e OPENAI_API_KEY=your-api-key \
     project-manager-ai
   ```

### Docker Compose

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
         - "8501:8501"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - REDIS_URL=redis://redis:6379
       depends_on:
         - redis
     
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
   ```

2. **Deploy**
   ```bash
   docker-compose up -d
   ```

## Production Deployment

### Environment Variables

Create production `.env`:

```bash
OPENAI_API_KEY=your-production-api-key
API_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

### Web Server (Nginx)

1. **Install Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
       }
   }
   ```

3. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/project-manager /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Process Management (Systemd)

1. **Create service file**
   ```bash
   sudo nano /etc/systemd/system/project-manager.service
   ```

2. **Service configuration**
   ```ini
   [Unit]
   Description=Project Manager AI Assistant
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/project-manager-assistant
   Environment=PATH=/path/to/venv/bin
   ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**
   ```bash
   sudo systemctl enable project-manager
   sudo systemctl start project-manager
   sudo systemctl status project-manager
   ```

### SSL Certificate (Let's Encrypt)

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

## Cloud Deployment

### AWS (EC2)

1. **Launch EC2 instance**
   - Ubuntu 20.04 LTS
   - t3.medium or larger
   - Security group with ports 22, 80, 443

2. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx redis-server
   ```

3. **Deploy application**
   ```bash
   git clone https://github.com/your-username/project-manager-assistant.git
   cd project-manager-assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure and start services**
   - Follow Nginx and Systemd setup above
   - Configure environment variables
   - Start services

### Heroku

1. **Create Procfile**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-api-key
   git push heroku main
   ```

## Monitoring and Logging

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check service status
sudo systemctl status project-manager
```

### Log Management

```bash
# View application logs
sudo journalctl -u project-manager -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
```

## Security Considerations

### Firewall Configuration

```bash
# UFW firewall setup
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Environment Security

```bash
# Secure environment variables
chmod 600 .env
chown www-data:www-data .env
```

## Troubleshooting

### Common Issues

**Service won't start**
```bash
# Check logs
sudo journalctl -u project-manager -f

# Check configuration
sudo nginx -t
```

**High memory usage**
```bash
# Monitor memory
htop
free -h

# Check Redis memory
redis-cli info memory
```

**API errors**
```bash
# Check API logs
tail -f /var/log/project-manager/api.log

# Test API endpoint
curl -X GET http://localhost:8000/health
```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump project_manager > backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump project_manager > backup_$DATE.sql
gzip backup_$DATE.sql
```

### Application Backup

```bash
# Backup application files
tar -czf app_backup_$(date +%Y%m%d).tar.gz /path/to/app

# Backup configuration
cp .env .env.backup
```

## Maintenance

### Regular Tasks

1. **Security updates**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. **Log cleanup**
   ```bash
   sudo logrotate -f /etc/logrotate.d/project-manager
   ```

3. **Backup verification**
   ```bash
   # Test backup restoration
   psql -d test_db -f backup.sql
   ```

### Update Procedures

1. **Zero-downtime deployment**
   ```bash
   # Blue-green deployment
   # Deploy to new instance
   # Switch traffic
   # Decommission old instance
   ```

2. **Rollback plan**
   ```bash
   # Keep previous version ready
   # Database migration rollback
   # Configuration rollback
   ```

---

*For more detailed information about specific deployment scenarios, refer to the cloud provider documentation.* 