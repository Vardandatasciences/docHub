# ⚡ Quick Environment Setup

## Create Environment Files

### Option 1: Manual Creation

Create these files in your project root:

**`.env.development`:**
```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENV=development
```

**`.env.production`:**
```env
VITE_API_BASE_URL=https://your-production-domain.com/api
VITE_ENV=production
```

### Option 2: Command Line (Windows PowerShell)

```powershell
# Development
@"
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENV=development
"@ | Out-File -FilePath .env.development -Encoding utf8

# Production
@"
VITE_API_BASE_URL=https://your-production-domain.com/api
VITE_ENV=production
"@ | Out-File -FilePath .env.production -Encoding utf8
```

### Option 3: Command Line (Git Bash/Linux/Mac)

```bash
# Development
cat > .env.development << EOL
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENV=development
EOL

# Production
cat > .env.production << EOL
VITE_API_BASE_URL=https://your-production-domain.com/api
VITE_ENV=production
EOL
```

---

## Run the Application

### 1. Start Backend

```bash
cd backend
python run.py
```

Backend at: `http://localhost:5000`

### 2. Start Frontend

```bash
# In project root
npm run dev
```

Frontend at: `http://localhost:8082`

---

## Test Integration

1. Open: `http://localhost:8082`
2. Click "Sign up"
3. Create account
4. Upload document
5. Success! 🎉

---

## Change Backend URL

Edit `.env.development`:

```env
# Local
VITE_API_BASE_URL=http://localhost:5000/api

# Network
VITE_API_BASE_URL=http://192.168.1.100:5000/api

# Remote
VITE_API_BASE_URL=https://api.yourdomain.com/api
```

**Important:** Restart frontend after changing env files!

---

## Troubleshooting

**CORS Error?**
- Check backend is running
- Check CORS_ORIGINS in `backend/config.py`

**Connection Refused?**
- Check backend URL in `.env.development`
- Check backend is running on correct port

**401 Unauthorized?**
- Login again
- Clear localStorage and retry

---

**That's it! You're ready to go! 🚀**






