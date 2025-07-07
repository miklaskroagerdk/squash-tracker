# Squash Match Tracker

A professional squash match tracking application with ELO rating system, persistent data storage, and comprehensive backup features.

## Features

- 🏆 **ELO Rating System** - Point-based ELO calculations with fair match scoring
- 📊 **Real-time Leaderboard** - Live rankings based on ELO ratings
- ⚡ **Easy Score Input** - Large, intuitive input fields for quick match entry
- 🎯 **Match Highlights** - Recent match results with ELO changes displayed
- 💾 **Persistent Data** - External database storage that survives deployments
- 🔄 **Automatic Backups** - Multiple backup systems for data protection
- 📱 **Responsive Design** - Works perfectly on desktop and mobile devices

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd squash-tracker-final
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Copy `.env.example` to `.env` and configure your database:

```bash
cp .env.example .env
```

Edit `.env` with your database configuration (see Database Options below).

### 4. Run the Application
```bash
cd src
python main.py
```

The application will be available at `http://localhost:5000`

## Database Options

### Option 1: External PostgreSQL (Recommended for Production)
```env
DB_TYPE=postgresql
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Option 2: External MySQL
```env
DB_TYPE=mysql
DATABASE_URL=mysql://username:password@host:port/database_name
```

### Option 3: Cloud SQLite with GitHub Storage (Default)
```env
DB_TYPE=cloud_sqlite
GITHUB_TOKEN=your_github_personal_access_token
```

### Option 4: Simple External SQLite
```env
DB_TYPE=sqlite
DATABASE_URL=sqlite:///path/to/external/database.db
```

## Deployment

### GitHub Pages / Vercel / Netlify
1. Fork this repository
2. Set up environment variables in your deployment platform
3. Configure your external database
4. Deploy directly from GitHub

### Docker Deployment
```bash
docker build -t squash-tracker .
docker run -p 5000:5000 --env-file .env squash-tracker
```

### Manual Deployment
1. Set up your external database
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `cd src && python main.py`

## Data Persistence

This application uses external database storage to ensure data persists across deployments:

- **External Database**: Data is stored in your configured external database
- **Automatic Backups**: Multiple backup systems protect your data
- **Cloud Sync**: Optional GitHub-based backup for SQLite configurations
- **Admin Tools**: Manual export/import capabilities via admin endpoints

## Admin Endpoints

Access these endpoints for data management:

- `GET /api/admin/database/status` - Database and backup status
- `POST /api/admin/cloud/export` - Export data to cloud backup
- `POST /api/admin/cloud/import` - Import data from cloud backup
- `GET /api/admin/cloud/download-backups` - List downloadable backups
- `POST /api/admin/deployment/backup` - Create deployment backup

## API Documentation

### Players
- `GET /api/players` - Get all players
- `POST /api/players` - Create new player
- `PUT /api/players/<id>` - Update player
- `DELETE /api/players/<id>` - Delete player

### Sessions
- `GET /api/sessions` - Get all sessions
- `POST /api/sessions` - Create new session
- `PUT /api/sessions/<id>` - Update session
- `DELETE /api/sessions/<id>` - Delete session

### Matches
- `GET /api/sessions/<id>/matches` - Get matches for session
- `PUT /api/matches/<id>` - Update match scores
- `DELETE /api/matches/<id>` - Delete match

## Development

### Project Structure
```
squash-tracker-final/
├── src/
│   ├── main.py                 # Main application
│   ├── models/
│   │   └── squash.py          # Database models
│   ├── routes/
│   │   └── squash.py          # API routes
│   ├── static/                # Frontend files
│   ├── database_manager.py    # Database management
│   ├── external_database.py   # External database configuration
│   ├── backup_scheduler.py    # Automated backups
│   ├── deployment_safety.py   # Deployment safety features
│   └── cloud_persistence.py   # Cloud data persistence
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

### Adding Features
1. Update database models in `src/models/squash.py`
2. Add API routes in `src/routes/squash.py`
3. Update frontend in `src/static/`
4. Test with external database configuration

## Troubleshooting

### Database Connection Issues
1. Verify your database credentials in `.env`
2. Check database server accessibility
3. Review logs for connection errors
4. Test connection using admin endpoints

### Data Not Persisting
1. Confirm external database is configured
2. Check environment variables are loaded
3. Verify database write permissions
4. Use admin endpoints to check database status

### Backup Issues
1. Check backup directory permissions
2. Verify cloud storage configuration
3. Test manual backup creation
4. Review backup scheduler logs

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review admin endpoint status
3. Check application logs
4. Verify database configuration

