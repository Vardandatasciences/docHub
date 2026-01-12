# DocHub Backend API

Flask-based REST API for document management system with S3 storage integration.

## Features

- 🔐 JWT-based authentication
- 📄 Document upload/download with S3 integration
- 🏷️ Category management
- 📊 Statistics and analytics
- 🔍 Full-text search
- 👥 User management
- 🔄 Automatic PDF/Excel processing
- 🌍 CORS support for frontend integration

## Tech Stack

- **Framework:** Flask 3.0
- **Database:** MySQL
- **Storage:** S3 (via custom RenderS3Client)
- **Authentication:** JWT (Flask-JWT-Extended)
- **PDF Processing:** PyPDF2, pdfplumber
- **Excel Processing:** openpyxl, pandas

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=dochub
S3_API_BASE_URL=http://15.207.1.40:3000
```

### 3. Create Database

Run the SQL commands in MySQL Workbench or command line:

```bash
mysql -u root -p < database_schema.sql
```

Or manually in MySQL Workbench:
1. Open `database_schema.sql`
2. Execute all SQL commands
3. Verify tables are created

### 4. Run the Application

**Development:**
```bash
python run.py
```

**Production (with Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

The API will be available at: `http://localhost:5000`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | Logout user |
| POST | `/api/auth/refresh` | Refresh access token |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents/` | List documents |
| GET | `/api/documents/<id>` | Get document details |
| POST | `/api/documents/upload` | Upload document |
| DELETE | `/api/documents/<id>` | Delete document |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List categories |
| GET | `/api/categories/<id>` | Get category details |
| POST | `/api/categories/` | Create category |
| PUT | `/api/categories/<id>` | Update category |
| DELETE | `/api/categories/<id>` | Delete category |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List users |
| PUT | `/api/users/profile` | Update profile |

### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/` | Get dashboard stats |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check API health |

## Project Structure

```
backend/
├── app.py                 # Flask application factory
├── config.py             # Configuration management
├── database.py           # Database utilities
├── run.py                # Application entry point
├── s3.py                 # S3 client (existing)
├── requirements.txt      # Python dependencies
├── database_schema.sql   # MySQL database schema
├── .env.example          # Environment template
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── documents.py     # Document management routes
│   ├── categories.py    # Category management routes
│   ├── users.py         # User management routes
│   └── stats.py         # Statistics routes
└── utils/
    ├── s3_helper.py     # S3 integration wrapper
    ├── auth_helper.py   # Auth utilities
    └── validators.py    # Input validation
```

## Environment Switching

The application supports easy switching between development and production:

### Development
```bash
export FLASK_ENV=development
python run.py
```

### Production
```bash
export FLASK_ENV=production
python run.py
```

Configuration is automatically loaded from `config.py` based on `FLASK_ENV`.

## Database Schema

The application uses 5 main tables:

1. **users** - User accounts and authentication
2. **categories** - Document categories
3. **documents** - Document metadata
4. **document_views** - View tracking
5. **document_shares** - Sharing between users

See `database_schema.sql` for complete schema.

## S3 Integration

The backend uses your existing `s3.py` file with `RenderS3Client` for:
- Document uploads
- Document downloads
- Data exports (Excel, CSV, PDF, etc.)
- Automatic PDF/Excel processing

## Authentication

JWT-based authentication with:
- Access tokens (24 hours)
- Refresh tokens (30 days)
- Password hashing (pbkdf2:sha256)

## API Examples

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Upload Document
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@document.pdf" \
  -F "category_id=1"
```

### Get Documents
```bash
curl -X GET "http://localhost:5000/api/documents/?search=report&category_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### Database Connection Issues
- Check MySQL is running: `systemctl status mysql`
- Verify credentials in `.env`
- Check database exists: `SHOW DATABASES;`

### Import Errors
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### S3 Upload Failures
- Check `S3_API_BASE_URL` in `.env`
- Verify s3.py is in backend folder
- Check network connectivity to S3 API

## License

MIT

## Support

For issues or questions, please create an issue in the repository.






