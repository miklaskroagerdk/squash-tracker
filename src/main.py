import os
import sys
# DON'T CHANGE THIS LINE - it's needed for deployment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from models.squash import init_database
from routes.squash import squash_bp
from simple_backup_manager import SimpleBackupManager
from external_database import ExternalDatabaseManager
import logging
from datetime import datetime
import atexit

# Create Flask app
app = Flask(__name__, static_folder='static')

# Enable CORS for all routes
CORS(app)

# Initialize external database manager
external_db = ExternalDatabaseManager()

# Test database connection
if not external_db.test_connection():
    print("Warning: Database connection test failed")

# Sync with external storage on startup
external_db.sync_with_external_storage()

# Get database path for backup manager
db_uri = external_db.get_database_uri()
if 'sqlite:///' in db_uri:
    db_path = db_uri.replace('sqlite:///', '')
else:
    db_path = '/tmp/external_squash_data/squash_tracker.db'

# Ensure database directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Initialize simple backup manager
backup_manager = SimpleBackupManager(db_path)

# Override database URI with external database
app.config['SQLALCHEMY_DATABASE_URI'] = external_db.get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Using external database: {external_db.get_database_uri()}")

# Store managers in app config for access in routes
app.config['EXTERNAL_DB'] = external_db
app.config['BACKUP_MANAGER'] = backup_manager

# Register squash tracker blueprint
app.register_blueprint(squash_bp)

# Initialize database
init_database(app)

# Admin endpoints for external database management
@app.route('/api/admin/database/status', methods=['GET'])
def get_database_status():
    """Get database and backup status"""
    try:
        external_db = app.config['EXTERNAL_DB']
        backup_manager = app.config['BACKUP_MANAGER']
        
        # Test database connection
        connection_ok = external_db.test_connection()
        
        # Get database file info
        db_uri = external_db.get_database_uri()
        if 'sqlite:///' in db_uri:
            db_path = db_uri.replace('sqlite:///', '')
            db_exists = os.path.exists(db_path)
            db_size = os.path.getsize(db_path) if db_exists else 0
        else:
            db_exists = connection_ok
            db_size = 0
        
        # Get backup info
        backups = backup_manager.get_backup_info()
        
        return jsonify({
            'success': True,
            'database': {
                'uri': db_uri,
                'exists': db_exists,
                'size': db_size,
                'connection_ok': connection_ok
            },
            'backups': {
                'count': len(backups),
                'latest': backups[0] if backups else None,
                'total_size': sum(b['size'] for b in backups)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting database status: {str(e)}'
        }), 500

@app.route('/api/admin/backup/create', methods=['POST'])
def create_backup():
    """Create a manual backup"""
    try:
        backup_manager = app.config['BACKUP_MANAGER']
        backup_info = backup_manager.create_backup()
        
        if backup_info:
            return jsonify({
                'success': True,
                'backup': backup_info,
                'message': 'Backup created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create backup'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating backup: {str(e)}'
        }), 500

@app.route('/api/admin/backups', methods=['GET'])
def list_backups():
    """List all available backups"""
    try:
        backup_manager = app.config['BACKUP_MANAGER']
        backups = backup_manager.get_backup_info()
        
        return jsonify({
            'success': True,
            'backups': backups,
            'count': len(backups)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing backups: {str(e)}'
        }), 500

@app.route('/api/admin/external/sync', methods=['POST'])
def sync_external_storage():
    """Sync with external storage"""
    try:
        external_db = app.config['EXTERNAL_DB']
        success = external_db.sync_with_external_storage()
        
        return jsonify({
            'success': success,
            'message': 'External storage sync completed' if success else 'External storage sync failed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error syncing external storage: {str(e)}'
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        return send_from_directory(static_folder_path, 'index.html')

# Create a backup on startup
try:
    backup_manager.create_backup()
    print("Startup backup created successfully")
except Exception as e:
    print(f"Failed to create startup backup: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

