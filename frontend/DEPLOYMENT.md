# Deployment Guide - Render

This guide walks you through deploying the Procurement Agent to Render (free tier available).

## Prerequisites

- GitHub account
- Render account (sign up at https://render.com)
- Push your code to GitHub

## Deployment Steps

### 1. Prepare Your Repository

Make sure all files are committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy Backend (FastAPI)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `procurement-agent-api` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

5. Click **"Create Web Service"**
6. Wait for deployment (5-10 minutes)
7. **Copy your backend URL**: `https://procurement-agent-api.onrender.com` (or similar)

### 3. Deploy Frontend (React/Vite)

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect the same GitHub repository
3. Configure the service:
   - **Name**: `procurement-agent-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Instance Type**: `Free`

4. **Add Environment Variable**:
   - Click **"Environment"** tab
   - Add: `VITE_API_URL` = `https://your-backend-url.onrender.com`
   - (Replace with your actual backend URL from step 2.7)

5. Click **"Create Static Site"**
6. Wait for deployment
7. **Your app is live!** Visit the provided URL

## Important Notes

### Free Tier Limitations

- **Backend**: Spins down after 15 minutes of inactivity (first request takes ~30s to wake up)
- **Frontend**: Always available (static site)
- **Storage**: Ephemeral (catalog.json persists as it's in code)

### CORS Configuration

The backend is configured to accept requests from any origin (`allow_origins=["*"]`). For production, update `backend/api.py` line 33:

```python
allow_origins=["https://your-frontend-url.onrender.com"]
```

### Environment Variables (Optional)

If using OpenAI, set in Render backend environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key

## Updating Your Deployment

Render auto-deploys on every push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Both services will automatically rebuild and redeploy.

## Troubleshooting

### Backend not responding
- Check logs in Render dashboard
- Ensure `PORT` environment variable is used (Render provides this automatically)
- First request after inactivity takes 30+ seconds on free tier

### Frontend can't connect to backend
- Verify `VITE_API_URL` environment variable is set correctly
- Check CORS settings in `backend/api.py`
- Ensure backend is deployed and running

### Build failures
- Check Render build logs for specific errors
- Verify all dependencies are in `requirements.txt` (backend) and `package.json` (frontend)

## Alternative: Using render.yaml

You can deploy both services at once using the included `render.yaml`:

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. Connect your repository
3. Render will detect `render.yaml` and create both services
4. Still need to add `VITE_API_URL` environment variable to frontend manually

## Cost

- **Free tier**: $0/month
- **Limitations**: Services sleep after inactivity, 750 hours/month
- **Upgrade**: Paid plans start at $7/month for always-on services

---

**Your app should now be live and accessible from anywhere!**

Need help? Check [Render Documentation](https://render.com/docs)
