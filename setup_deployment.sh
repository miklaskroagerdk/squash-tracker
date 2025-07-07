#!/bin/bash

echo "🏆 Squash Tracker Deployment Setup"
echo "=================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

echo "📁 Initializing Git repository..."
git init

echo "📝 Adding all files..."
git add .

echo "💾 Creating initial commit..."
git commit -m "Initial commit: Squash Tracker with external database support"

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name it 'squash-tracker' (or your preferred name)"
echo "   - Make it public or private"
echo "   - DO NOT initialize with README (we already have files)"
echo ""
echo "2. Connect this repository to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Choose a deployment platform:"
echo ""
echo "   🚀 OPTION A: Railway (Easiest - Recommended)"
echo "   - Go to https://railway.app"
echo "   - Sign in with GitHub"
echo "   - Click 'Deploy from GitHub'"
echo "   - Select your repository"
echo "   - Add PostgreSQL service"
echo "   - Deploy!"
echo ""
echo "   🚀 OPTION B: Vercel + Supabase"
echo "   - Set up database: https://supabase.com"
echo "   - Deploy app: https://vercel.com"
echo "   - Connect GitHub repository"
echo "   - Add DATABASE_URL environment variable"
echo ""
echo "   🚀 OPTION C: Render + PlanetScale"
echo "   - Set up database: https://planetscale.com"
echo "   - Deploy app: https://render.com"
echo "   - Connect GitHub repository"
echo "   - Add DATABASE_URL environment variable"
echo ""
echo "4. Set environment variables (if not using Railway):"
echo "   DATABASE_URL=your_database_connection_string"
echo "   DB_TYPE=postgresql"
echo ""
echo "5. Test your deployment:"
echo "   - Visit your app URL"
echo "   - Check /api/admin/database/status"
echo "   - Create test data"
echo "   - Redeploy and verify data persists"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "✅ Repository is ready for deployment!"

