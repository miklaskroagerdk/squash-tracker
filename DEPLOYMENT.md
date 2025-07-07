# Squash Tracker Deployment Guide

This guide provides step-by-step instructions for deploying your Squash Tracker with persistent external database storage.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
1. **Create Railway account**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your GitHub account
3. **Deploy from GitHub**: Select your repository
4. **Add PostgreSQL**: Add a PostgreSQL service to your project
5. **Environment variables**: Railway auto-configures DATABASE_URL
6. **Deploy**: Your app will be live with persistent database!

### Option 2: Vercel + Supabase
1. **Create Supabase account**: Go to [supabase.com](https://supabase.com)
2. **Create new project**: Get your PostgreSQL connection string
3. **Deploy to Vercel**: Connect your GitHub repository
4. **Set environment variables**: Add DATABASE_URL in Vercel dashboard
5. **Deploy**: Your app will be live!

### Option 3: Render + PlanetScale
1. **Create PlanetScale account**: Go to [planetscale.com](https://planetscale.com)
2. **Create database**: Get your MySQL connection string
3. **Deploy to Render**: Connect your GitHub repository
4. **Set environment variables**: Add DATABASE_URL
5. **Deploy**: Your app will be live!

## 🗄️ Database Setup

### PostgreSQL (Recommended)
**Free providers:**
- **Supabase**: 500MB free, excellent for small apps
- **Railway**: 1GB free, auto-configures with your app
- **ElephantSQL**: 20MB free, good for testing

**Environment variables:**
```env
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:password@host:port/database
```

### MySQL
**Free providers:**
- **PlanetScale**: 1GB free, serverless MySQL
- **Railway**: 1GB free MySQL service

**Environment variables:**
```env
DB_TYPE=mysql
DATABASE_URL=mysql://user:password@host:port/database
```

### SQLite (Development only)
```env
DB_TYPE=sqlite
SQLITE_PATH=/path/to/database.db
```

## 🔧 Step-by-Step Deployment

### Step 1: Set Up External Database

#### Option A: Supabase (PostgreSQL)
1. Go to [supabase.com](https://supabase.com) and create account
2. Create new project
3. Go to Settings > Database
4. Copy the connection string (URI format)
5. Save for Step 3

#### Option B: Railway Database
1. Go to [railway.app](https://railway.app) and create account
2. Create new project
3. Add PostgreSQL service
4. Copy DATABASE_URL from Variables tab
5. Save for Step 3

#### Option C: PlanetScale (MySQL)
1. Go to [planetscale.com](https://planetscale.com) and create account
2. Create new database
3. Create branch (main)
4. Get connection string from Connect tab
5. Save for Step 3

### Step 2: Prepare Repository
1. **Fork/Clone**: Fork this repository or upload files to new repo
2. **Verify files**: Ensure all files are present:
   - `src/` directory with application code
   - `requirements.txt`
   - `Dockerfile`
   - `vercel.json` / `railway.toml` / `Procfile`
   - `.env.example`

### Step 3: Deploy Application

#### Option A: Deploy to Railway
1. **Connect GitHub**: Link your repository
2. **Deploy**: Railway will auto-detect and deploy
3. **Add database**: Add PostgreSQL service if not using external
4. **Set variables**: Add DATABASE_URL if using external database
5. **Done**: Your app is live with persistent database!

#### Option B: Deploy to Vercel
1. **Connect GitHub**: Import your repository
2. **Set environment variables**:
   ```
   DATABASE_URL=your_database_connection_string
   DB_TYPE=postgresql
   ```
3. **Deploy**: Vercel will build and deploy
4. **Done**: Your app is live!

#### Option C: Deploy to Render
1. **Connect GitHub**: Link your repository
2. **Create Web Service**: Select your repository
3. **Set environment variables**:
   ```
   DATABASE_URL=your_database_connection_string
   DB_TYPE=postgresql
   ```
4. **Deploy**: Render will build and deploy
5. **Done**: Your app is live!

## 🔐 Environment Variables

### Required Variables
```env
# Database Configuration
DATABASE_URL=your_database_connection_string
DB_TYPE=postgresql  # or mysql, sqlite

# Optional: Flask Configuration
FLASK_ENV=production
```

### Platform-Specific Setup

#### Railway
- DATABASE_URL is auto-configured if using Railway PostgreSQL
- No additional setup needed

#### Vercel
- Add variables in Vercel dashboard under Settings > Environment Variables
- Redeploy after adding variables

#### Render
- Add variables in Render dashboard under Environment
- Auto-deploys when variables are updated

## ✅ Verification

### Test Your Deployment
1. **Visit your app URL**
2. **Check database status**: Visit `/api/admin/database/status`
3. **Create test data**: Add players and matches
4. **Redeploy**: Make a small change and redeploy
5. **Verify persistence**: Check that data survived the redeployment

### Expected Response from `/api/admin/database/status`:
```json
{
  "success": true,
  "database": {
    "uri": "postgresql://...",
    "exists": true,
    "size": 28672,
    "connection_ok": true
  },
  "backups": {
    "count": 1,
    "latest": {...},
    "total_size": 28672
  }
}
```

## 🔄 Updates and Maintenance

### Updating Your App
1. **Make changes** to your code
2. **Commit and push** to GitHub
3. **Auto-deploy**: Most platforms auto-deploy from GitHub
4. **Verify**: Check that data persists after deployment

### Database Backups
- **Automatic**: App creates backups on startup
- **Manual**: Use `/api/admin/backup/create` endpoint
- **Download**: Use admin endpoints to download backups

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Failed
- **Check DATABASE_URL**: Ensure it's correctly formatted
- **Verify credentials**: Test connection string manually
- **Check firewall**: Ensure database allows connections

#### App Won't Start
- **Check logs**: View deployment logs for errors
- **Verify requirements**: Ensure all dependencies are installed
- **Check environment**: Verify all required variables are set

#### Data Not Persisting
- **Check database type**: Ensure using external database
- **Verify DATABASE_URL**: Must point to external database
- **Test connection**: Use admin endpoints to verify

### Getting Help
1. **Check logs**: View deployment platform logs
2. **Test locally**: Run app locally with same DATABASE_URL
3. **Admin endpoints**: Use `/api/admin/database/status` for diagnostics

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ App loads without errors
- ✅ Database status shows connection_ok: true
- ✅ You can create players and matches
- ✅ Data persists after redeployment
- ✅ Admin endpoints return valid responses

**Congratulations! Your Squash Tracker now has permanent, persistent data storage!** 🏆

