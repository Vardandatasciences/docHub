# ⚡ Quick Start Guide - DocHub Backend

Get up and running in 5 minutes!

## 📦 Installation

```bash
# 1. Navigate to backend folder
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your settings
cat > .env << EOL
FLASK_ENV=development
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=jwt-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
MYSQL_DB=dochub
S3_API_BASE_URL=http://15.207.1.40:3000
FRONTEND_URL=http://localhost:8080
PORT=5000
EOL
```

## 🗄️ Database Setup

```bash
# Create database and tables
mysql -u root -p < database_schema.sql

# Or manually in MySQL:
# 1. Open MySQL Workbench
# 2. Open database_schema.sql
# 3. Execute all SQL commands
```

## 🚀 Run Server

```bash
python run.py
```

Server starts at: **http://localhost:5000**

## ✅ Test API

```bash
# Health check
curl http://localhost:5000/api/health

# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","password":"password123"}'

# Get categories (use token from register response)
curl http://localhost:5000/api/categories/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 Project Structure

```
backend/
├── app.py              # Main Flask app
├── config.py           # Configuration (dev/prod)
├── database.py         # Database utilities
├── run.py              # Start server
├── s3.py               # S3 operations
├── requirements.txt    # Dependencies
├── database_schema.sql # Database schema
├── routes/             # API endpoints
│   ├── auth.py        # Authentication
│   ├── documents.py   # Document management
│   ├── categories.py  # Categories
│   ├── users.py       # User management
│   └── stats.py       # Statistics
└── utils/              # Helper functions
    ├── s3_helper.py   # S3 wrapper
    ├── auth_helper.py # Auth utilities
    └── validators.py  # Input validation
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/register` | POST | Register user |
| `/api/auth/login` | POST | Login |
| `/api/documents/` | GET | List documents |
| `/api/documents/upload` | POST | Upload file |
| `/api/categories/` | GET | List categories |
| `/api/categories/` | POST | Create category |
| `/api/stats/` | GET | Get statistics |

## 🔄 Environment Switching

### Development
```bash
export FLASK_ENV=development
python run.py
```

### Production
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 🛠️ Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python run.py

# Check database connection
python -c "from database import get_db; get_db()"

# Update dependencies
pip freeze > requirements.txt
```

## 📖 Documentation

- **Setup Guide:** `SETUP_GUIDE.md` - Detailed setup instructions
- **API Docs:** `API_DOCUMENTATION.md` - Complete API reference
- **README:** `README.md` - Project overview

## 🔥 Default Users

After running database_schema.sql:

| Email | Password | Role |
|-------|----------|------|
| admin@dochub.com | admin123 | admin |
| john@dochub.com | - | user |
| sarah@dochub.com | - | user |

## 🎯 Next Steps

1. ✅ Start backend: `python run.py`
2. ✅ Test API endpoints
3. ✅ Connect frontend
4. ✅ Upload documents
5. ✅ Deploy to production

## 💡 Pro Tips

- Use Postman/Insomnia for API testing
- Check logs if errors occur
- Keep `.env` file secret
- Use virtual environment: `python -m venv venv`
- Read full documentation for advanced features

## 🐛 Troubleshooting

**Can't connect to database?**
```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
# or check Services app on Windows
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Port already in use?**
```bash
# Change port in .env
PORT=5001
```

## 📧 Support

Check documentation or create an issue for help!

---

**That's it! You're ready to go! 🚀**






