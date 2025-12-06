# UNILAG Price Saver - Vercel Deployment Guide

## 1. Prepare Your Project Structure

Create a `vercel.json` in your backend root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "50mb" }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

## 2. Update Backend for CORS

Add this to `app/main.py` after creating the FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://*.vercel.app",  # Allow all Vercel deployments
        "*"  # For dev; restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 3. Create Frontend Folders

```
.
├── app/               # FastAPI backend
├── frontend.html      # Standalone HTML (for serving locally)
├── public/            # New: Static frontend for Vercel
│   ├── index.html     # Multi-page frontend
│   ├── styles.css     # (optional) Separated styles
│   └── app.js         # (optional) Separated JavaScript
└── vercel.json
```

## 4. Deploy Backend to Vercel

```powershell
# 1. Install Vercel CLI
npm install -g vercel
# or
pip install vercel

# 2. Login to Vercel (creates account if needed)
vercel login

# 3. Deploy from project root
vercel --prod

# Note the backend URL: https://your-project.vercel.app
```

## 5. Deploy Frontend to Vercel

**Option A: Deploy together (Backend + Frontend)**

```powershell
# Frontend as static files in public/
# Vercel will serve public/index.html automatically

# After step 4, Vercel will ask to deploy frontend
vercel --prod
```

**Option B: Deploy frontend separately**

```powershell
# Create separate Vercel project for frontend
mkdir unilag-price-saver-frontend
cd unilag-price-saver-frontend

# Create index.html with your multi-page frontend code
# (Paste the frontend code below into index.html)

# Deploy
vercel --prod
```

## 6. Frontend Configuration for Vercel

Once frontend is deployed, update the API URL in your frontend JavaScript:

```javascript
// Detect environment and set API URL
const isProduction = window.location.hostname.includes('vercel.app');
let API_URL = localStorage.getItem('apiUrl');

if (!API_URL) {
    API_URL = isProduction 
        ? 'https://your-backend.vercel.app'  // Production backend URL
        : 'http://localhost:8000';             // Local backend URL
}
```

## 7. Environment Variables

Create `.env.local` in your project root (Vercel will read this):

```
VITE_API_URL=https://your-backend.vercel.app
DATABASE_URL=sqlite:///./prices.db
ADMIN_API_KEY=your-secure-admin-key-here
```

In `app/main.py`:
```python
import os
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "change-me-in-env")
BACKEND_URL = os.getenv("VITE_API_URL", "http://localhost:8000")
```

## 8. Complete Frontend Code (Multi-Page)

Save as `public/index.html`:

```html
[See separate frontend.html file with page classes]
```

## Quick Deployment Checklist

- [ ] Backend `vercel.json` created
- [ ] CORS middleware added to FastAPI
- [ ] Environment variables set in Vercel dashboard
- [ ] Backend deployed: `vercel --prod`
- [ ] Note backend URL from Vercel
- [ ] Frontend deployed or served from same project
- [ ] Frontend API URL points to backend URL
- [ ] Test endpoints via Swagger UI: `https://your-backend.vercel.app/docs`

## Testing After Deployment

1. Visit frontend: `https://your-frontend.vercel.app`
2. Click "Check Backend Connection" button
3. Should show `"status": 200` if connected
4. Test create items, prices, etc.

## Troubleshooting

**502 Bad Gateway**: Backend server crashed
- Check logs: `vercel logs`
- Verify `ADMIN_API_KEY` env var is set

**CORS errors**: Frontend can't reach backend
- Ensure CORS middleware is added to FastAPI
- Check `allow_origins` includes frontend domain

**Database errors**: SQLite not persisting
- Use environment-managed database (PostgreSQL on Heroku/Railway)
- Or use serverless alternative like Turso SQLite

## Next Steps

- Add authentication (JWT tokens)
- Use environment-specific URLs
- Set up CI/CD with GitHub Actions
- Monitor with Vercel analytics
- Add database migrations
