# 📘 DocHub API Documentation

Complete API reference for DocHub document management system.

## Base URL

**Development:** `http://localhost:5000/api`  
**Production:** `https://your-domain.com/api`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Response Format

All responses follow this structure:

### Success Response
```json
{
  "data": {},
  "message": "Success message"
}
```

### Error Response
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": "Additional details (only in development)"
}
```

---

## 🔐 Authentication Endpoints

### Register User

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Validation:**
- Name: Required, non-empty
- Email: Required, valid email format, unique
- Password: Required, minimum 6 characters

---

### Login

**POST** `/auth/login`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### Get Current User

**GET** `/auth/me`

Get authenticated user's information.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "department": "IT",
    "phone": "+1234567890",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

---

### Refresh Token

**POST** `/auth/refresh`

Get new access token using refresh token.

**Headers:** `Authorization: Bearer {refresh_token}`

**Response:** `200 OK`
```json
{
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## 📄 Document Endpoints

### List Documents

**GET** `/documents/`

Get all documents with optional filters and pagination.

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `category_id` (int, optional): Filter by category
- `search` (string, optional): Search in name, summary, category
- `page` (int, default: 1): Page number
- `per_page` (int, default: 20): Items per page

**Example:**
```
GET /documents/?category_id=1&search=report&page=1&per_page=10
```

**Response:** `200 OK`
```json
{
  "documents": [
    {
      "id": 1,
      "name": "Annual Report 2024.pdf",
      "originalName": "Annual Report 2024.pdf",
      "category": "Reports",
      "categoryId": 2,
      "categoryColor": "hsl(199 89% 48%)",
      "size": "2.4 MB",
      "type": "pdf",
      "uploadedAt": "2024-01-15T10:30:00",
      "uploadedBy": "John Smith",
      "url": "https://s3.amazonaws.com/...",
      "s3Key": "documents/abc123.pdf",
      "summary": "Annual financial report for 2024...",
      "pageCount": 45,
      "status": "ready"
    }
  ],
  "total": 100,
  "page": 1,
  "perPage": 20,
  "totalPages": 5
}
```

---

### Get Document

**GET** `/documents/{id}`

Get single document details.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "document": {
    "id": 1,
    "name": "Annual Report 2024.pdf",
    "originalName": "Annual Report 2024.pdf",
    "category": "Reports",
    "categoryId": 2,
    "categoryColor": "hsl(199 89% 48%)",
    "size": "2.4 MB",
    "type": "pdf",
    "uploadedAt": "2024-01-15T10:30:00",
    "uploadedBy": "John Smith",
    "url": "https://s3.amazonaws.com/...",
    "s3Key": "documents/abc123.pdf",
    "summary": "Full summary text...",
    "extractedText": "Full extracted text...",
    "pageCount": 45,
    "wordCount": 5000,
    "author": "Finance Team",
    "title": "Annual Report",
    "status": "ready"
  }
}
```

---

### Upload Document

**POST** `/documents/upload`

Upload a new document to S3 and create database record.

**Headers:** 
- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Form Data:**
- `file` (file, required): Document file
- `category_id` (int, required): Category ID
- `custom_name` (string, optional): Custom filename

**Allowed File Types:**
- pdf, doc, docx, xls, xlsx, ppt, pptx, txt, csv

**Example (curl):**
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "category_id=1" \
  -F "custom_name=My Document.pdf"
```

**Response:** `201 Created`
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 10,
    "name": "My Document.pdf",
    "category": "Contracts",
    "categoryColor": "hsl(38 92% 50%)",
    "size": "1.2 MB",
    "type": "pdf",
    "uploadedAt": "2024-01-20T15:45:00",
    "uploadedBy": "John Doe",
    "url": "https://s3.amazonaws.com/...",
    "status": "processing"
  },
  "uploadResult": {
    "success": true,
    "s3_key": "documents/xyz789.pdf",
    "s3_url": "https://s3.amazonaws.com/..."
  }
}
```

**Processing Status:**
- `processing`: Document is being analyzed (PDF/Excel)
- `ready`: Document is ready
- `failed`: Processing failed

---

### Delete Document

**DELETE** `/documents/{id}`

Soft delete a document (marks as archived).

**Headers:** `Authorization: Bearer {token}`

**Permissions:** Only uploader or admin can delete

**Response:** `200 OK`
```json
{
  "message": "Document deleted successfully"
}
```

---

## 🏷️ Category Endpoints

### List Categories

**GET** `/categories/`

Get all active categories.

**Headers:** `Authorization: Bearer {token}`

**Query Parameters:**
- `include_inactive` (boolean, default: false): Include inactive categories

**Response:** `200 OK`
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Contracts",
      "color": "hsl(38 92% 50%)",
      "description": "Business contracts and agreements",
      "icon": "📄",
      "count": 15,
      "isActive": true,
      "createdBy": "Admin User",
      "createdAt": "2024-01-01T00:00:00"
    }
  ]
}
```

---

### Create Category

**POST** `/categories/`

Create a new category.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "Legal Documents",
  "color": "hsl(262 83% 58%)",
  "description": "Legal and compliance documents",
  "icon": "⚖️"
}
```

**Response:** `201 Created`
```json
{
  "message": "Category created successfully",
  "category": {
    "id": 7,
    "name": "Legal Documents",
    "color": "hsl(262 83% 58%)",
    "description": "Legal and compliance documents",
    "icon": "⚖️",
    "count": 0,
    "isActive": true
  }
}
```

---

### Update Category

**PUT** `/categories/{id}`

Update category details.

**Headers:** `Authorization: Bearer {token}`

**Request Body:** (all fields optional)
```json
{
  "name": "Legal & Compliance",
  "color": "hsl(262 83% 58%)",
  "description": "Updated description",
  "icon": "⚖️"
}
```

**Response:** `200 OK`
```json
{
  "message": "Category updated successfully",
  "category": {
    "id": 7,
    "name": "Legal & Compliance",
    "color": "hsl(262 83% 58%)",
    "description": "Updated description",
    "icon": "⚖️",
    "count": 0,
    "isActive": true
  }
}
```

---

### Delete Category

**DELETE** `/categories/{id}`

Soft delete a category.

**Headers:** `Authorization: Bearer {token}`

**Note:** Cannot delete category with documents. Reassign or delete documents first.

**Response:** `200 OK`
```json
{
  "message": "Category deleted successfully"
}
```

---

## 📊 Statistics Endpoints

### Get Dashboard Stats

**GET** `/stats/`

Get comprehensive dashboard statistics.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "totalDocuments": 150,
  "totalCategories": 6,
  "totalUsers": 25,
  "totalStorage": 5368709120,
  "totalStorageFormatted": "5.0 GB",
  "recentUploads": 12,
  "categoryStats": [
    {
      "name": "Reports",
      "color": "hsl(199 89% 48%)",
      "count": 45,
      "size": 2147483648,
      "sizeFormatted": "2.0 GB"
    }
  ],
  "topUploaders": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "count": 30
    }
  ],
  "fileTypeStats": [
    {
      "type": "pdf",
      "count": 80
    },
    {
      "type": "xlsx",
      "count": 40
    }
  ]
}
```

---

## 👥 User Endpoints

### List Users

**GET** `/users/`

Get all active users with their document counts.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "department": "IT",
      "documentCount": 30,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

---

### Update Profile

**PUT** `/users/profile`

Update current user's profile.

**Headers:** `Authorization: Bearer {token}`

**Request Body:** (all fields optional)
```json
{
  "name": "John Updated",
  "department": "Engineering",
  "phone": "+1234567890"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "name": "John Updated",
    "email": "john@example.com",
    "department": "Engineering",
    "phone": "+1234567890"
  }
}
```

---

## ❤️ Health Check

### API Health

**GET** `/health`

Check if API is running.

**No authentication required**

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

---

## ❌ Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Duplicate resource |
| 500 | Internal Server Error |

---

## 🔒 Rate Limiting

API requests are rate-limited to prevent abuse:
- **Development:** No limits
- **Production:** 100 requests per minute per IP

Exceeded limits return `429 Too Many Requests`.

---

## 📝 Notes

1. **Tokens expire:**
   - Access tokens: 24 hours
   - Refresh tokens: 30 days

2. **File processing:**
   - PDF files are automatically processed for text extraction and summary
   - Excel files are processed for metadata
   - Processing happens asynchronously

3. **Search functionality:**
   - Searches in document name, summary, and category
   - Case-insensitive
   - Supports partial matching

4. **Soft deletes:**
   - Documents and categories are soft-deleted (marked as archived/inactive)
   - Can be restored by updating the database directly if needed

---

## 🧪 Testing with Postman

Import this as a Postman collection or use individual requests:

1. **Register** → Get tokens
2. **Use token** in Authorization header for other requests
3. **Create category** → Get category ID
4. **Upload document** → Use category ID
5. **List documents** → See uploaded document
6. **Get stats** → View dashboard data

Happy API testing! 🚀






