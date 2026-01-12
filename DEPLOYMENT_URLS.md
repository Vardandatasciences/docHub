# Deployment URLs Configuration Guide - DocHub

## Current Configuration

- **Server IP**: `13.205.15.232`
- **Domain**: `riskavaire.vardaands.com`
- **Frontend Port**: `8081`
- **Backend Port**: `8002`
- **ECR Repository**: `480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub`

---

## Where to Add Frontend and Backend Deployed URLs

### 1. **Backend API URL** (for Frontend to connect to Backend)

The backend URL is configured in **environment files** that are read during the frontend build process.

#### Location: `.env.production` file (in project root)

Create this file with your deployed backend URL:

```env
# Backend API URL - Choose ONE option based on your setup:

# Option 1: If frontend container can access backend via Docker network (same host)
# Use the container name and internal port
VITE_API_BASE_URL=http://dochub_backend:8000/api

# Option 2: If accessing from browser via IP (current setup)
VITE_API_BASE_URL=http://13.205.15.232:8002/api

# Option 3: If using domain with port
VITE_API_BASE_URL=http://riskavaire.vardaands.com:8002/api

# Option 4: If using subdomain (recommended for production)
VITE_API_BASE_URL=http://api.riskavaire.vardaands.com/api
# OR with HTTPS:
# VITE_API_BASE_URL=https://api.riskavaire.vardaands.com/api

# Environment
VITE_ENV=production
```

**Important Notes:**
- The `.env.production` file must be in the **project root** (same folder as `package.json`)
- This file is read during `npm run build` or Docker build
- The URL must include `/api` at the end (as your backend serves API at `/api`)
- If using Docker network, use container name `dochub_backend` and port `8000` (internal)
- If accessing from browser, use the public IP/domain and port `8002` (host port)

---

### 2. **Frontend URL** (where users access the frontend)

The frontend URL is determined by:
- **Host**: Your server's IP address or domain name
- **Port**: `8081` (as configured in the workflow)

**Current Access URLs:**
- `http://13.205.15.232:8081`
- `http://riskavaire.vardaands.com:8081`

**With Subdomain (if configured):**
- `http://dochub.riskavaire.vardaands.com`
- `https://dochub.riskavaire.vardaands.com` (with SSL)

**Note:** The frontend URL doesn't need to be configured in code - it's just where you access the deployed frontend.

---

### 3. **Backend URL** (where backend is accessible)

The backend is accessible at:
- **Host**: Your server's IP address or domain name  
- **Port**: `8002` (as configured in the workflow)

**Current Access URLs:**
- `http://13.205.15.232:8002/api`
- `http://riskavaire.vardaands.com:8002/api`

**With Subdomain (if configured):**
- `http://api.riskavaire.vardaands.com/api`
- `https://api.riskavaire.vardaands.com/api` (with SSL)

---

## Quick Setup Steps

### Step 1: Create `.env.production` file

In your project root, create `.env.production`:

**For Docker network (recommended if both containers on same host):**
```env
VITE_API_BASE_URL=http://dochub_backend:8000/api
VITE_ENV=production
```

**For public access via IP (current setup):**
```env
VITE_API_BASE_URL=http://13.205.15.232:8002/api
VITE_ENV=production
```

**For domain access:**
```env
VITE_API_BASE_URL=http://riskavaire.vardaands.com:8002/api
VITE_ENV=production
```

**For subdomain (recommended for production):**
```env
VITE_API_BASE_URL=http://api.riskavaire.vardaands.com/api
VITE_ENV=production
```

### Step 2: Build and Deploy

The GitHub Actions workflow will:
1. Read `.env.production` during Docker build
2. Build the frontend with the correct backend URL
3. Deploy both containers

### Step 3: Access Your Application

**Current Setup (Port-based):**
- **Frontend**: `http://13.205.15.232:8081`
- **Backend API**: `http://13.205.15.232:8002/api`

**With Domain:**
- **Frontend**: `http://riskavaire.vardaands.com:8081`
- **Backend API**: `http://riskavaire.vardaands.com:8002/api`

**With Subdomain (Recommended):**
- **Frontend**: `http://dochub.riskavaire.vardaands.com`
- **Backend API**: `http://api.riskavaire.vardaands.com/api`

---

## Domain Setup

Since you already have `riskavaire.vardaands.com` pointing to your server, you have two options:

### Option 1: Use Subdomains (Recommended)
- Frontend: `dochub.riskavaire.vardaands.com`
- Backend: `api.riskavaire.vardaands.com`

See `DOMAIN_SETUP.md` for detailed Nginx configuration.

### Option 2: Use Ports (Current)
- Frontend: `riskavaire.vardaands.com:8081`
- Backend: `riskavaire.vardaands.com:8002/api`

---

## Troubleshooting

### Frontend can't connect to backend?

1. **Check the URL in `.env.production`**
   - If using Docker network: `http://dochub_backend:8000/api`
   - If using public URL: `http://13.205.15.232:8002/api`
   - If using domain: `http://riskavaire.vardaands.com:8002/api`

2. **Verify backend is running:**
   ```bash
   docker ps | grep dochub_backend
   curl http://localhost:8002/api/health
   ```

3. **Check CORS settings** in backend if accessing from browser

4. **Verify network connectivity:**
   ```bash
   # From frontend container
   docker exec dochub_frontend curl http://dochub_backend:8000/api/health
   ```

---

## Important Reminders

1. ✅ Create `.env.production` in project root
2. ✅ Include `/api` at the end of backend URL
3. ✅ Use port `8002` for backend (host port)
4. ✅ Use port `8081` for frontend (host port)
5. ✅ Restart containers after changing `.env.production`
6. ✅ Rebuild Docker image if you change `.env.production`
7. ✅ Update CORS settings in backend if using subdomain/domain

