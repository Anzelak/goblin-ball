import os
import datetime
from config import CONFIG

# Setup debug logging
class DebugLogger:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.log_file = None
        if enabled:
            # Create logs directory if it doesn't exist
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(script_dir, "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create a new log file with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = os.path.join(log_dir, f"goblinball_debug_{timestamp}.txt")
            self.log_file = open(log_path, "w")
            self.log(f"=== Goblinball Debug Log - {timestamp} ===")
            self.log(f"Log file path: {log_path}")
    
    def log(self, message, level="INFO"):
        """Write a message to the debug log"""
        if not self.enabled or not self.log_file:
            return
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Write to file and flush immediately
        self.log_file.write(log_message + "\n")
        self.log_file.flush()
        
        # Echo to console if in verbose mode
        if CONFIG.get("verbose_debug", False):
            print(log_message)
    
    def close(self):
        """Close the log file"""
        if self.log_file:
            self.log_file.close()

# Create global debug logger
DEBUG = DebugLogger(CONFIG.get("debug_logging", True)) 