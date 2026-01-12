# Port Mapping Explanation

## How Docker Port Mapping Works

### Frontend Container:
- **Inside Container**: Nginx listens on port `80` (standard HTTP port)
- **On Host Server**: Exposed as port `8081`
- **Port Mapping**: `-p 8081:80` means "map host port 8081 to container port 80"

**So:**
- `nginx.conf` listens on port `80` ✅ (INSIDE the container)
- You access it via `http://13.205.15.232:8081` ✅ (from OUTSIDE/HOST)

### Backend Container:
- **Inside Container**: Flask/Gunicorn listens on port `8000`
- **On Host Server**: Exposed as port `8002`
- **Port Mapping**: `-p 8002:8000` means "map host port 8002 to container port 8000"

**So:**
- Backend listens on port `8000` ✅ (INSIDE the container)
- You access it via `http://13.205.15.232:8002/api` ✅ (from OUTSIDE/HOST)

---

## Visual Diagram

```
┌─────────────────────────────────────────────────┐
│  HOST SERVER (13.205.15.232)                    │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Frontend Container                      │  │
│  │  nginx.conf → listens on port 80         │  │
│  │  └─ Mapped to host port 8081            │  │
│  └──────────────────────────────────────────┘  │
│           ↕ Port Mapping: 8081:80                │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Backend Container                       │  │
│  │  Flask/Gunicorn → listens on port 8000   │  │
│  │  └─ Mapped to host port 8002            │  │
│  └──────────────────────────────────────────┘  │
│           ↕ Port Mapping: 8002:8000              │
└─────────────────────────────────────────────────┘
```

---

## Why This Setup?

1. **Standard Ports Inside Containers**: 
   - Nginx standard port is 80
   - Flask standard port is 8000
   - This is best practice

2. **Custom Ports on Host**:
   - Port 8081 for frontend (to avoid conflicts)
   - Port 8002 for backend (to avoid conflicts)
   - You can use any available ports on the host

3. **Port Mapping Syntax**: `-p HOST_PORT:CONTAINER_PORT`
   - `-p 8081:80` = Host port 8081 → Container port 80
   - `-p 8002:8000` = Host port 8002 → Container port 8000

---

## Current Configuration

### Frontend:
- **nginx.conf**: Listens on port `80` (inside container) ✅
- **Docker run**: `-p 8081:80` (maps to host port 8081) ✅
- **Access URL**: `http://13.205.15.232:8081` ✅

### Backend:
- **Flask/Gunicorn**: Listens on port `8000` (inside container) ✅
- **Docker run**: `-p 8002:8000` (maps to host port 8002) ✅
- **Access URL**: `http://13.205.15.232:8002/api` ✅

---

## Summary

✅ **nginx.conf is CORRECT** - it should listen on port 80 (inside container)
✅ **Port mapping is CORRECT** - `-p 8081:80` maps it to host port 8081
✅ **No changes needed** - This is the standard Docker setup

The confusion is understandable - just remember:
- **Inside container** = Standard ports (80, 8000)
- **Outside/Host** = Your custom ports (8081, 8002)

