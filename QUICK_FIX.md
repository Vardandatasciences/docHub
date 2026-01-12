# Quick Fix - Frontend Not Opening

## Immediate Steps to Fix

### 1. Check if Container is Running

SSH to your server and run:
```bash
docker ps -a | grep dochub_frontend
```

**If container is NOT running:**
```bash
# Check logs to see why it stopped
docker logs dochub_frontend

# Restart it
docker start dochub_frontend
```

### 2. Create .env.production File

On your server, in the project root, create `.env.production`:
```bash
cd /path/to/your/project
cat > .env.production << EOF
VITE_API_BASE_URL=http://13.205.15.232:8002/api
VITE_ENV=production
EOF
```

### 3. Rebuild and Redeploy Frontend

```bash
# Pull latest code (if using git)
git pull

# Rebuild image
docker build --no-cache -t dochub_frontend:latest .

# Stop and remove old container
docker stop dochub_frontend || true
docker rm dochub_frontend || true

# Run new container
docker run -d \
  --name dochub_frontend \
  -p 8081:80 \
  --restart unless-stopped \
  dochub_frontend:latest

# Check if it's running
docker ps | grep dochub_frontend

# Check logs
docker logs dochub_frontend
```

### 4. Verify Port is Open

```bash
# Check if port 8081 is listening
sudo netstat -tuln | grep 8081

# Test locally
curl http://localhost:8081

# If using AWS, check Security Group:
# - Add inbound rule: Port 8081, TCP, Source: 0.0.0.0/0
```

### 5. Test from Browser

Open: `http://13.205.15.232:8081`

If still not working, check:
- Browser console (F12) for errors
- Network tab for failed requests
- Server firewall/security groups

---

## Common Quick Fixes

### Fix 1: Container Not Running
```bash
docker start dochub_frontend
docker logs dochub_frontend
```

### Fix 2: Wrong Backend URL
```bash
# Update .env.production
echo "VITE_API_BASE_URL=http://13.205.15.232:8002/api" > .env.production
echo "VITE_ENV=production" >> .env.production

# Rebuild
docker build --no-cache -t dochub_frontend:latest .
docker stop dochub_frontend && docker rm dochub_frontend
docker run -d --name dochub_frontend -p 8081:80 --restart unless-stopped dochub_frontend:latest
```

### Fix 3: Port Conflict
```bash
# Find what's using port 8081
sudo lsof -i :8081
# Kill it or use different port
```

### Fix 4: Missing Files
```bash
# Check if dist folder exists in image
docker run --rm dochub_frontend:latest ls -la /usr/share/nginx/html
```

---

## One-Command Rebuild

```bash
docker build --no-cache -t dochub_frontend:latest . && \
docker stop dochub_frontend 2>/dev/null; \
docker rm dochub_frontend 2>/dev/null; \
docker run -d --name dochub_frontend -p 8081:80 --restart unless-stopped dochub_frontend:latest && \
docker logs dochub_frontend
```

