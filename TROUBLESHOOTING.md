# Troubleshooting Guide - DocHub Deployment

## Frontend Not Opening (http://13.205.15.232:8081/)

### Step 1: Check if Container is Running

```bash
# Check if container exists and is running
docker ps -a | grep dochub_frontend

# Check container logs
docker logs dochub_frontend

# Check if port is listening
netstat -tuln | grep 8081
# OR
ss -tuln | grep 8081
```

### Step 2: Check Container Status

```bash
# If container is not running, check why
docker inspect dochub_frontend

# Check container exit code
docker ps -a | grep dochub_frontend
```

### Step 3: Verify Image was Built Correctly

```bash
# Check if image exists
docker images | grep dochub_frontend

# Check image details
docker inspect dochub_frontend:latest
```

### Step 4: Check Firewall/Security Groups

```bash
# Check if port 8081 is open
sudo ufw status
# OR
sudo iptables -L -n | grep 8081

# If using AWS, check Security Group:
# - Inbound rule for port 8081 (TCP) from 0.0.0.0/0
```

### Step 5: Test Container Locally

```bash
# Stop existing container
docker stop dochub_frontend || true
docker rm dochub_frontend || true

# Run container manually to see errors
docker run -d \
  --name dochub_frontend_test \
  -p 8081:80 \
  dochub_frontend:latest

# Check logs immediately
docker logs -f dochub_frontend_test
```

### Step 6: Rebuild if Needed

```bash
# Pull latest code
git pull

# Rebuild image
docker build --no-cache -t dochub_frontend:latest .

# Remove old container
docker stop dochub_frontend || true
docker rm dochub_frontend || true

# Run new container
docker run -d \
  --name dochub_frontend \
  -p 8081:80 \
  --restart unless-stopped \
  dochub_frontend:latest
```

---

## Common Issues and Solutions

### Issue 1: Container Exits Immediately

**Symptoms:** Container shows as "Exited" in `docker ps -a`

**Solution:**
```bash
# Check logs for errors
docker logs dochub_frontend

# Common causes:
# 1. Nginx config error - check nginx.conf syntax
# 2. Missing files in /usr/share/nginx/html
# 3. Port conflict
```

### Issue 2: Port Already in Use

**Symptoms:** Error: "bind: address already in use"

**Solution:**
```bash
# Find what's using port 8081
sudo lsof -i :8081
# OR
sudo netstat -tulpn | grep 8081

# Kill the process or use different port
```

### Issue 3: 404 Not Found

**Symptoms:** Can access but get 404 errors

**Solution:**
- Check if `dist` folder was created during build
- Verify nginx.conf is correct (SPA routing)
- Check if index.html exists in container:
  ```bash
  docker exec dochub_frontend ls -la /usr/share/nginx/html
  ```

### Issue 4: Blank Page / White Screen

**Symptoms:** Page loads but shows blank

**Solution:**
```bash
# Check browser console for errors
# Check if backend URL is correct in .env.production
# Verify build completed successfully:
docker exec dochub_frontend ls -la /usr/share/nginx/html
```

### Issue 5: Cannot Connect to Backend

**Symptoms:** Frontend loads but API calls fail

**Solution:**
1. Check `.env.production` has correct backend URL:
   ```env
   VITE_API_BASE_URL=http://13.205.15.232:8002/api
   ```

2. Rebuild frontend with correct URL:
   ```bash
   docker build --build-arg VITE_API_BASE_URL=http://13.205.15.232:8002/api -t dochub_frontend:latest .
   ```

3. Verify backend is running:
   ```bash
   curl http://13.205.15.232:8002/api/health
   ```

---

## Quick Diagnostic Commands

```bash
# 1. Check all containers
docker ps -a

# 2. Check container logs
docker logs dochub_frontend --tail 50
docker logs dochub_backend --tail 50

# 3. Check if ports are listening
sudo netstat -tulpn | grep -E '8081|8002'

# 4. Test from inside container
docker exec dochub_frontend curl http://localhost:80
docker exec dochub_backend curl http://localhost:8000

# 5. Check disk space
df -h

# 6. Check Docker system
docker system df
docker system prune -a  # Clean up if needed
```

---

## Manual Deployment Steps

If automated deployment fails, deploy manually:

### Backend:
```bash
cd backend
docker build -t dochub_backend:latest .
docker run -d \
  --name dochub_backend \
  -p 8002:8000 \
  --env-file /home/ubuntu/dochub.env \
  -v /home/ubuntu/MEDIA_ROOT:/app/MEDIA_ROOT \
  -v /home/ubuntu/TEMP_MEDIA_ROOT:/app/TEMP_MEDIA_ROOT \
  -v /home/ubuntu/Reports:/app/Reports \
  --restart unless-stopped \
  dochub_backend:latest
```

### Frontend:
```bash
# Ensure .env.production exists with correct backend URL
docker build -t dochub_frontend:latest .
docker run -d \
  --name dochub_frontend \
  -p 8081:80 \
  --restart unless-stopped \
  dochub_frontend:latest
```

---

## Verify Deployment

```bash
# Test frontend
curl http://localhost:8081
curl http://13.205.15.232:8081

# Test backend
curl http://localhost:8002/api/health
curl http://13.205.15.232:8002/api/health

# Check from browser
# Frontend: http://13.205.15.232:8081
# Backend API: http://13.205.15.232:8002/api/health
```

---

## Still Not Working?

1. **Check GitHub Actions logs** - See if build/deploy step failed
2. **Check server resources** - CPU, memory, disk space
3. **Check network connectivity** - Can you SSH to server?
4. **Check Docker daemon** - `sudo systemctl status docker`
5. **Review all logs** - `docker logs dochub_frontend` and `docker logs dochub_backend`

