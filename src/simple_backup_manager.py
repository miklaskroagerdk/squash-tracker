import os
import shutil
import logging
from datetime import datetime

class SimpleBackupManager:
    """Simplified backup manager for external database"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.backup_dir = '/tmp/external_squash_data/backups'
        self.logger = logging.getLogger('simple_backup_manager')
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Create a backup of the database"""
        try:
            if not os.path.exists(self.db_path):
                self.logger.warning(f"Database file does not exist: {self.db_path}")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"squash_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(self.db_path, backup_path)
            
            backup_info = {
                'filename': backup_filename,
                'path': backup_path,
                'size': os.path.getsize(backup_path),
                'created': datetime.now().isoformat(),
                'modified': datetime.fromtimestamp(os.path.getmtime(backup_path)).isoformat()
            }
            
            self.logger.info(f"Backup created: {backup_path}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def get_backup_info(self):
        """Get information about existing backups"""
        try:
            if not os.path.exists(self.backup_dir):
                return []
            
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.db') and 'backup' in filename:
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"Error getting backup info: {e}")
            return []
    
    def get_database_uri(self):
        """Get database URI for SQLAlchemy"""
        return f"sqlite:///{self.db_path}"

