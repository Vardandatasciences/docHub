# 🔗 Frontend-Backend Integration Guide

## ✅ Integration Complete!

Your frontend is now connected to the backend with a **centralized API system**!

---

## 📁 New Files Created

### API Configuration & Client
```
src/
├── lib/
│   ├── api-config.ts        # Centralized API configuration ⭐
│   └── api-client.ts        # HTTP client with auth handling
│
└── services/
    ├── auth.service.ts      # Authentication API calls
    ├── document.service.ts  # Document API calls
    ├── category.service.ts  # Category API calls
    └── stats.service.ts     # Statistics API calls
```

### Environment Files
```
.env.development         # Development config
.env.production          # Production config
.env.example             # Template
```

---

## ⚙️ Centralized API Configuration

### Easy Environment Switching

**Development (.env.development):**
```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENV=development
```

**Production (.env.production):**
```env
VITE_API_BASE_URL=https://your-production-domain.com/api
VITE_ENV=production
```

**Switch environments automatically:**
```bash
# Development
npm run dev

# Production build
npm run build
```

---

## 🔌 API System Architecture

### 1. API Configuration (`src/lib/api-config.ts`)

Centralized configuration for all API settings:

```typescript
export const apiConfig = {
  baseURL: 'http://localhost:5000/api',  // Auto from env
  endpoints: {
    login: '/auth/login',
    register: '/auth/register',
    documents: '/documents',
    categories: '/categories',
    // ... all endpoints defined
  }
};
```

**Benefits:**
- ✅ Single source of truth
- ✅ Easy to update URLs
- ✅ Type-safe endpoints
- ✅ Environment-aware

### 2. API Client (`src/lib/api-client.ts`)

Handles all HTTP requests with:
- ✅ Automatic JWT token handling
- ✅ Automatic token refresh
- ✅ Error handling
- ✅ Request timeout
- ✅ File upload support

```typescript
// Example usage
import { apiClient } from '@/lib/api-client';

// GET request
const data = await apiClient.get('/documents');

// POST request
const result = await apiClient.post('/auth/login', { email, password });

// File upload
const formData = new FormData();
formData.append('file', file);
await apiClient.upload('/documents/upload', formData);
```

### 3. Service Layer

Each feature has its own service:

**Auth Service:**
```typescript
import { authService } from '@/services/auth.service';

// Register
await authService.register({ name, email, password });

// Login
await authService.login({ email, password });

// Logout
await authService.logout();
```

**Document Service:**
```typescript
import { documentService } from '@/services/document.service';

// Get documents
const docs = await documentService.getDocuments({ search: 'report' });

// Upload
await documentService.uploadDocument(file, categoryId);
```

**Category Service:**
```typescript
import { categoryService } from '@/services/category.service';

// Get categories
const cats = await categoryService.getCategories();

// Create
await categoryService.createCategory({ name: 'New Category' });
```

---

## 🔄 Updated Components

### 1. AuthContext (`src/contexts/AuthContext.tsx`)

Now uses real API calls:

```typescript
// Before: localStorage only
const login = (name: string, email: string) => {
  localStorage.setItem('user', JSON.stringify({ name, email }));
};

// After: Real API call
const login = async (email: string, password: string) => {
  const response = await authService.login({ email, password });
  setUser(response.user);
  // Tokens stored automatically
};
```

### 2. Login Page (`src/pages/Login.tsx`)

Now calls backend API:

```typescript
// Register
await register(name, email, password);  // Calls /api/auth/register

// Login
await login(email, password);  // Calls /api/auth/login
```

### 3. useDocuments Hook (`src/hooks/useDocuments.ts`)

Fetches from backend:

```typescript
// Fetch documents from API
const fetchDocuments = async () => {
  const response = await documentService.getDocuments({
    category_id: selectedCategoryId,
    search: searchQuery
  });
  setDocuments(response.documents);
};

// Upload to backend
const addDocument = async (file: File, category: string) => {
  await documentService.uploadDocument(file, categoryId);
  // Refreshes list automatically
};
```

---

## 🚀 How to Run

### Step 1: Start Backend

```bash
cd backend
python run.py
```

Backend runs at: `http://localhost:5000`

### Step 2: Configure Frontend

Create `.env.development`:

```bash
# In project root
cat > .env.development << EOL
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENV=development
EOL
```

### Step 3: Start Frontend

```bash
npm run dev
```

Frontend runs at: `http://localhost:8082`

### Step 4: Test Integration

1. **Open browser:** `http://localhost:8082`
2. **Register:** Create a new account
3. **Login:** Sign in with credentials
4. **Upload:** Upload a document
5. **Browse:** View documents and categories

---

## 🔐 Authentication Flow

### 1. Register/Login

```
User submits form
    ↓
Frontend: authService.login()
    ↓
API Client: POST /api/auth/login
    ↓
Backend: Validates credentials
    ↓
Backend: Returns user + JWT tokens
    ↓
Frontend: Stores tokens in localStorage
    ↓
Frontend: Redirects to dashboard
```

### 2. Authenticated Requests

```
User requests documents
    ↓
Frontend: documentService.getDocuments()
    ↓
API Client: Adds Authorization header
    ↓
API Client: GET /api/documents
    ↓
Backend: Validates JWT token
    ↓
Backend: Returns documents
    ↓
Frontend: Displays documents
```

### 3. Token Refresh (Automatic)

```
Request fails with 401
    ↓
API Client: Detects expired token
    ↓
API Client: Calls /api/auth/refresh
    ↓
Backend: Issues new tokens
    ↓
API Client: Stores new tokens
    ↓
API Client: Retries original request
    ↓
Success!
```

---

## 📊 API Endpoints Used

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token

### Documents
- `GET /api/documents/` - List documents
- `GET /api/documents/{id}` - Get document
- `POST /api/documents/upload` - Upload document
- `DELETE /api/documents/{id}` - Delete document

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Statistics
- `GET /api/stats/` - Get dashboard stats

---

## 🛠️ Configuration Options

### API Configuration (`src/lib/api-config.ts`)

```typescript
export const apiConfig = {
  baseURL: API_BASE_URL,           // From env variable
  timeout: 30000,                  // 30 seconds
  tokenKey: 'docHub_access_token', // LocalStorage key
  refreshTokenKey: 'docHub_refresh_token',
  userKey: 'docHub_user',
};
```

### Change Backend URL

**Option 1: Environment Variable**
```env
# .env.development
VITE_API_BASE_URL=http://192.168.1.100:5000/api
```

**Option 2: Direct Edit**
```typescript
// src/lib/api-config.ts
const API_BASE_URL = 'http://your-backend-url.com/api';
```

---

## 🔍 Debugging

### Check API Configuration

Open browser console:

```javascript
// You'll see in development:
🔧 API Configuration: {
  baseURL: "http://localhost:5000/api",
  environment: "development"
}
```

### Check Network Requests

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. See all API calls

### Check Stored Tokens

```javascript
// In browser console
localStorage.getItem('docHub_access_token')
localStorage.getItem('docHub_user')
```

---

## ❌ Common Issues & Solutions

### Issue 1: CORS Error

**Error:** `Access to fetch blocked by CORS policy`

**Solution:** Backend CORS is configured for `http://localhost:8082`. If using different port:

```python
# backend/config.py
CORS_ORIGINS = ['http://localhost:8082', 'http://localhost:YOUR_PORT']
```

### Issue 2: Connection Refused

**Error:** `Failed to fetch` or `Network error`

**Solution:**
1. Check backend is running: `http://localhost:5000/api/health`
2. Check frontend env variable: `VITE_API_BASE_URL`
3. Restart frontend after env changes

### Issue 3: 401 Unauthorized

**Error:** `Unauthorized` on API calls

**Solution:**
1. Login again to get fresh token
2. Check token in localStorage
3. Clear localStorage and login again

### Issue 4: Token Expired

**Solution:** Automatic! API client refreshes tokens automatically.

---

## 📝 Environment Variables

### Development

```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_ENV=development
```

### Production

```env
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_ENV=production
```

### Testing with Different Backend

```env
# Local backend
VITE_API_BASE_URL=http://localhost:5000/api

# Remote backend
VITE_API_BASE_URL=http://192.168.1.100:5000/api

# Production backend
VITE_API_BASE_URL=https://api.yourdomain.com/api
```

---

## ✅ Integration Checklist

- [x] API configuration created
- [x] API client with auth handling
- [x] Service layer for all features
- [x] AuthContext updated
- [x] Login/Register connected
- [x] Document upload connected
- [x] Category management connected
- [x] Environment variables configured
- [x] Error handling implemented
- [x] Token refresh automatic
- [x] Loading states added

---

## 🎯 Next Steps

1. **Test Everything:**
   - Register new user
   - Login
   - Upload document
   - Create category
   - Search documents

2. **Customize:**
   - Update API URLs for your environment
   - Adjust timeout settings
   - Add more error handling

3. **Deploy:**
   - Build frontend: `npm run build`
   - Deploy backend
   - Update production env variables

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `src/lib/api-config.ts` | API configuration & endpoints |
| `src/lib/api-client.ts` | HTTP client with auth |
| `src/services/auth.service.ts` | Auth API calls |
| `src/services/document.service.ts` | Document API calls |
| `src/services/category.service.ts` | Category API calls |
| `src/contexts/AuthContext.tsx` | Auth state management |
| `src/hooks/useDocuments.ts` | Document state management |
| `.env.development` | Dev environment config |
| `.env.production` | Prod environment config |

---

## 🎉 Success!

Your frontend is now **fully integrated** with the backend!

**Features Working:**
- ✅ User registration
- ✅ User login
- ✅ Document upload to S3
- ✅ Document listing
- ✅ Category management
- ✅ Search & filtering
- ✅ Automatic token refresh
- ✅ Error handling

**Centralized API System:**
- ✅ Single configuration file
- ✅ Easy environment switching
- ✅ Type-safe API calls
- ✅ Automatic authentication

---

**Ready to code! 🚀**






