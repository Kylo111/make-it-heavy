"""
Session Manager for Make It Heavy GUI application.
Handles conversation persistence, session history, and session management.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ChatMessage:
    """Chat message data model"""
    sender: str  # "user", "agent", "system"
    content: str
    timestamp: datetime
    message_type: str = "text"  # "text", "progress", "error"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            sender=data['sender'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_type=data.get('message_type', 'text')
        )


@dataclass
class ChatSession:
    """Chat session data model"""
    session_id: str
    title: str
    created_at: datetime
    last_updated: datetime
    messages: List[ChatMessage]
    config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'config': self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            session_id=data['session_id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_updated=datetime.fromisoformat(data['last_updated']),
            messages=[ChatMessage.from_dict(msg) for msg in data['messages']],
            config=data.get('config')
        )


class SessionManager:
    """
    Manages chat sessions, conversation persistence, and session history.
    """
    
    def __init__(self, sessions_dir: str = ".kiro/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[ChatSession] = None
        self.sessions_cache: Dict[str, ChatSession] = {}
        
        # Load existing sessions
        self._load_sessions()
    
    def _load_sessions(self):
        """Load all existing sessions from disk"""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    session = ChatSession.from_dict(session_data)
                    self.sessions_cache[session.session_id] = session
                    
                except Exception as e:
                    print(f"Error loading session {session_file}: {e}")
                    
        except Exception as e:
            print(f"Error loading sessions directory: {e}")
    
    def create_new_session(self, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        if not title:
            title = f"Chat {now.strftime('%Y-%m-%d %H:%M')}"
        
        session = ChatSession(
            session_id=session_id,
            title=title,
            created_at=now,
            last_updated=now,
            messages=[]
        )
        
        self.current_session = session
        self.sessions_cache[session_id] = session
        self._save_session(session)
        
        return session
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load an existing session"""
        if session_id in self.sessions_cache:
            self.current_session = self.sessions_cache[session_id]
            return self.current_session
        return None
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session"""
        return self.current_session
    
    def add_message(self, sender: str, content: str, message_type: str = "text") -> ChatMessage:
        """Add a message to the current session"""
        if not self.current_session:
            self.create_new_session()
        
        message = ChatMessage(
            sender=sender,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type
        )
        
        self.current_session.messages.append(message)
        self.current_session.last_updated = datetime.now()
        
        # Update session title based on first user message
        if sender == "user" and len([m for m in self.current_session.messages if m.sender == "user"]) == 1:
            self.current_session.title = self._generate_session_title(content)
        
        self._save_session(self.current_session)
        return message
    
    def get_session_list(self) -> List[Dict[str, Any]]:
        """Get list of all sessions (sorted by last updated)"""
        sessions = list(self.sessions_cache.values())
        sessions.sort(key=lambda s: s.last_updated, reverse=True)
        
        return [
            {
                'session_id': session.session_id,
                'title': session.title,
                'created_at': session.created_at,
                'last_updated': session.last_updated,
                'message_count': len(session.messages)
            }
            for session in sessions
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            # Remove from cache
            if session_id in self.sessions_cache:
                del self.sessions_cache[session_id]
            
            # Remove file
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            # Clear current session if it was deleted
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            
            return True
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def clear_current_session(self):
        """Clear the current session (create new empty session)"""
        self.create_new_session()
    
    def update_session_config(self, config: Dict[str, Any]):
        """Update configuration for current session"""
        if self.current_session:
            self.current_session.config = config
            self.current_session.last_updated = datetime.now()
            self._save_session(self.current_session)
    
    def export_session(self, session_id: str, export_path: str) -> bool:
        """Export session to a file"""
        try:
            if session_id not in self.sessions_cache:
                return False
            
            session = self.sessions_cache[session_id]
            
            # Create export data
            export_data = {
                'session': session.to_dict(),
                'exported_at': datetime.now().isoformat(),
                'export_version': '1.0'
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting session {session_id}: {e}")
            return False
    
    def import_session(self, import_path: str) -> Optional[str]:
        """Import session from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            session_data = import_data['session']
            session = ChatSession.from_dict(session_data)
            
            # Generate new session ID to avoid conflicts
            session.session_id = str(uuid.uuid4())
            session.title = f"[Imported] {session.title}"
            
            self.sessions_cache[session.session_id] = session
            self._save_session(session)
            
            return session.session_id
            
        except Exception as e:
            print(f"Error importing session: {e}")
            return None
    
    def _save_session(self, session: ChatSession):
        """Save session to disk"""
        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving session {session.session_id}: {e}")
    
    def _generate_session_title(self, first_message: str) -> str:
        """Generate a session title from the first user message"""
        # Take first 50 characters and clean up
        title = first_message.strip()[:50]
        if len(first_message) > 50:
            title += "..."
        
        # Remove newlines and extra spaces
        title = " ".join(title.split())
        
        return title if title else f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about sessions"""
        total_sessions = len(self.sessions_cache)
        total_messages = sum(len(session.messages) for session in self.sessions_cache.values())
        
        if self.sessions_cache:
            oldest_session = min(self.sessions_cache.values(), key=lambda s: s.created_at)
            newest_session = max(self.sessions_cache.values(), key=lambda s: s.created_at)
        else:
            oldest_session = newest_session = None
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'oldest_session_date': oldest_session.created_at if oldest_session else None,
            'newest_session_date': newest_session.created_at if newest_session else None
        }