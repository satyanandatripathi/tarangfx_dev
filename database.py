"""
Database Module for PnProjects Audio Bot
Handles all database operations with Supabase for scalability
"""

import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for user sessions and processing queue"""

    _instance: Optional['DatabaseManager'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            try:
                supabase_url = os.getenv('SUPABASE_URL')
                supabase_key = os.getenv('SUPABASE_ANON_KEY')

                if not supabase_url or not supabase_key:
                    logger.warning("Supabase credentials not found, using in-memory storage")
                    self._client = None
                else:
                    self._client = create_client(supabase_url, supabase_key)
                    logger.info("Database connection established")
            except Exception as e:
                logger.error("Failed to connect to database: %s", e)
                self._client = None

    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._client is not None

    async def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get active session for user"""
        if not self.is_connected:
            return None

        try:
            response = self._client.table('user_sessions') \
                .select('*') \
                .eq('user_id', user_id) \
                .gt('expires_at', datetime.utcnow().isoformat()) \
                .order('updated_at', desc=True) \
                .limit(1) \
                .execute()

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.exception("Error getting user session")
            return None

    async def create_user_session(
        self,
        user_id: int,
        file_path: Optional[str] = None,
        original_filename: Optional[str] = None,
        file_info: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """Create new user session"""
        if not self.is_connected:
            return None

        try:
            session_data = {
                'user_id': user_id,
                'file_path': file_path,
                'original_filename': original_filename,
                'file_info': file_info or {},
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }

            response = self._client.table('user_sessions') \
                .insert(session_data) \
                .execute()

            if response.data:
                logger.info("Created session for user %s", user_id)
                return response.data[0]
            return None
        except Exception as e:
            logger.exception("Error creating user session")
            return None

    async def update_user_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update existing session"""
        if not self.is_connected:
            return False

        try:
            response = self._client.table('user_sessions') \
                .update(updates) \
                .eq('id', session_id) \
                .execute()

            return bool(response.data)
        except Exception as e:
            logger.exception("Error updating session")
            return False

    async def delete_user_session(self, session_id: str) -> bool:
        """Delete user session"""
        if not self.is_connected:
            return False

        try:
            self._client.table('user_sessions') \
                .delete() \
                .eq('id', session_id) \
                .execute()

            logger.info("Deleted session: %s", session_id)
            return True
        except Exception as e:
            logger.exception("Error deleting session")
            return False

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count"""
        if not self.is_connected:
            return 0

        try:
            response = self._client.table('user_sessions') \
                .delete() \
                .lt('expires_at', datetime.utcnow().isoformat()) \
                .execute()

            count = len(response.data) if response.data else 0
            if count > 0:
                logger.info("Cleaned up %d expired sessions", count)
            return count
        except Exception as e:
            logger.exception("Error cleaning up sessions")
            return 0

    async def extend_session_expiry(self, session_id: str) -> bool:
        """Extend session expiry by 5 minutes"""
        if not self.is_connected:
            return False

        try:
            new_expiry = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            response = self._client.table('user_sessions') \
                .update({
                    'updated_at': datetime.utcnow().isoformat(),
                    'expires_at': new_expiry
                }) \
                .eq('id', session_id) \
                .execute()

            return bool(response.data)
        except Exception as e:
            logger.exception("Error extending session")
            return False


class InMemorySessionManager:
    """Fallback in-memory session manager when database is not available"""

    def __init__(self):
        self.sessions: Dict[int, Dict] = {}

    def get_session(self, user_id: int) -> Optional[Dict]:
        """Get user session from memory"""
        session = self.sessions.get(user_id)
        if session and session.get('expires_at', datetime.min) > datetime.utcnow():
            return session
        elif session:
            del self.sessions[user_id]
        return None

    def create_session(self, user_id: int, **kwargs) -> Dict:
        """Create new session in memory"""
        session = {
            'user_id': user_id,
            'file_path': kwargs.get('file_path'),
            'original_filename': kwargs.get('original_filename'),
            'file_info': kwargs.get('file_info', {}),
            'settings': {
                'format': 'mp3',
                'bitrate': '320k',
                'sample_rate': 48000,
                'channels': 2,
                'bass_boost': 0,
                'normalize': False,
                'fade_in': 0,
                'fade_out': 0,
                'speed': 1.0,
                'eq': [],
                'effects': []
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }
        self.sessions[user_id] = session
        return session

    def update_session(self, user_id: int, updates: Dict) -> bool:
        """Update session in memory"""
        if user_id in self.sessions:
            self.sessions[user_id].update(updates)
            self.sessions[user_id]['updated_at'] = datetime.utcnow()
            self.sessions[user_id]['expires_at'] = datetime.utcnow() + timedelta(minutes=5)
            return True
        return False

    def delete_session(self, user_id: int) -> bool:
        """Delete session from memory"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            return True
        return False

    def cleanup_expired(self) -> int:
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = [uid for uid, sess in self.sessions.items()
                   if sess.get('expires_at', datetime.min) < now]
        for uid in expired:
            del self.sessions[uid]
        return len(expired)
