from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from models.squash import db, Player, Session, Match

squash_bp = Blueprint('squash', __name__, url_prefix='/api')

def validate_json_request():
    """Decorator to validate JSON request"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if request.content_type != 'application/json':
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            try:
                data = request.get_json()
                if data is None:
                    data = {}
                return f(*args, data=data, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Invalid JSON'}), 400
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# Health check endpoint
@squash_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Player endpoints
@squash_bp.route('/players', methods=['GET'])
def get_players():
    """Get all active players"""
    try:
        players = Player.query.filter_by(active=True).all()
        return jsonify([player.to_dict() for player in players])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error occurred'}), 500

@squash_bp.route('/players', methods=['POST'])
@validate_json_request()
def create_player(data):
    """Create a new player"""
    try:
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Player name is required'}), 400
        
        # Check if player already exists
        existing_player = Player.query.filter_by(name=name).first()
        if existing_player:
            return jsonify({'error': 'Player with this name already exists'}), 400
        
        player = Player(name=name)
        db.session.add(player)
        db.session.commit()
        
        return jsonify(player.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@squash_bp.route('/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    """Soft delete a player (mark as inactive)"""
    try:
        player = Player.query.get_or_404(player_id)
        player.active = False
        db.session.commit()
        return jsonify({'message': 'Player deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

# Session endpoints
@squash_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions with their matches"""
    try:
        sessions = Session.query.order_by(Session.created_at.desc()).all()
        return jsonify([session.to_dict() for session in sessions])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error occurred'}), 500

@squash_bp.route('/sessions', methods=['POST'])
@validate_json_request()
def create_session(data):
    """Create a new session with matches"""
    try:
        player_ids = data.get('player_ids', [])
        if len(player_ids) < 2:
            return jsonify({'error': 'At least 2 players are required'}), 400
        
        # Validate all players exist
        players = Player.query.filter(Player.id.in_(player_ids)).all()
        if len(players) != len(player_ids):
            return jsonify({'error': 'One or more players not found'}), 404
        
        # Create session
        session = Session()
        db.session.add(session)
        db.session.flush()  # Get session ID
        
        # Create matches for all player combinations
        matches_created = 0
        for i in range(len(player_ids)):
            for j in range(i + 1, len(player_ids)):
                match = Match(
                    session_id=session.id,
                    player1_id=player_ids[i],
                    player2_id=player_ids[j]
                )
                db.session.add(match)
                matches_created += 1
        
        db.session.commit()
        
        # Return session with matches
        session = Session.query.get(session.id)
        return jsonify(session.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@squash_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session and all its matches"""
    try:
        session = Session.query.get_or_404(session_id)
        
        # First, revert ELO changes for all completed matches in this session
        completed_matches = Match.query.filter_by(session_id=session_id).filter(
            Match.player1_score.isnot(None),
            Match.player2_score.isnot(None)
        ).all()
        
        for match in completed_matches:
            if match.player1_elo_change is not None:
                match.player1.elo_rating -= match.player1_elo_change
            if match.player2_elo_change is not None:
                match.player2.elo_rating -= match.player2_elo_change
        
        # Delete all matches in the session
        Match.query.filter_by(session_id=session_id).delete()
        
        # Delete the session
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': 'Session and all matches deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

# Match endpoints
@squash_bp.route('/matches', methods=['POST'])
@validate_json_request()
def create_match(data):
    """Create a new match"""
    try:
        session_id = data.get('session_id')
        player1_id = data.get('player1_id')
        player2_id = data.get('player2_id')
        player1_score = data.get('player1_score')
        player2_score = data.get('player2_score')
        notes = data.get('notes', '').strip() if data.get('notes') else None
        
        # Validate required fields
        if not session_id or not player1_id or not player2_id:
            return jsonify({'error': 'session_id, player1_id, and player2_id are required'}), 400
        
        if player1_id == player2_id:
            return jsonify({'error': 'Players must be different'}), 400
        
        # Validate players exist
        player1 = Player.query.get(player1_id)
        player2 = Player.query.get(player2_id)
        if not player1 or not player2:
            return jsonify({'error': 'One or both players not found'}), 404
        
        # Validate session exists
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        match = Match(
            session_id=session_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player1_score=player1_score,
            player2_score=player2_score,
            notes=notes
        )
        
        # Update scores if provided
        if player1_score is not None and player2_score is not None:
            match.update_scores(player1_score, player2_score)
        
        db.session.add(match)
        db.session.commit()
        
        # Prepare response with ELO changes if match is completed
        response_data = match.to_dict()
        if match.player1_elo_change is not None and match.player2_elo_change is not None:
            response_data['elo_changes'] = {
                'player1': {
                    'name': match.player1.name,
                    'elo_before': match.player1_elo_before,
                    'elo_change': match.player1_elo_change,
                    'elo_after': match.player1.elo_rating
                },
                'player2': {
                    'name': match.player2.name,
                    'elo_before': match.player2_elo_before,
                    'elo_change': match.player2_elo_change,
                    'elo_after': match.player2.elo_rating
                }
            }
        
        return jsonify(response_data), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@squash_bp.route('/matches/<int:match_id>', methods=['PUT'])
@validate_json_request()
def update_match(match_id, data):
    """Update match scores and information"""
    try:
        match = Match.query.get_or_404(match_id)
        
        # Store original ELO ratings before update
        original_player1_elo = match.player1.elo_rating
        original_player2_elo = match.player2.elo_rating
        
        # If match was already completed, revert previous ELO changes
        if match.is_completed() and match.player1_elo_change is not None and match.player2_elo_change is not None:
            match.player1.elo_rating -= match.player1_elo_change
            match.player2.elo_rating -= match.player2_elo_change
        
        # Update scores if provided
        if 'player1_score' in data and 'player2_score' in data:
            player1_score = data['player1_score']
            player2_score = data['player2_score']
            
            # Validate scores are integers
            if not isinstance(player1_score, int) or not isinstance(player2_score, int):
                return jsonify({'error': 'Scores must be integers'}), 400
            
            # Validate score ranges
            if player1_score < 0 or player2_score < 0:
                return jsonify({'error': 'Scores cannot be negative'}), 400
            
            match.update_scores(player1_score, player2_score)
        
        # Update notes if provided
        if 'notes' in data:
            match.notes = data['notes'].strip() if data['notes'] else None
        
        db.session.commit()
        
        # Trigger backup after match completion (if backup scheduler is available)
        try:
            from flask import current_app
            backup_scheduler = current_app.config.get('BACKUP_SCHEDULER')
            if backup_scheduler:
                backup_scheduler.trigger_match_backup()
        except Exception as e:
            # Don't fail the request if backup fails
            print(f"Warning: Failed to trigger backup after match update: {e}")
        
        # Prepare response with ELO changes
        response_data = match.to_dict()
        
        # Add ELO change information for display
        if match.player1_elo_change is not None and match.player2_elo_change is not None:
            response_data['elo_changes'] = {
                'player1': {
                    'name': match.player1.name,
                    'elo_before': match.player1_elo_before,
                    'elo_change': match.player1_elo_change,
                    'elo_after': match.player1.elo_rating
                },
                'player2': {
                    'name': match.player2.name,
                    'elo_before': match.player2_elo_before,
                    'elo_change': match.player2_elo_change,
                    'elo_after': match.player2.elo_rating
                }
            }
        
        return jsonify(response_data)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

@squash_bp.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    """Delete a match and revert ELO changes"""
    try:
        match = Match.query.get_or_404(match_id)
        
        # Revert ELO changes if match was completed
        if match.is_completed() and match.player1_elo_change is not None and match.player2_elo_change is not None:
            match.player1.elo_rating -= match.player1_elo_change
            match.player2.elo_rating -= match.player2_elo_change
        
        db.session.delete(match)
        db.session.commit()
        return jsonify({'message': 'Match deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

# Leaderboard endpoint
@squash_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get player leaderboard with ELO ratings"""
    try:
        players = Player.query.filter_by(active=True).all()
        leaderboard = []
        
        for player in players:
            # Get all matches for this player
            all_matches = Match.query.filter(
                (Match.player1_id == player.id) | (Match.player2_id == player.id),
                Match.player1_score.isnot(None),
                Match.player2_score.isnot(None)
            ).all()
            
            if not all_matches:
                continue
            
            total_matches = len(all_matches)
            wins = len([m for m in all_matches if m.winner_id == player.id])
            losses = total_matches - wins
            win_rate = wins / total_matches if total_matches > 0 else 0
            
            # Calculate total points (3 for win, 1 for loss)
            total_points = wins * 3 + losses * 1
            points_per_match = total_points / total_matches if total_matches > 0 else 0
            
            leaderboard.append({
                'id': player.id,
                'name': player.name,
                'elo_rating': player.elo_rating,
                'matches_played': total_matches,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate * 100, 1),  # Convert to percentage
                'total_points': total_points,
                'points_per_match': round(points_per_match, 2)
            })
        
        # Sort by ELO rating (descending), then by points per match
        leaderboard.sort(key=lambda x: (x['elo_rating'], x['points_per_match']), reverse=True)
        
        return jsonify(leaderboard)
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error occurred'}), 500


# Highlight stats endpoint
@squash_bp.route('/highlights', methods=['GET'])
def get_highlights():
    """Get highlight stats from recent sessions with ELO changes"""
    try:
        # Get the most recent completed matches (last 10)
        recent_matches = Match.query.filter(
            Match.player1_score.isnot(None),
            Match.player2_score.isnot(None),
            Match.completed_at.isnot(None)
        ).order_by(Match.completed_at.desc()).limit(10).all()
        
        highlights = []
        for match in recent_matches:
            highlight = {
                'match_id': match.id,
                'session_id': match.session_id,
                'date': match.completed_at.strftime('%Y-%m-%d'),
                'player1_name': match.player1.name,
                'player2_name': match.player2.name,
                'player1_score': match.player1_score,
                'player2_score': match.player2_score,
                'winner_name': match.winner.name if match.winner else 'Tie',
                'player1_elo_before': match.player1_elo_before,
                'player2_elo_before': match.player2_elo_before,
                'player1_elo_change': match.player1_elo_change,
                'player2_elo_change': match.player2_elo_change,
                'player1_elo_after': (match.player1_elo_before or 0) + (match.player1_elo_change or 0),
                'player2_elo_after': (match.player2_elo_before or 0) + (match.player2_elo_change or 0)
            }
            highlights.append(highlight)
        
        # Get some summary stats
        total_matches_today = Match.query.filter(
            Match.completed_at >= datetime.utcnow().date(),
            Match.player1_score.isnot(None),
            Match.player2_score.isnot(None)
        ).count()
        
        # Get biggest ELO gains/losses from recent matches
        biggest_gain = None
        biggest_loss = None
        
        for match in recent_matches:
            if match.player1_elo_change and match.player2_elo_change:
                if biggest_gain is None or match.player1_elo_change > biggest_gain['elo_change']:
                    biggest_gain = {
                        'player_name': match.player1.name,
                        'elo_change': match.player1_elo_change,
                        'opponent': match.player2.name,
                        'score': f"{match.player1_score}-{match.player2_score}"
                    }
                if biggest_gain is None or match.player2_elo_change > biggest_gain['elo_change']:
                    biggest_gain = {
                        'player_name': match.player2.name,
                        'elo_change': match.player2_elo_change,
                        'opponent': match.player1.name,
                        'score': f"{match.player2_score}-{match.player1_score}"
                    }
                
                if biggest_loss is None or match.player1_elo_change < biggest_loss['elo_change']:
                    biggest_loss = {
                        'player_name': match.player1.name,
                        'elo_change': match.player1_elo_change,
                        'opponent': match.player2.name,
                        'score': f"{match.player1_score}-{match.player2_score}"
                    }
                if biggest_loss is None or match.player2_elo_change < biggest_loss['elo_change']:
                    biggest_loss = {
                        'player_name': match.player2.name,
                        'elo_change': match.player2_elo_change,
                        'opponent': match.player1.name,
                        'score': f"{match.player2_score}-{match.player1_score}"
                    }
        
        return jsonify({
            'recent_matches': highlights,
            'stats': {
                'matches_today': total_matches_today,
                'biggest_elo_gain': biggest_gain,
                'biggest_elo_loss': biggest_loss
            }
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error occurred'}), 500

