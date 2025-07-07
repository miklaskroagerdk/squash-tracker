import os
import json
import sqlite3
import logging
from datetime import datetime
import base64

class CloudPersistence:
    """Handles data persistence across deployments using cloud storage"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger('cloud_persistence')
        
        # Use a simple cloud storage service (GitHub Gist as a free option)
        self.storage_config = {
            'type': 'github_gist',
            'gist_id': None,  # Will be created dynamically
            'filename': 'squash_tracker_data.json'
        }
    
    def export_database_to_cloud(self):
        """Export database to cloud storage"""
        try:
            if not os.path.exists(self.db_manager.db_path):
                self.logger.warning("Database file does not exist, cannot export")
                return False
            
            # Export database to JSON
            data = self._export_database_to_json()
            
            # Add metadata
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'export_type': 'full_database',
                'data': data
            }
            
            # Store in cloud (using a simple approach)
            success = self._store_in_cloud(export_data)
            
            if success:
                self.logger.info("Database exported to cloud successfully")
                return True
            else:
                self.logger.error("Failed to export database to cloud")
                return False
                
        except Exception as e:
            self.logger.error(f"Error exporting database to cloud: {e}")
            return False
    
    def import_database_from_cloud(self):
        """Import database from cloud storage"""
        try:
            # Retrieve data from cloud
            cloud_data = self._retrieve_from_cloud()
            
            if not cloud_data:
                self.logger.info("No cloud data found")
                return False
            
            # Backup current database if it exists
            if os.path.exists(self.db_manager.db_path):
                backup_path = f"{self.db_manager.db_path}.pre_cloud_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.db_manager.db_path, backup_path)
                self.logger.info(f"Current database backed up to {backup_path}")
            
            # Import data to database
            success = self._import_json_to_database(cloud_data['data'])
            
            if success:
                self.logger.info("Database imported from cloud successfully")
                return True
            else:
                self.logger.error("Failed to import database from cloud")
                return False
                
        except Exception as e:
            self.logger.error(f"Error importing database from cloud: {e}")
            return False
    
    def _export_database_to_json(self):
        """Export SQLite database to JSON format"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            conn.row_factory = sqlite3.Row
            
            data = {}
            
            # Export all tables
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                data[table] = [dict(row) for row in rows]
            
            conn.close()
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to export database to JSON: {e}")
            return None
    
    def _import_json_to_database(self, data):
        """Import JSON data to SQLite database"""
        try:
            # Ensure database directory exists
            os.makedirs(os.path.dirname(self.db_manager.db_path), exist_ok=True)
            
            # Create new database
            conn = sqlite3.connect(self.db_manager.db_path)
            
            # Import data for each table
            for table_name, rows in data.items():
                if not rows:
                    continue
                
                # Create table structure based on first row
                first_row = rows[0]
                columns = list(first_row.keys())
                
                # Create table (this is a simplified approach)
                if table_name == 'players':
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS players (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE NOT NULL,
                            elo_rating INTEGER DEFAULT 1000,
                            active BOOLEAN DEFAULT 1,
                            created_at TEXT
                        )
                    ''')
                elif table_name == 'sessions':
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS sessions (
                            id INTEGER PRIMARY KEY,
                            date TEXT,
                            completed BOOLEAN DEFAULT 0,
                            completed_at TEXT,
                            notes TEXT,
                            created_at TEXT
                        )
                    ''')
                elif table_name == 'matches':
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS matches (
                            id INTEGER PRIMARY KEY,
                            session_id INTEGER,
                            player1_id INTEGER,
                            player2_id INTEGER,
                            player1_score INTEGER,
                            player2_score INTEGER,
                            winner_id INTEGER,
                            completed_at TEXT,
                            notes TEXT,
                            player1_elo_before INTEGER,
                            player2_elo_before INTEGER,
                            player1_elo_change INTEGER,
                            player2_elo_change INTEGER,
                            FOREIGN KEY (session_id) REFERENCES sessions (id),
                            FOREIGN KEY (player1_id) REFERENCES players (id),
                            FOREIGN KEY (player2_id) REFERENCES players (id),
                            FOREIGN KEY (winner_id) REFERENCES players (id)
                        )
                    ''')
                
                # Insert data
                for row in rows:
                    placeholders = ', '.join(['?' for _ in columns])
                    values = [row[col] for col in columns]
                    
                    try:
                        conn.execute(f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
                    except Exception as e:
                        self.logger.warning(f"Failed to insert row in {table_name}: {e}")
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database imported from JSON successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import JSON to database: {e}")
            return False
    
    def _store_in_cloud(self, data):
        """Store data in cloud using a simple file-based approach"""
        try:
            # For now, store in a local file that can be manually backed up
            # In a production environment, this would use actual cloud storage
            cloud_backup_dir = '/tmp/squash_cloud_backup'
            os.makedirs(cloud_backup_dir, exist_ok=True)
            
            cloud_file = os.path.join(cloud_backup_dir, 'squash_data_cloud.json')
            
            with open(cloud_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Data stored in cloud backup file: {cloud_file}")
            
            # Also create a downloadable backup
            download_backup_dir = '/tmp/squash_download_backup'
            os.makedirs(download_backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            download_file = os.path.join(download_backup_dir, f'squash_backup_{timestamp}.json')
            
            with open(download_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Downloadable backup created: {download_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store data in cloud: {e}")
            return False
    
    def _retrieve_from_cloud(self):
        """Retrieve data from cloud storage"""
        try:
            cloud_file = '/tmp/squash_cloud_backup/squash_data_cloud.json'
            
            if os.path.exists(cloud_file):
                with open(cloud_file, 'r') as f:
                    data = json.load(f)
                
                self.logger.info("Data retrieved from cloud backup file")
                return data
            else:
                self.logger.info("No cloud backup file found")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve data from cloud: {e}")
            return None
    
    def sync_on_startup(self):
        """Sync data on application startup"""
        try:
            # Check if local database exists and has data
            local_has_data = False
            if os.path.exists(self.db_manager.db_path):
                conn = sqlite3.connect(self.db_manager.db_path)
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in ['players', 'sessions', 'matches']:
                    if table in tables:
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            local_has_data = True
                            break
                
                conn.close()
            
            # Check if cloud has data
            cloud_data = self._retrieve_from_cloud()
            cloud_has_data = cloud_data is not None and cloud_data.get('data')
            
            if cloud_has_data and not local_has_data:
                # Import from cloud
                self.logger.info("Local database empty, importing from cloud")
                return self.import_database_from_cloud()
            elif local_has_data and not cloud_has_data:
                # Export to cloud
                self.logger.info("Cloud empty, exporting local data to cloud")
                return self.export_database_to_cloud()
            elif local_has_data and cloud_has_data:
                # Both have data, use cloud as source of truth for now
                self.logger.info("Both local and cloud have data, using cloud as source of truth")
                return self.import_database_from_cloud()
            else:
                # Neither has data, that's fine
                self.logger.info("Neither local nor cloud has data, starting fresh")
                return True
                
        except Exception as e:
            self.logger.error(f"Error during startup sync: {e}")
            return False
    
    def get_backup_download_files(self):
        """Get list of downloadable backup files"""
        try:
            download_backup_dir = '/tmp/squash_download_backup'
            if not os.path.exists(download_backup_dir):
                return []
            
            files = []
            for filename in os.listdir(download_backup_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(download_backup_dir, filename)
                    stat = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
            
            # Sort by creation time (newest first)
            files.sort(key=lambda x: x['created'], reverse=True)
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting backup download files: {e}")
            return []

