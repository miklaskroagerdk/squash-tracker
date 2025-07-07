import os
import shutil
import json
import sqlite3
from datetime import datetime
import logging

class DeploymentSafety:
    """Ensures data persistence across deployments with multiple safeguards"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger('deployment_safety')
        
        # Multiple backup locations for redundancy
        self.backup_locations = [
            '/data/squash_backups',
            '/var/lib/squash_backups', 
            '/tmp/squash_emergency_backups'
        ]
        
        # Ensure all backup locations exist
        for location in self.backup_locations:
            try:
                os.makedirs(location, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"Could not create backup location {location}: {e}")
    
    def create_deployment_backup(self):
        """Create backups in multiple locations before deployment"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_deployment_backup_{timestamp}"
        
        successful_backups = []
        
        for location in self.backup_locations:
            try:
                if not os.path.exists(location):
                    continue
                    
                # Create SQLite backup
                db_backup_path = os.path.join(location, f"{backup_name}.db")
                if os.path.exists(self.db_manager.db_path):
                    shutil.copy2(self.db_manager.db_path, db_backup_path)
                    
                    # Create JSON backup for additional safety
                    json_backup_path = os.path.join(location, f"{backup_name}.json")
                    self._export_to_json(json_backup_path)
                    
                    # Create metadata file
                    metadata_path = os.path.join(location, f"{backup_name}_metadata.json")
                    metadata = {
                        'timestamp': timestamp,
                        'original_db_path': self.db_manager.db_path,
                        'backup_type': 'pre_deployment',
                        'db_size': os.path.getsize(self.db_manager.db_path),
                        'created_at': datetime.now().isoformat()
                    }
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    successful_backups.append(location)
                    self.logger.info(f"Deployment backup created at {location}")
                    
            except Exception as e:
                self.logger.error(f"Failed to create backup at {location}: {e}")
        
        return successful_backups
    
    def _export_to_json(self, json_path):
        """Export database to JSON format"""
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
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to create JSON backup: {e}")
    
    def find_latest_backup(self):
        """Find the most recent backup across all locations"""
        latest_backup = None
        latest_time = None
        
        for location in self.backup_locations:
            try:
                if not os.path.exists(location):
                    continue
                    
                for file in os.listdir(location):
                    if file.endswith('_metadata.json'):
                        metadata_path = os.path.join(location, file)
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            
                            backup_time = datetime.fromisoformat(metadata['created_at'])
                            if latest_time is None or backup_time > latest_time:
                                latest_time = backup_time
                                backup_name = file.replace('_metadata.json', '')
                                latest_backup = {
                                    'location': location,
                                    'name': backup_name,
                                    'metadata': metadata,
                                    'db_path': os.path.join(location, f"{backup_name}.db"),
                                    'json_path': os.path.join(location, f"{backup_name}.json")
                                }
                        except Exception as e:
                            self.logger.warning(f"Could not read metadata from {metadata_path}: {e}")
                            
            except Exception as e:
                self.logger.warning(f"Could not scan backup location {location}: {e}")
        
        return latest_backup
    
    def restore_from_backup(self, backup_info=None):
        """Restore database from backup"""
        if backup_info is None:
            backup_info = self.find_latest_backup()
        
        if backup_info is None:
            self.logger.error("No backup found for restoration")
            return False
        
        try:
            # Create backup of current database before restoring
            if os.path.exists(self.db_manager.db_path):
                current_backup = f"{self.db_manager.db_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.db_manager.db_path, current_backup)
                self.logger.info(f"Current database backed up to {current_backup}")
            
            # Restore from backup
            if os.path.exists(backup_info['db_path']):
                # Ensure target directory exists
                os.makedirs(os.path.dirname(self.db_manager.db_path), exist_ok=True)
                
                shutil.copy2(backup_info['db_path'], self.db_manager.db_path)
                self.logger.info(f"Database restored from {backup_info['db_path']}")
                return True
            else:
                self.logger.error(f"Backup file not found: {backup_info['db_path']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def verify_data_integrity_after_deployment(self):
        """Verify that data exists and is intact after deployment"""
        try:
            if not os.path.exists(self.db_manager.db_path):
                self.logger.error("Database file does not exist after deployment")
                return False
            
            # Check if database is readable
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                self.logger.warning("Database exists but has no tables")
                conn.close()
                return False
            
            # Check if we have data in key tables
            has_data = False
            for table in ['players', 'sessions', 'matches']:
                if table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        has_data = True
                        self.logger.info(f"Table {table} has {count} records")
            
            conn.close()
            
            if not has_data:
                self.logger.warning("Database exists but appears to be empty")
                return False
            
            self.logger.info("Data integrity verification passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Data integrity verification failed: {e}")
            return False
    
    def auto_recovery_if_needed(self):
        """Automatically recover data if database is missing or empty"""
        if not self.verify_data_integrity_after_deployment():
            self.logger.warning("Data integrity check failed, attempting auto-recovery")
            
            latest_backup = self.find_latest_backup()
            if latest_backup:
                self.logger.info(f"Found backup from {latest_backup['metadata']['created_at']}")
                if self.restore_from_backup(latest_backup):
                    self.logger.info("Auto-recovery successful")
                    return True
                else:
                    self.logger.error("Auto-recovery failed")
                    return False
            else:
                self.logger.error("No backup found for auto-recovery")
                return False
        else:
            self.logger.info("Data integrity check passed, no recovery needed")
            return True
    
    def get_backup_status(self):
        """Get comprehensive backup status"""
        status = {
            'backup_locations': [],
            'latest_backup': None,
            'total_backups': 0
        }
        
        for location in self.backup_locations:
            location_info = {
                'path': location,
                'exists': os.path.exists(location),
                'backup_count': 0,
                'total_size_mb': 0
            }
            
            if location_info['exists']:
                try:
                    files = os.listdir(location)
                    backup_files = [f for f in files if f.endswith('.db') and 'backup' in f]
                    location_info['backup_count'] = len(backup_files)
                    
                    total_size = 0
                    for file in backup_files:
                        file_path = os.path.join(location, file)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                    
                    location_info['total_size_mb'] = round(total_size / (1024 * 1024), 2)
                    status['total_backups'] += location_info['backup_count']
                    
                except Exception as e:
                    location_info['error'] = str(e)
            
            status['backup_locations'].append(location_info)
        
        status['latest_backup'] = self.find_latest_backup()
        
        return status

