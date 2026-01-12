# Docker Guide - Building, Pushing, and Pulling Images

## Important Note

**You MUST have Dockerfiles to create Docker images.** Dockerfiles contain the instructions for building images. I've created the necessary Dockerfiles for you:

- ✅ `backend/Dockerfile` - For backend Flask application
- ✅ `Dockerfile` (in root) - For frontend React/Vite application

---

## Quick Start

### 1. Build Images Locally

#### Build Backend Image:
```bash
cd backend
docker build -t dochub_backend:latest .
```

#### Build Frontend Image:
```bash
# From project root
docker build -t dochub_frontend:latest .
```

---

## Building and Pushing to ECR

### Step 1: Login to ECR

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 480940871468.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 2: Build Backend Image

```bash
cd backend
docker build -t dochub_backend:latest .
```

### Step 3: Tag Backend Image for ECR

```bash
docker tag dochub_backend:latest 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:backend-latest
```

### Step 4: Push Backend Image to ECR

```bash
docker push 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:backend-latest
```

### Step 5: Build Frontend Image

```bash
# From project root
docker build -t dochub_frontend:latest .
```

**Note:** If you need to set environment variables during build:
```bash
docker build --build-arg VITE_API_BASE_URL=http://13.205.15.232:8002/api -t dochub_frontend:latest .
```

### Step 6: Tag Frontend Image for ECR

```bash
docker tag dochub_frontend:latest 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:frontend-latest
```

### Step 7: Push Frontend Image to ECR

```bash
docker push 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:frontend-latest
```

---

## Pulling Images from ECR

### Pull Backend Image:

```bash
# Login first
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 480940871468.dkr.ecr.ap-south-1.amazonaws.com

# Pull image
docker pull 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:backend-latest

# Tag for local use
docker tag 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:backend-latest dochub_backend:latest
```

### Pull Frontend Image:

```bash
# Pull image
docker pull 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:frontend-latest

# Tag for local use
docker tag 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:frontend-latest dochub_frontend:latest
```

---

## Running Containers Locally

### Run Backend Container:

```bash
docker run -d \
  --name dochub_backend \
  -p 8002:8000 \
  --env-file /path/to/config.env \
  -v /path/to/MEDIA_ROOT:/app/MEDIA_ROOT \
  -v /path/to/TEMP_MEDIA_ROOT:/app/TEMP_MEDIA_ROOT \
  -v /path/to/Reports:/app/Reports \
  dochub_backend:latest
```

### Run Frontend Container:

```bash
docker run -d \
  --name dochub_frontend \
  -p 8081:80 \
  dochub_frontend:latest
```

---

## Using GitHub Actions Workflow

The workflow in `.github/workflows/main.yml` will automatically:

1. ✅ Build both images
2. ✅ Tag them for ECR
3. ✅ Push to ECR
4. ✅ Deploy containers

**You just need to:**
- Ensure Dockerfiles are in place (✅ Done)
- Create `.env.production` for frontend build
- Push to main/master branch

---

## Frontend Build with Environment Variables

The frontend Dockerfile supports build arguments. To build with specific backend URL:

```bash
docker build \
  --build-arg VITE_API_BASE_URL=http://13.205.15.232:8002/api \
  --build-arg VITE_ENV=production \
  -t dochub_frontend:latest .
```

**OR** create `.env.production` file in project root:
```env
VITE_API_BASE_URL=http://13.205.15.232:8002/api
VITE_ENV=production
```

Then build normally - Vite will automatically read `.env.production` during build.

---

## Troubleshooting

### Build fails?

1. **Check Docker is running:**
   ```bash
   docker ps
   ```

2. **Check Dockerfile syntax:**
   ```bash
   docker build --no-cache -t test .
   ```

3. **Check for missing files:**
   - Backend: Ensure `requirements.txt` exists
   - Frontend: Ensure `package.json` exists

### Push fails?

1. **Check ECR login:**
   ```bash
   aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 480940871468.dkr.ecr.ap-south-1.amazonaws.com
   ```

2. **Check repository exists in ECR:**
   ```bash
   aws ecr describe-repositories --region ap-south-1
   ```

3. **Check IAM permissions** for ECR push

### Pull fails?

1. **Ensure you're logged in to ECR**
2. **Check image tag exists:**
   ```bash
   aws ecr describe-images --repository-name dochub --region ap-south-1
   ```

---

## Complete Workflow Example

```bash
# 1. Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 480940871468.dkr.ecr.ap-south-1.amazonaws.com

# 2. Build and push backend
cd backend
docker build -t dochub_backend:latest .
docker tag dochub_backend:latest 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:backend-latest
docker push 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:backend-latest

# 3. Build and push frontend
cd ..
docker build -t dochub_frontend:latest .
docker tag dochub_frontend:latest 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:frontend-latest
docker push 480940871468.dkr.ecr.ap-south-1.amazonaws.com/dochub:frontend-latest
```

---

## Summary

✅ **Dockerfiles Created:**
- `backend/Dockerfile` - Backend Flask app
- `Dockerfile` - Frontend React/Vite app

✅ **Next Steps:**
1. Create `.env.production` for frontend
2. Build images (manually or via GitHub Actions)
3. Push to ECR
4. Deploy using the workflow

The GitHub Actions workflow will handle everything automatically when you push to main/master branch!

