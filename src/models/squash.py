from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    elo_rating = db.Column(db.Integer, default=1000, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    player1_matches = db.relationship('Match', foreign_keys='Match.player1_id', backref='player1', lazy='dynamic')
    player2_matches = db.relationship('Match', foreign_keys='Match.player2_id', backref='player2', lazy='dynamic')
    won_matches = db.relationship('Match', foreign_keys='Match.winner_id', backref='winner', lazy='dynamic')
    
    def __repr__(self):
        return f'<Player {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'elo_rating': self.elo_rating,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    matches = db.relationship('Match', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Session {self.id} on {self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'matches': [match.to_dict() for match in self.matches.all()]
        }

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player1_score = db.Column(db.Integer, nullable=True)
    player2_score = db.Column(db.Integer, nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    player1_elo_before = db.Column(db.Integer, nullable=True)
    player2_elo_before = db.Column(db.Integer, nullable=True)
    player1_elo_change = db.Column(db.Integer, nullable=True)
    player2_elo_change = db.Column(db.Integer, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.CheckConstraint('player1_id != player2_id', name='different_players'),
        Index('idx_match_session_players', 'session_id', 'player1_id', 'player2_id'),
        Index('idx_match_completed', 'completed_at'),
    )
    
    def __repr__(self):
        return f'<Match {self.id}: {self.player1_score or "?"}-{self.player2_score or "?"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'winner_id': self.winner_id,
            'player1_elo_before': self.player1_elo_before,
            'player2_elo_before': self.player2_elo_before,
            'player1_elo_change': self.player1_elo_change,
            'player2_elo_change': self.player2_elo_change,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'player1_name': self.player1.name if self.player1 else None,
            'player2_name': self.player2.name if self.player2 else None,
            'winner_name': self.winner.name if self.winner else None,
            'is_completed': self.is_completed()
        }
    
    def is_completed(self):
        """Check if match has been completed (has scores)"""
        return self.player1_score is not None and self.player2_score is not None
    
    def update_scores(self, player1_score, player2_score):
        """Update match scores, determine winner, and calculate ELO changes"""
        # Store ELO ratings before the match
        self.player1_elo_before = self.player1.elo_rating
        self.player2_elo_before = self.player2.elo_rating
        
        # Update scores
        self.player1_score = player1_score
        self.player2_score = player2_score
        
        # Set completion timestamp
        self.completed_at = datetime.utcnow()
        
        # Determine winner
        if player1_score > player2_score:
            self.winner_id = self.player1_id
        elif player2_score > player1_score:
            self.winner_id = self.player2_id
        else:
            self.winner_id = None  # Tie
        
        # Calculate ELO changes based on points scored
        elo_changes = self.calculate_elo_changes(
            self.player1_elo_before, 
            self.player2_elo_before, 
            player1_score, 
            player2_score
        )
        
        self.player1_elo_change = elo_changes[0]
        self.player2_elo_change = elo_changes[1]
        
        # Update player ELO ratings
        self.player1.elo_rating += self.player1_elo_change
        self.player2.elo_rating += self.player2_elo_change
    
    @staticmethod
    def calculate_elo_changes(elo1, elo2, score1, score2):
        """
        Calculate ELO changes based on points scored in the match
        
        Args:
            elo1, elo2: Current ELO ratings of players
            score1, score2: Points scored in the match
            
        Returns:
            tuple: (player1_elo_change, player2_elo_change)
        """
        # Base K-factor (maximum rating change)
        K = 32
        
        # Calculate expected scores based on ELO difference
        expected1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
        expected2 = 1 - expected1
        
        # Calculate actual performance based on points scored
        total_points = score1 + score2
        if total_points == 0:
            actual1 = actual2 = 0.5  # Tie with no points
        else:
            actual1 = score1 / total_points
            actual2 = score2 / total_points
        
        # Calculate point differential multiplier (closer matches = smaller changes)
        point_diff = abs(score1 - score2)
        max_possible_diff = max(score1, score2)  # Maximum possible difference
        
        if max_possible_diff == 0:
            diff_multiplier = 1.0
        else:
            # Scale from 0.5 (very close) to 1.5 (blowout)
            diff_multiplier = 0.5 + (point_diff / max_possible_diff)
        
        # Calculate ELO changes
        change1 = int(K * diff_multiplier * (actual1 - expected1))
        change2 = int(K * diff_multiplier * (actual2 - expected2))
        
        return (change1, change2)

def init_database(app):
    """Initialize database with default data"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Create default players if they don't exist
        default_players = ['Miklas', 'Morten', 'Patrick', 'Jens']
        for player_name in default_players:
            existing_player = Player.query.filter_by(name=player_name).first()
            if not existing_player:
                player = Player(name=player_name)
                db.session.add(player)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing default players: {e}")

