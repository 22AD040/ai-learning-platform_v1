import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    """Application configuration"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    APP_NAME = "Smart Academic Assistant Pro"
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    if not GEMINI_API_KEY:
        print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables!")
        print("   Please add GEMINI_API_KEY=your-api-key-here to your .env file")
    

    DATA_DIR = "data"
    USERS_FILE = os.path.join(DATA_DIR, "users.json")
    CHATS_FILE = os.path.join(DATA_DIR, "chats.json")
    

    ROLES = {
        "school": "School Student",
        "college": "College Student",
        "aspirant": "Exam Aspirant"
    }
    

    SCHOOL_SUBJECTS = ["Mathematics", "Science", "English", "Social Studies", "Computer Science"]
    
  
    ASPIRANT_SUBJECTS = ["Quantitative Aptitude", "Logical Reasoning", "English", "General Knowledge", "Technical Subjects"]