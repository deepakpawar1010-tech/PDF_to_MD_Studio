"""
PDF_to_MD_Studio v1.0 - Configuration Manager
============================================
Handles application configuration, settings persistence,
and environment-based configuration loading.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from core.constants import (
    BASE_DIR,
    DEFAULT_SETTINGS,
    LOGS_DIR,
    MARKER_EXECUTABLE,
    OUTPUT_DIR,
    TEMP_DIR,
)


class ConfigManager:
    """
    Singleton configuration manager for the application.
    Handles loading, saving, and accessing user settings.
    """
    
    _instance: Optional["ConfigManager"] = None
    _config_file: Path = BASE_DIR / "config.json"
    
    def __new__(cls) -> "ConfigManager":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize configuration if not already done."""
        if self._initialized:
            return
        
        self._settings: Dict[str, Any] = {}
        self._load_config()
        self._initialized = True
    
    def _load_config(self) -> None:
        """
        Load configuration from file or create defaults.
        Merges saved settings with default settings.
        """
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                self._settings = {**DEFAULT_SETTINGS, **saved_settings}
            except (json.JSONDecodeError, IOError) as e:
                # If file is corrupted, use defaults and log issue
                self._settings = DEFAULT_SETTINGS.copy()
                self._save_config()
        else:
            # First run - create default config
            self._settings = DEFAULT_SETTINGS.copy()
            self._save_config()
    
    def _save_config(self) -> None:
        """Persist current settings to config file."""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            # If we can't write config, continue with in-memory settings
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Setting key to retrieve
            default: Fallback value if key doesn't exist
            
        Returns:
            The configuration value
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and persist to disk.
        
        Args:
            key: Setting key to update
            value: New value for the setting
        """
        self._settings[key] = value
        self._save_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple settings at once.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self._settings.update(updates)
        self._save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to application defaults."""
        self._settings = DEFAULT_SETTINGS.copy()
        self._save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all current settings.
        
        Returns:
            Dictionary of all configuration values
        """
        return self._settings.copy()
    
    def get_marker_path(self) -> str:
        """
        Get the path to the marker executable.
        Checks environment variable first, then PATH.
        
        Returns:
            Path to marker_single.exe
        """
        # Check for environment variable override
        env_path = os.environ.get("MARKER_PATH")
        if env_path and Path(env_path).exists():
            return env_path
        
        # Check if marker_single.exe is in PATH
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            marker_path = Path(path_dir) / MARKER_EXECUTABLE
            if marker_path.exists():
                return str(marker_path)
        
        # Return default name and let the system resolve it
        return MARKER_EXECUTABLE
    
    def get_output_dir(self) -> Path:
        """
        Get the configured output directory.
        
        Returns:
            Path object for output directory
        """
        custom_dir = self.get("custom_output_dir")
        if custom_dir and Path(custom_dir).exists():
            return Path(custom_dir)
        return OUTPUT_DIR
    
    def get_temp_dir(self) -> Path:
        """
        Get the configured temporary directory.
        
        Returns:
            Path object for temp directory
        """
        custom_dir = self.get("custom_temp_dir")
        if custom_dir and Path(custom_dir).exists():
            return Path(custom_dir)
        return TEMP_DIR
    
    def get_log_dir(self) -> Path:
        """
        Get the configured logs directory.
        
        Returns:
            Path object for logs directory
        """
        custom_dir = self.get("custom_log_dir")
        if custom_dir and Path(custom_dir).exists():
            return Path(custom_dir)
        return LOGS_DIR


# Global config instance for easy access
config = ConfigManager()


def get_config() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager singleton instance
    """
    return config