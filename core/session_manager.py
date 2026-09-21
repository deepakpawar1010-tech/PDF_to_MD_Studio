"""
PDF_to_MD_Studio v1.0 - Session State Manager
==============================================
Manages Streamlit session state for the application.
Provides type-safe accessors and initialization.
"""

from typing import Any, Dict, List, Optional

import streamlit as st

from core.constants import DEFAULT_SETTINGS, SESSION_KEYS


class SessionManager:
    """
    Manages Streamlit session state with safe initialization
    and typed accessors for all application state.
    """
    
    @staticmethod
    def initialize() -> None:
        """
        Initialize all session state variables if they don't exist.
        Safe to call multiple times (idempotent).
        """
        defaults = {
            SESSION_KEYS["conversion_history"]: [],
            SESSION_KEYS["current_file"]: None,
            SESSION_KEYS["output_path"]: None,
            SESSION_KEYS["settings"]: DEFAULT_SETTINGS.copy(),
            SESSION_KEYS["theme"]: "light",
            SESSION_KEYS["last_conversion_time"]: None,
            SESSION_KEYS["batch_files"]: [],
            SESSION_KEYS["zip_output_path"]: None,
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Safely get a value from session state.
        
        Args:
            key: Session state key
            default: Default if key doesn't exist
            
        Returns:
            The stored value or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set a value in session state.
        
        Args:
            key: Session state key
            value: Value to store
        """
        st.session_state[key] = value
    
    @staticmethod
    def delete(key: str) -> None:
        """
        Remove a key from session state if it exists.
        
        Args:
            key: Key to remove
        """
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def exists(key: str) -> bool:
        """
        Check if a key exists in session state.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists
        """
        return key in st.session_state
    
    # -------------------------------------------------------------------------
    # Typed accessors for common session data
    # -------------------------------------------------------------------------
    
    @classmethod
    def get_conversion_history(cls) -> List[Dict[str, Any]]:
        """Get the list of past conversions."""
        return cls.get(SESSION_KEYS["conversion_history"], [])
    
    @classmethod
    def add_conversion(cls, record: Dict[str, Any]) -> None:
        """
        Add a conversion record to history.
        
        Args:
            record: Dictionary with conversion details
        """
        history = cls.get_conversion_history()
        history.insert(0, record)  # Most recent first
        # Keep only last 50 conversions
        history = history[:50]
        cls.set(SESSION_KEYS["conversion_history"], history)
    
    @classmethod
    def clear_history(cls) -> None:
        """Clear all conversion history."""
        cls.set(SESSION_KEYS["conversion_history"], [])
    
    @classmethod
    def get_current_file(cls) -> Optional[str]:
        """Get the currently selected/uploaded file path."""
        return cls.get(SESSION_KEYS["current_file"])
    
    @classmethod
    def set_current_file(cls, file_path: Optional[str]) -> None:
        """Set the currently selected file path."""
        cls.set(SESSION_KEYS["current_file"], file_path)
    
    @classmethod
    def get_output_path(cls) -> Optional[str]:
        """Get the path to the last conversion output."""
        return cls.get(SESSION_KEYS["output_path"])
    
    @classmethod
    def set_output_path(cls, path: Optional[str]) -> None:
        """Set the output path for the current conversion."""
        cls.set(SESSION_KEYS["output_path"], path)
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """Get current session settings."""
        return cls.get(SESSION_KEYS["settings"], DEFAULT_SETTINGS.copy())
    
    @classmethod
    def update_settings(cls, updates: Dict[str, Any]) -> None:
        """
        Update session settings with new values.
        
        Args:
            updates: Dictionary of settings to update
        """
        settings = cls.get_settings()
        settings.update(updates)
        cls.set(SESSION_KEYS["settings"], settings)
    
    @classmethod
    def reset_settings(cls) -> None:
        """Reset settings to defaults."""
        cls.set(SESSION_KEYS["settings"], DEFAULT_SETTINGS.copy())
    
    @classmethod
    def get_theme(cls) -> str:
        """Get current UI theme ('dark' or 'light')."""
        return cls.get(SESSION_KEYS["theme"], "light")
    
    @classmethod
    def set_theme(cls, theme: str) -> None:
        """Set UI theme."""
        cls.set(SESSION_KEYS["theme"], theme)
    
    @classmethod
    def get_batch_files(cls) -> List[str]:
        """Get list of files in current batch."""
        return cls.get(SESSION_KEYS["batch_files"], [])
    
    @classmethod
    def set_batch_files(cls, files: List[str]) -> None:
        """Set batch file list."""
        cls.set(SESSION_KEYS["batch_files"], files)
    
    @classmethod
    def clear_batch_files(cls) -> None:
        """Clear batch file list."""
        cls.set(SESSION_KEYS["batch_files"], [])
    
    @classmethod
    def get_zip_output_path(cls) -> Optional[str]:
        """Get path to generated ZIP archive."""
        return cls.get(SESSION_KEYS["zip_output_path"])
    
    @classmethod
    def set_zip_output_path(cls, path: Optional[str]) -> None:
        """Set ZIP output path."""
        cls.set(SESSION_KEYS["zip_output_path"], path)


def init_session() -> None:
    """
    Convenience function to initialize session state.
    Call this at the start of every page.
    """
    SessionManager.initialize()