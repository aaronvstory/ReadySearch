"""Session management to prevent multiple browser instances and infinite loops."""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class SessionState:
    """Track session state and prevent infinite loops."""
    session_id: str
    browser_started: bool = False
    current_search: Optional[str] = None
    search_start_time: float = 0.0
    search_count: int = 0
    last_search_time: float = 0.0
    is_active: bool = False
    
class SessionManager:
    """Manages browser sessions and prevents infinite loops."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.sessions: Dict[str, SessionState] = {}
        self.global_lock = asyncio.Lock()
        self.max_search_time = 30.0  # Maximum search time in seconds
        self.max_concurrent_searches = 1  # Only allow 1 search at a time
        self.active_searches = 0
        
    async def start_session(self, session_id: str) -> bool:
        """
        Start a new session or return existing session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if session started successfully
        """
        async with self.global_lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if session.is_active:
                    logger.warning(f"Session {session_id} already active")
                    return False
                    
            # Create new session
            self.sessions[session_id] = SessionState(
                session_id=session_id,
                is_active=True
            )
            
            logger.info(f"📋 Automation session started")
            logger.info(f"Session ID: {session_id}")
            return True
    
    async def start_search(self, session_id: str, search_name: str) -> bool:
        """
        Start a new search, preventing concurrent searches.
        
        Args:
            session_id: Session identifier
            search_name: Name being searched
            
        Returns:
            True if search can proceed
        """
        async with self.global_lock:
            if session_id not in self.sessions:
                logger.error(f"Session {session_id} not found")
                return False
                
            session = self.sessions[session_id]
            
            # Check if already searching
            if session.current_search:
                elapsed = time.time() - session.search_start_time
                if elapsed < self.max_search_time:
                    logger.warning(f"Search already in progress for {session.current_search} ({elapsed:.1f}s)")
                    return False
                else:
                    logger.warning(f"Previous search for {session.current_search} timed out, forcing new search")
                    
            # Check global concurrent search limit
            if self.active_searches >= self.max_concurrent_searches:
                logger.warning(f"Maximum concurrent searches ({self.max_concurrent_searches}) reached")
                return False
                
            # Start new search
            session.current_search = search_name
            session.search_start_time = time.time()
            session.search_count += 1
            session.last_search_time = time.time()
            self.active_searches += 1
            
            logger.info(f"🔍 Starting search for: {search_name}")
            return True
    
    async def complete_search(self, session_id: str, search_name: str, duration_ms: int) -> bool:
        """
        Complete a search and release resources.
        
        Args:
            session_id: Session identifier  
            search_name: Name that was searched
            duration_ms: Search duration in milliseconds
            
        Returns:
            True if search completed successfully
        """
        async with self.global_lock:
            if session_id not in self.sessions:
                logger.warning(f"Session {session_id} not found during search completion")
                return False
                
            session = self.sessions[session_id]
            
            if session.current_search != search_name:
                logger.warning(f"Search mismatch: expected {session.current_search}, got {search_name}")
                
            # Clear current search
            session.current_search = None
            session.search_start_time = 0.0
            self.active_searches = max(0, self.active_searches - 1)
            
            logger.info(f"✅ Search completed for: {search_name} ({duration_ms}ms)")
            return True
    
    async def end_session(self, session_id: str) -> bool:
        """
        End a session and cleanup resources.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session ended successfully
        """
        async with self.global_lock:
            if session_id not in self.sessions:
                logger.warning(f"Session {session_id} not found during cleanup")
                return False
                
            session = self.sessions[session_id]
            
            # Force complete any active search
            if session.current_search:
                logger.warning(f"Force completing search for {session.current_search}")
                self.active_searches = max(0, self.active_searches - 1)
                
            # Remove session
            del self.sessions[session_id]
            
            logger.info(f"🧹 Session ended: {session_id}")
            return True
    
    async def check_session_health(self, session_id: str) -> Dict[str, Any]:
        """
        Check session health and detect issues.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with health status
        """
        async with self.global_lock:
            if session_id not in self.sessions:
                return {
                    'healthy': False,
                    'error': 'Session not found',
                    'active_searches': self.active_searches
                }
                
            session = self.sessions[session_id]
            current_time = time.time()
            
            # Check for stuck searches
            stuck_search = False
            if session.current_search:
                elapsed = current_time - session.search_start_time
                if elapsed > self.max_search_time:
                    stuck_search = True
                    
            # Check for too many concurrent searches
            too_many_searches = self.active_searches > self.max_concurrent_searches
            
            return {
                'healthy': not (stuck_search or too_many_searches),
                'session_id': session_id,
                'current_search': session.current_search,
                'search_count': session.search_count,
                'active_searches': self.active_searches,
                'stuck_search': stuck_search,
                'too_many_searches': too_many_searches,
                'last_search_elapsed': current_time - session.last_search_time if session.last_search_time > 0 else 0
            }
    
    async def force_cleanup(self) -> bool:
        """
        Force cleanup of all sessions and searches.
        
        Returns:
            True if cleanup completed
        """
        async with self.global_lock:
            logger.warning("🚨 Force cleanup of all sessions")
            
            # Clear all sessions
            self.sessions.clear()
            self.active_searches = 0
            
            logger.info("✅ Force cleanup completed")
            return True

# Global session manager instance
session_manager = SessionManager()