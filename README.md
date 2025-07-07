# Squash Match Tracker

A professional squash match tracking application with ELO rating system, persistent data storage, and comprehensive backup features.

## Features

- 🏆 **ELO Rating System** - Point-based ELO calculations with fair match scoring
- - 📊 **Real-time Leaderboard** - Live rankings based on ELO ratings
  - - ⚡ **Easy Score Input** - Large, intuitive input fields for quick match entry
    - - 🎯 **Match Highlights** - Recent match results with ELO changes displayed
      - - 💾 **Persistent Data** - External database storage that survives deployments
        - - 🔄 **Automatic Backups** - Multiple backup systems for data protection
          - - 📱 **Responsive Design** - Works perfectly on desktop and mobile devices
           
            - ## Quick Start
           
            - ### 1. Clone the Repository
            - ```bash
              git clone https://github.com/miklaskroagerdk/squash-tracker.git
              cd squash-tracker
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

              ### Option 3: Simple External SQLite
              ```env
              DB_TYPE=sqlite
              DATABASE_URL=sqlite:///path/to/external/database.db
              ```

              ## Deployment

              ### Railway (Recommended)
              1. Fork this repository
              2. 2. Connect to Railway
                 3. 3. Add PostgreSQL database
                    4. 4. Set environment variables
                       5. 5. Deploy automatically
                         
                          6. ### Docker Deployment
                          7. ```bash
                             docker build -t squash-tracker .
                             docker run -p 5000:5000 --env-file .env squash-tracker
                             ```

                             ## License

                             MIT License
