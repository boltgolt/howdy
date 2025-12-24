"""
Configuration manager for Howdy GUI Manager
Handles reading and writing Howdy config.ini file
"""

import configparser
import os
import shutil
from datetime import datetime
from typing import Any, Optional


class ConfigManager:
    """Manages Howdy configuration file operations"""
    
    def __init__(self, config_path: str = "/etc/howdy/config.ini"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                self.config.read(self.config_path)
                return True
            return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            # Create backup first
            self.create_backup()
            
            # Write configuration
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def create_backup(self) -> Optional[str]:
        """Create a backup of the current config file"""
        try:
            if os.path.exists(self.config_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.config_path}.backup_{timestamp}"
                shutil.copy2(self.config_path, backup_path)
                return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
        return None
    
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """Get a configuration value"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def get_int(self, section: str, option: str, fallback: int = 0) -> int:
        """Get an integer configuration value"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_float(self, section: str, option: str, fallback: float = 0.0) -> float:
        """Get a float configuration value"""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def get_boolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """Get a boolean configuration value"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, option: str, value: Any) -> bool:
        """Set a configuration value"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, option, str(value))
            return True
        except Exception as e:
            print(f"Error setting config value: {e}")
            return False
    
    def get_all_sections(self) -> list:
        """Get all configuration sections"""
        return self.config.sections()
    
    def get_section_options(self, section: str) -> dict:
        """Get all options in a section as a dictionary"""
        try:
            return dict(self.config.items(section))
        except configparser.NoSectionError:
            return {}
