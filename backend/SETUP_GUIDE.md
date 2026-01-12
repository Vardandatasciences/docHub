# 🚀 DocHub Backend Setup Guide

Complete step-by-step guide to set up and run the DocHub backend API.

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- MySQL Workbench (recommended) or MySQL CLI
- pip (Python package manager)

## 🛠️ Setup Steps

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Create MySQL Database

#### Option A: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Open the `database_schema.sql` file
4. Click "Execute" (⚡ icon) to run all SQL commands
5. Verify tables are created by refreshing the Schemas panel

#### Option B: Using MySQL Command Line

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE dochub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Use the database
USE dochub;

# Execute the schema file
source database_schema.sql;

# Or if you're outside MySQL:
mysql -u root -p dochub < database_schema.sql
```

#### Verify Database Creation

```sql
-- Show all tables
SHOW TABLES;

-- Check users table
SELECT * FROM users;

-- Check categories table
SELECT * FROM categories;
```

You should see:
- ✅ 5 tables created (users, categories, documents, document_views, document_shares)
- ✅ 4 default users inserted
- ✅ 6 default categories inserted

### Step 3: Configure Environment Variables

Create a `.env` file in the backend folder:

```bash
# Copy example (if available)
cp .env.example .env

# Or create manually
touch .env
```

Add the following content to `.env`:

```env
# Flask Environment
FLASK_ENV=development

# Secret Keys (change in production!)
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password-here
MYSQL_DB=dochub

# S3 Configuration
S3_API_BASE_URL=http://15.207.1.40:3000

# Frontend URL
FRONTEND_URL=http://localhost:8080
CORS_ORIGINS=http://localhost:8080,http://localhost:5173,http://localhost:3000

# Server Configuration
PORT=5000
HOST=0.0.0.0
```

**Important:** Replace `your-mysql-password-here` with your actual MySQL password!

### Step 4: Test Database Connection

```bash
python -c "from database import get_db; print('✅ Database connection successful!' if get_db() else '❌ Connection failed')"
```

### Step 5: Run the Application

```bash
python run.py
```

You should see:

```
╔═══════════════════════════════════════════════════╗
║         DocHub API Server Starting...            ║
╠═══════════════════════════════════════════════════╣
║  Environment: development                         ║
║  Host:        0.0.0.0                            ║
║  Port:        5000                               ║
║  URL:         http://0.0.0.0:5000               ║
╚═══════════════════════════════════════════════════╝

✅ Database connection successful
 * Serving Flask app 'app'
 * Debug mode: on
```

### Step 6: Test the API

Open your browser or use curl to test:

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Register a User:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Get Categories (requires token):**
```bash
curl http://localhost:5000/api/categories/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 🔧 Configuration for Frontend

Update your frontend to use the backend API:

### Development Environment

In your frontend `.env` or config file:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### Production Environment

```env
VITE_API_BASE_URL=https://your-production-domain.com/api
```

## 🌐 Switching Between Development and Production

The backend automatically detects the environment based on `FLASK_ENV`:

### Development Mode

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows CMD
$env:FLASK_ENV="development"  # Windows PowerShell

python run.py
```

Features:
- ✅ Debug mode enabled
- ✅ Detailed error messages
- ✅ Auto-reload on code changes
- ✅ CORS enabled for localhost

### Production Mode

```bash
export FLASK_ENV=production   # Linux/Mac
set FLASK_ENV=production      # Windows CMD
$env:FLASK_ENV="production"   # Windows PowerShell

gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

Features:
- ✅ Debug mode disabled
- ✅ Production error handling
- ✅ Secure secret keys required
- ✅ CORS configured for your domain

## 📊 Database Management

### View All Documents
```sql
SELECT d.*, c.name as category, u.name as uploader
FROM documents d
JOIN categories c ON d.category_id = c.id
JOIN users u ON d.uploaded_by = u.id
WHERE d.is_archived = FALSE;
```

### Update Category Document Counts
```sql
UPDATE categories c
SET document_count = (
    SELECT COUNT(*) FROM documents d 
    WHERE d.category_id = c.id AND d.is_archived = FALSE
);
```

### Get Statistics
```sql
SELECT 
    (SELECT COUNT(*) FROM documents WHERE is_archived = FALSE) as total_documents,
    (SELECT COUNT(*) FROM categories WHERE is_active = TRUE) as total_categories,
    (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as total_users,
    (SELECT SUM(file_size) FROM documents WHERE is_archived = FALSE) as total_size;
```

## 🐛 Troubleshooting

### Problem: Database connection failed

**Solution:**
1. Check MySQL is running: `systemctl status mysql` (Linux) or Services (Windows)
2. Verify credentials in `.env`
3. Check database exists: `SHOW DATABASES;`
4. Verify user has permissions: `GRANT ALL PRIVILEGES ON dochub.* TO 'root'@'localhost';`

### Problem: ModuleNotFoundError

**Solution:**
```bash
pip install -r requirements.txt
# Or specific module:
pip install flask-jwt-extended
```

### Problem: Import error for s3.py

**Solution:**
- Ensure `s3.py` is in the `backend` folder
- Check file permissions: `ls -la s3.py`

### Problem: CORS errors from frontend

**Solution:**
- Add your frontend URL to `CORS_ORIGINS` in `.env`:
  ```env
  CORS_ORIGINS=http://localhost:8080,http://localhost:5173
  ```

### Problem: JWT token expired

**Solution:**
- Use the refresh token endpoint: `POST /api/auth/refresh`
- Or login again

## 📝 Next Steps

1. ✅ Test all API endpoints using Postman or curl
2. ✅ Connect frontend to backend
3. ✅ Upload test documents
4. ✅ Configure S3 storage
5. ✅ Set up production environment
6. ✅ Configure domain and SSL

## 🔐 Security Checklist for Production

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY` to strong random values
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Review CORS origins
- [ ] Use strong MySQL password
- [ ] Disable debug mode
- [ ] Set up logging and monitoring

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-JWT-Extended Docs](https://flask-jwt-extended.readthedocs.io/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## 💡 Tips

- Use Postman or Insomnia for API testing
- Check logs if something goes wrong
- Keep your dependencies updated: `pip list --outdated`
- Use virtual environments for isolation
- Read the `README.md` for detailed API documentation

## ✅ Success Indicators

You're all set when:
- ✅ Health check returns `{"status": "healthy"}`
- ✅ Can register and login users
- ✅ Can create categories
- ✅ Can upload documents
- ✅ Frontend connects successfully

Happy coding! 🎉






