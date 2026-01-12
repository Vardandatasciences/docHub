# Domain Setup Guide for DocHub

## Current Setup

- **Server IP**: `13.205.15.232`
- **Domain**: `riskavaire.vardaands.com`
- **Existing App**: Port 8080 redirects to domain
- **DocHub Frontend**: Port 8081
- **DocHub Backend**: Port 8002

## Domain Configuration Options

### Option 1: Subdomain (Recommended)
Set up a subdomain for DocHub:
- **Frontend**: `dochub.riskavaire.vardaands.com` or `app.riskavaire.vardaands.com`
- **Backend API**: `api.riskavaire.vardaands.com` or `dochub-api.riskavaire.vardaands.com`

**Nginx Configuration Example:**
```nginx
# Frontend subdomain
server {
    listen 80;
    server_name dochub.riskavaire.vardaands.com;
    
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Backend API subdomain
server {
    listen 80;
    server_name api.riskavaire.vardaands.com;
    
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: Path-based Routing
Use the same domain with different paths:
- **Frontend**: `riskavaire.vardaands.com/dochub`
- **Backend API**: `riskavaire.vardaands.com/dochub-api`

**Nginx Configuration Example:**
```nginx
server {
    listen 80;
    server_name riskavaire.vardaands.com;
    
    # Existing app (port 8080)
    location / {
        proxy_pass http://127.0.0.1:8080;
        # ... existing config
    }
    
    # DocHub Frontend
    location /dochub {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # DocHub Backend API
    location /dochub-api {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 3: Port-based Access (Current)
Access directly via ports (no domain setup needed):
- **Frontend**: `http://13.205.15.232:8081` or `http://riskavaire.vardaands.com:8081`
- **Backend**: `http://13.205.15.232:8002/api` or `http://riskavaire.vardaands.com:8002/api`

## Recommended Setup

**For production, use Option 1 (Subdomain):**

1. **DNS Configuration**: Add A records:
   - `dochub.riskavaire.vardaands.com` → `13.205.15.232`
   - `api.riskavaire.vardaands.com` → `13.205.15.232`

2. **Nginx Configuration**: Set up reverse proxy as shown above

3. **Frontend Environment**: Update `.env.production`:
   ```env
   VITE_API_BASE_URL=http://api.riskavaire.vardaands.com/api
   VITE_ENV=production
   ```

4. **SSL/HTTPS**: Set up Let's Encrypt certificates for HTTPS:
   ```bash
   sudo certbot --nginx -d dochub.riskavaire.vardaands.com -d api.riskavaire.vardaands.com
   ```

## Access URLs

### Current Setup (Port-based):
- Frontend: `http://13.205.15.232:8081`
- Backend: `http://13.205.15.232:8002/api`

### With Subdomain (Recommended):
- Frontend: `http://dochub.riskavaire.vardaands.com`
- Backend: `http://api.riskavaire.vardaands.com/api`

### With HTTPS:
- Frontend: `https://dochub.riskavaire.vardaands.com`
- Backend: `https://api.riskavaire.vardaands.com/api`

## Important Notes

1. **CORS Configuration**: If using subdomains, update backend CORS settings to allow:
   - `http://dochub.riskavaire.vardaands.com`
   - `https://dochub.riskavaire.vardaands.com`

2. **Environment Variables**: The frontend needs to know the backend URL at build time (in `.env.production`)

3. **Firewall**: Ensure ports 8081 and 8002 are open if accessing directly via ports

4. **Multiple Apps**: Since you have other applications, subdomain approach is cleaner and avoids port conflicts

