# 🏆 Squash Match Tracker

A professional squash match tracking application with ELO rating system, built with React frontend and Flask backend.

## ✨ Features

- **ELO Rating System**: Professional ranking system that adjusts based on match outcomes
- **Session Management**: Create sessions with automatic match generation
- **Real-time Scoring**: Live score input with validation
- **Persistent Database**: External PostgreSQL database ensures data never gets lost
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Match Validation**: Ensures proper squash scoring rules (11+ points, 2-point lead)

## 🚀 Live Demo

**Production**: [Deploy from this GitHub repository]
**Staging**: Available via Manus deployment for testing

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, TailwindCSS, Shadcn/UI
- **Backend**: Flask, SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **Deployment**: Railway, Vercel, Docker support

## 📦 Quick Deploy

### Railway (Recommended)
1. Fork this repository
2. Connect to Railway
3. Set environment variables:
   ```
   DB_CONNECTION_STRING=your_postgresql_url
   ```
4. Deploy!

### Vercel + Supabase
1. Fork this repository
2. Create a Supabase project
3. Deploy to Vercel with environment variables
4. Your app is live!

### Docker
```bash
docker build -t squash-tracker .
docker run -p 5000:5000 -e DB_CONNECTION_STRING=your_db_url squash-tracker
```

## 🔧 Environment Variables

```env
# Database Configuration
DB_TYPE=postgresql
DB_CONNECTION_STRING=postgresql://user:pass@host:port/db

# Optional: Backup Configuration
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
```

## 🏗️ Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/miklaskroagerdk/squash-tracker.git
   cd squash-tracker
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

5. **Access the app**
   Open http://localhost:5000

## 📊 Database Schema

The application uses three main tables:
- **players**: Player information and ELO ratings
- **sessions**: Match sessions with date and completion status
- **matches**: Individual match results with scores

## 🎮 How to Use

1. **Add Players**: Start by adding players in the "Manage Players" section
2. **Create Session**: Select players and create a new session
3. **Play Matches**: The app automatically generates 5 matches per session
4. **Enter Scores**: Input match scores with real-time validation
5. **Track Rankings**: View the leaderboard with ELO ratings

## 🔒 Data Persistence

- **External Database**: Uses PostgreSQL for guaranteed data persistence
- **No Data Loss**: Data survives all deployments and updates
- **Automatic Backups**: Optional backup system for extra security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use this project for your squash club!

## 🙋‍♂️ Support

For issues or questions:
1. Check the [Issues](https://github.com/miklaskroagerdk/squash-tracker/issues) page
2. Create a new issue if needed
3. Include details about your deployment environment

---

**Built with ❤️ for the squash community**

