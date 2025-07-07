import os
import shutil
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

class DatabaseManager:
    """Manages database persistence, backups, and recovery"""
    
    def __init__(self, app_config):
        self.app_config = app_config
        self.db_path = self._get_persistent_db_path()
        self.backup_dir = self._get_backup_directory()
        self.logger = self._setup_logging()
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _get_persistent_db_path(self):
        """Get the path for persistent database storage"""
        # Use environment variable if set, otherwise use a persistent location
        # that survives deployments in the Manus platform
        persistent_dir = os.environ.get('PERSISTENT_DATA_DIR')
        
        if not persistent_dir:
            # For Manus deployments, use /data which persists across deployments
            # Fall back to /var/lib/squash_data for other environments
            if os.path.exists('/data'):
                persistent_dir = '/data/squash_data'
            else:
                persistent_dir = '/var/lib/squash_data'
        
        os.makedirs(persistent_dir, exist_ok=True)
        return os.path.join(persistent_dir, 'squash_tracker.db')
    
    def _get_backup_directory(self):
        """Get the backup directory path"""
        persistent_dir = os.environ.get('PERSISTENT_DATA_DIR')
        
        if not persistent_dir:
            # For Manus deployments, use /data which persists across deployments
            # Fall back to /var/lib/squash_data for other environments
            if os.path.exists('/data'):
                persistent_dir = '/data/squash_data'
            else:
                persistent_dir = '/var/lib/squash_data'
        
        return os.path.join(persistent_dir, 'backups')
    
    def _setup_logging(self):
        """Setup logging for database operations"""
        logger = logging.getLogger('database_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_database_uri(self):
        """Get the database URI for SQLAlchemy"""
        return f"sqlite:///{self.db_path}"
    
    def create_backup(self, backup_name=None):
        """Create a backup of the current database"""
        if not os.path.exists(self.db_path):
            self.logger.warning("Database file does not exist, cannot create backup")
            return None
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"squash_backup_{timestamp}.db"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backup created: {backup_path}")
            
            # Also create a JSON export for additional safety
            json_backup_path = backup_path.replace('.db', '.json')
            self._export_to_json(json_backup_path)
            
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def _export_to_json(self, json_path):
        """Export database to JSON format for additional backup safety"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            data = {}
            
            # Export all tables
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                data[table] = [dict(row) for row in rows]
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"JSON backup created: {json_path}")
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to create JSON backup: {e}")
    
    def restore_from_backup(self, backup_path):
        """Restore database from a backup file"""
        if not os.path.exists(backup_path):
            self.logger.error(f"Backup file does not exist: {backup_path}")
            return False
        
        try:
            # Create a backup of current database before restoring
            if os.path.exists(self.db_path):
                current_backup = self.create_backup("pre_restore_backup")
                self.logger.info(f"Current database backed up to: {current_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            self.logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def auto_backup(self, max_backups=10):
        """Create automatic backup and clean up old backups"""
        backup_path = self.create_backup()
        
        if backup_path:
            # Clean up old backups
            self._cleanup_old_backups(max_backups)
        
        return backup_path
    
    def _cleanup_old_backups(self, max_backups):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('squash_backup_') and file.endswith('.db'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for file_path, _ in backup_files[max_backups:]:
                os.remove(file_path)
                # Also remove corresponding JSON file
                json_file = file_path.replace('.db', '.json')
                if os.path.exists(json_file):
                    os.remove(json_file)
                self.logger.info(f"Removed old backup: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    def get_backup_info(self):
        """Get information about available backups"""
        backups = []
        
        try:
            for file in os.listdir(self.backup_dir):
                if file.startswith('squash_backup_') and file.endswith('.db'):
                    file_path = os.path.join(self.backup_dir, file)
                    stat = os.stat(file_path)
                    backups.append({
                        'filename': file,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to get backup info: {e}")
        
        return backups
    
    def verify_database_integrity(self):
        """Verify database integrity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == "ok":
                self.logger.info("Database integrity check passed")
                return True
            else:
                self.logger.error(f"Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to verify database integrity: {e}")
            return False
    
    def migrate_existing_database(self, old_db_path):
        """Migrate data from an existing database to the persistent location"""
        if not os.path.exists(old_db_path):
            self.logger.info("No existing database to migrate")
            return True
        
        try:
            # If persistent database doesn't exist, copy the old one
            if not os.path.exists(self.db_path):
                shutil.copy2(old_db_path, self.db_path)
                self.logger.info(f"Migrated database from {old_db_path} to {self.db_path}")
                
                # Create initial backup after migration
                self.create_backup("initial_migration_backup")
                return True
            else:
                self.logger.info("Persistent database already exists, no migration needed")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to migrate database: {e}")
            return False

