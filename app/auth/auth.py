import json
import bcrypt
from datetime import datetime
from typing import Dict, Optional
import os
from app.config import Config

class Authentication:
    """Handles user authentication and management"""
    
    def __init__(self):
        self.users_file = Config.USERS_FILE
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure the users data file exists"""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register_user(self, username: str, password: str, email: str, role: str) -> Dict:
        """Register a new user"""
        users = self._load_users()
     
        if username in users:
            return {"success": False, "message": "Username already exists"}
        
       
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
      
        user = {
            "username": username,
            "password": hashed_password.decode('utf-8'),
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        users[username] = user
        self._save_users(users)
        
        return {"success": True, "message": "User registered successfully"}
    
    def login_user(self, username: str, password: str) -> Dict:
        """Authenticate user login"""
        users = self._load_users()
        
        if username not in users:
            return {"success": False, "message": "Invalid username or password"}
        
        user = users[username]
        
   
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        
            user['last_login'] = datetime.now().isoformat()
            users[username] = user
            self._save_users(users)
            
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "username": user['username'],
                    "email": user['email'],
                    "role": user['role']
                }
            }
        
        return {"success": False, "message": "Invalid username or password"}
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user's role"""
        users = self._load_users()
        if username in users:
            return users[username]['role']
        return None