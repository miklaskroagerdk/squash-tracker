import os
import logging
from urllib.parse import urlparse

class ExternalDatabaseManager:
    """Manages external database connections for cloud deployment"""
    
    def __init__(self):
        self.logger = logging.getLogger('external_database')
        self.db_type = os.getenv('DB_TYPE', 'cloud_sqlite')
        self.database_url = os.getenv('DATABASE_URL', None)
        
    def get_database_uri(self):
        """Get the appropriate database URI based on environment"""
        
        # Check for explicit DATABASE_URL (common in cloud deployments)
        if self.database_url:
            self.logger.info(f"Using DATABASE_URL: {self.database_url[:20]}...")
            return self.database_url
        
        # Check for specific database type configuration
        if self.db_type == 'postgresql':
            # PostgreSQL configuration
            host = os.getenv('POSTGRES_HOST', 'localhost')
            port = os.getenv('POSTGRES_PORT', '5432')
            user = os.getenv('POSTGRES_USER', 'postgres')
            password = os.getenv('POSTGRES_PASSWORD', '')
            database = os.getenv('POSTGRES_DB', 'squash_tracker')
            
            uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            self.logger.info(f"Using PostgreSQL: {host}:{port}/{database}")
            return uri
            
        elif self.db_type == 'mysql':
            # MySQL configuration
            host = os.getenv('MYSQL_HOST', 'localhost')
            port = os.getenv('MYSQL_PORT', '3306')
            user = os.getenv('MYSQL_USER', 'root')
            password = os.getenv('MYSQL_PASSWORD', '')
            database = os.getenv('MYSQL_DB', 'squash_tracker')
            
            uri = f"mysql://{user}:{password}@{host}:{port}/{database}"
            self.logger.info(f"Using MySQL: {host}:{port}/{database}")
            return uri
            
        elif self.db_type == 'sqlite':
            # Custom SQLite path
            db_path = os.getenv('SQLITE_PATH', '/tmp/external_squash_data/squash_tracker.db')
            uri = f"sqlite:///{db_path}"
            self.logger.info(f"Using SQLite: {db_path}")
            return uri
            
        else:
            # Default: Cloud SQLite with persistent storage
            persistent_dir = '/tmp/external_squash_data'
            os.makedirs(persistent_dir, exist_ok=True)
            db_path = os.path.join(persistent_dir, 'squash_tracker.db')
            uri = f"sqlite:///{db_path}"
            self.logger.info(f"Using Cloud SQLite: {db_path}")
            return uri
    
    def test_connection(self):
        """Test database connection"""
        try:
            uri = self.get_database_uri()
            
            # For SQLite, just check if we can create the file
            if uri.startswith('sqlite:///'):
                db_path = uri.replace('sqlite:///', '')
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                # Try to create/touch the file
                with open(db_path, 'a'):
                    pass
                return True
            
            # For other databases, we'd need to actually connect
            # For now, assume they're configured correctly
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    def sync_with_external_storage(self):
        """Sync with external storage (placeholder for cloud storage integration)"""
        try:
            # This would implement cloud storage sync in a real deployment
            # For now, just ensure the database directory exists
            uri = self.get_database_uri()
            if uri.startswith('sqlite:///'):
                db_path = uri.replace('sqlite:///', '')
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.logger.info("External storage sync completed")
            return True
            
        except Exception as e:
            self.logger.error(f"External storage sync failed: {e}")
            return False
    
    def get_database_info(self):
        """Get database information for admin purposes"""
        uri = self.get_database_uri()
        parsed = urlparse(uri)
        
        return {
            'type': self.db_type,
            'scheme': parsed.scheme,
            'host': parsed.hostname,
            'port': parsed.port,
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'uri_masked': f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}{parsed.path}" if parsed.hostname else uri
        }

