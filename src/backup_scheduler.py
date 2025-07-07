import threading
import time
import schedule
from datetime import datetime, timedelta
import logging

class BackupScheduler:
    """Handles automated database backups on a schedule"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger('backup_scheduler')
        self.scheduler_thread = None
        self.running = False
        
        # Configure backup schedule
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup the backup schedule"""
        # Daily backup at 2 AM
        schedule.every().day.at("02:00").do(self._daily_backup)
        
        # Weekly backup on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self._weekly_backup)
        
        # Backup after every 10 matches (handled separately)
        self.match_counter = 0
        self.matches_per_backup = 10
    
    def _daily_backup(self):
        """Create daily backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d")
            backup_name = f"daily_backup_{timestamp}.db"
            backup_path = self.db_manager.create_backup(backup_name)
            
            if backup_path:
                self.logger.info(f"Daily backup created: {backup_path}")
            else:
                self.logger.error("Failed to create daily backup")
                
        except Exception as e:
            self.logger.error(f"Error during daily backup: {e}")
    
    def _weekly_backup(self):
        """Create weekly backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d")
            backup_name = f"weekly_backup_{timestamp}.db"
            backup_path = self.db_manager.create_backup(backup_name)
            
            if backup_path:
                self.logger.info(f"Weekly backup created: {backup_path}")
                
                # Keep weekly backups longer (clean up after 8 weeks)
                self._cleanup_weekly_backups(max_weeks=8)
            else:
                self.logger.error("Failed to create weekly backup")
                
        except Exception as e:
            self.logger.error(f"Error during weekly backup: {e}")
    
    def _cleanup_weekly_backups(self, max_weeks=8):
        """Clean up old weekly backups"""
        try:
            import os
            backup_dir = self.db_manager.backup_dir
            cutoff_date = datetime.now() - timedelta(weeks=max_weeks)
            
            for file in os.listdir(backup_dir):
                if file.startswith('weekly_backup_') and file.endswith('.db'):
                    file_path = os.path.join(backup_dir, file)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        # Also remove JSON backup
                        json_file = file_path.replace('.db', '.json')
                        if os.path.exists(json_file):
                            os.remove(json_file)
                        self.logger.info(f"Removed old weekly backup: {file}")
                        
        except Exception as e:
            self.logger.error(f"Error cleaning up weekly backups: {e}")
    
    def trigger_match_backup(self):
        """Trigger backup after match completion"""
        self.match_counter += 1
        
        if self.match_counter >= self.matches_per_backup:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"match_milestone_{timestamp}.db"
                backup_path = self.db_manager.create_backup(backup_name)
                
                if backup_path:
                    self.logger.info(f"Match milestone backup created: {backup_path}")
                    self.match_counter = 0  # Reset counter
                    
            except Exception as e:
                self.logger.error(f"Error during match milestone backup: {e}")
    
    def start(self):
        """Start the backup scheduler"""
        if self.running:
            self.logger.warning("Backup scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Backup scheduler started")
    
    def stop(self):
        """Stop the backup scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Backup scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in backup scheduler: {e}")
                time.sleep(60)  # Continue running even if there's an error
    
    def get_next_backup_times(self):
        """Get information about next scheduled backups"""
        jobs = schedule.jobs
        next_runs = []
        
        for job in jobs:
            next_runs.append({
                'job': str(job.job_func.__name__),
                'next_run': job.next_run.isoformat() if job.next_run else None
            })
        
        return next_runs
    
    def force_backup(self, backup_type="manual"):
        """Force an immediate backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{backup_type}_backup_{timestamp}.db"
            backup_path = self.db_manager.create_backup(backup_name)
            
            if backup_path:
                self.logger.info(f"Manual backup created: {backup_path}")
                return backup_path
            else:
                self.logger.error("Failed to create manual backup")
                return None
                
        except Exception as e:
            self.logger.error(f"Error during manual backup: {e}")
            return None

