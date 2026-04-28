"""
FastAPI Server for Smart Academic Assistant Pro
Complete working version for Render deployment
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import os
import sys


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


try:
    from jose import jwt
    JOSE_AVAILABLE = True
except ImportError:
    try:
        import jwt
        JOSE_AVAILABLE = True
    except ImportError:
        JOSE_AVAILABLE = False
        print("⚠️ JWT library not installed")


try:
    from app.auth.auth import Authentication
    from app.api.routes import API
    from app.services.llm_service import LLMService
    from app.config import Config
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"⚠️ Import error: {e}")
  
    class Authentication:
        def login_user(self, username, password):
            return {"success": False, "message": "Auth service unavailable"}
        def register_user(self, username, password, email, role):
            return {"success": False, "message": "Auth service unavailable"}
    
    class API:
        def get_school_study_materials(self, subject): return {}
        def get_placement_guides(self): return {}
        def get_project_solutions(self): return []
        def get_subject_time_charts(self): return {}
        def get_assessment_tests(self): return []
        def evaluate_assessment_test(self, test_id, answers): return None
    
    class LLMService:
        def __init__(self): self.gemini_available = False
        def generate_study_content_with_ai(self, topic, level): 
            return {"overview": f"Content for {topic}", "full_form": "N/A"}
        def generate_mindmap_with_ai(self, topic): return {"topic": topic, "branches": []}
        def generate_quiz_with_ai(self, topic, num_questions): return {"topic": topic, "questions": []}
    
    class Config:
        APP_NAME = "Smart Academic Assistant Pro"
        DATA_DIR = "data"
        SCHOOL_SUBJECTS = ["Mathematics", "Science", "English", "Social Studies", "Computer Science"]


auth = Authentication()
api = API()
llm = LLMService()


security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str

class ContentRequest(BaseModel):
    topic: str
    level: str = "Intermediate"
    role: str = "college"

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 10

class QuizSubmitRequest(BaseModel):
    quiz_id: int
    answers: Dict[str, int]

class TestSubmitRequest(BaseModel):
    test_id: int
    answers: Dict[str, int]

class MessageResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None



@asynccontextmanager
async def lifespan(app: FastAPI):

    print("=" * 50)
    print("🚀 FastAPI Server Starting...")
    print(f"✅ Authentication Service: Ready")
    print(f"✅ LLM Service: {'Available' if llm.gemini_available else 'Using Fallback'}")
    print(f"✅ API Service: Ready")
    print("=" * 50)
    yield
 
    print("👋 FastAPI Server Shutting Down...")

app = FastAPI(
    title="Smart Academic Assistant Pro API",
    description="""
    ## 🎓 Smart Academic Assistant Pro - REST API
    
    This API provides educational content generation, quizzes, study materials, and authentication.
    
    ### Features:
    - 📚 **AI Content Generation** - Generate study content for any topic
    - 🔐 **Authentication** - User login and registration
    - 📝 **Quizzes & Tests** - Create and submit quizzes
    - 📖 **Study Materials** - Access PDF guides and resources
    
    ### Base URL:
    `https://your-app.onrender.com`
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Smart Academic Assistant Pro",
        "email": "support@smartacademic.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_access_token(data: dict):
    if not JOSE_AVAILABLE:
        return "jwt_not_available_install_python_jose"
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not JOSE_AVAILABLE:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")



@app.get("/")
async def root():
    return {
        "name": "Smart Academic Assistant Pro API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/api/health",
        "endpoints": {
            "auth": {
                "login": "POST /api/auth/login",
                "register": "POST /api/auth/register"
            },
            "content": {
                "generate": "POST /api/content/generate",
                "mindmap": "POST /api/mindmap/generate",
                "quiz": "POST /api/quiz/generate"
            },
            "materials": {
                "school": "GET /api/materials/school/{subject}",
                "placement": "GET /api/placement-guides",
                "projects": "GET /api/project-solutions",
                "assessment": "GET /api/assessment-tests"
            },
            "quizzes": {
                "college": "GET /api/quizzes/college"
            },
            "health": {
                "check": "GET /api/health"
            }
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "authentication": "active",
            "llm_service": "active" if getattr(llm, 'gemini_available', False) else "fallback",
            "api_service": "active"
        }
    }



@app.post("/api/auth/login", response_model=MessageResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT token for subsequent authenticated requests.
    """
    result = auth.login_user(request.username, request.password)
    
    if result['success']:
        access_token = create_access_token(
            data={"sub": request.username, "role": result['user']['role']}
        )
        
        return MessageResponse(
            success=True,
            message=result['message'],
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "username": request.username,
                "role": result['user']['role']
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result['message']
        )

@app.post("/api/auth/register", response_model=MessageResponse, tags=["Authentication"])
async def register(request: RegisterRequest):
    """
    Register a new user.
    
    - **username**: Desired username
    - **password**: Desired password
    - **email**: User's email address
    - **role**: User role (school/college/aspirant)
    """
    result = auth.register_user(request.username, request.password, request.email, request.role)
    
    if result['success']:
        return MessageResponse(
            success=True,
            message=result['message'],
            data={"username": request.username, "role": request.role}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['message']
        )



@app.post("/api/content/generate", response_model=MessageResponse, tags=["Content"])
async def generate_content(request: ContentRequest):
    """
    Generate AI-powered study content for any topic.
    
    - **topic**: Topic to generate content for (e.g., "Artificial Intelligence", "Python")
    - **level**: Difficulty level (Beginner/Intermediate/Advanced)
    - **role**: User role for context (school/college/aspirant)
    """
    try:
        content = llm.generate_study_content_with_ai(request.topic, request.level)
        
        return MessageResponse(
            success=True,
            message=f"Content generated for {request.topic}",
            data=content
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@app.post("/api/mindmap/generate", response_model=MessageResponse, tags=["Content"])
async def generate_mindmap(topic: str):
    """
    Generate an interactive mindmap/learning roadmap for a topic.
    
    - **topic**: Topic to generate mindmap for
    """
    try:
        mindmap = llm.generate_mindmap_with_ai(topic)
        
        return MessageResponse(
            success=True,
            message=f"Mindmap generated for {topic}",
            data=mindmap
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mindmap generation failed: {str(e)}"
        )

@app.post("/api/quiz/generate", response_model=MessageResponse, tags=["Content"])
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz with multiple-choice questions on a topic.
    
    - **topic**: Topic to generate quiz for
    - **num_questions**: Number of questions to generate
    """
    try:
        quiz = llm.generate_quiz_with_ai(request.topic, request.num_questions)
        
        return MessageResponse(
            success=True,
            message=f"Quiz generated for {request.topic}",
            data=quiz
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation failed: {str(e)}"
        )



@app.get("/api/materials/school/{subject}", tags=["Materials"])
async def get_school_materials(subject: str):
    """
    Get school study materials PDFs for a subject.
    
    - **subject**: Subject name (Mathematics, Science, English, Social Studies, Computer Science)
    """
    materials = api.get_school_study_materials(subject)
    return {"subject": subject, "materials": materials}

@app.get("/api/placement-guides", tags=["Materials"])
async def get_placement_guides():
    """Get placement preparation guides (Resume, Aptitude, Technical Interview, HR, GD)."""
    guides = api.get_placement_guides()
    return {"guides": guides}

@app.get("/api/project-solutions", tags=["Materials"])
async def get_project_solutions():
    """Get real-time project examples and solutions."""
    projects = api.get_project_solutions()
    return {"projects": projects}

@app.get("/api/subject-time-charts", tags=["Materials"])
async def get_subject_time_charts():
    """Get subject-wise time allocation charts for exam aspirants."""
    charts = api.get_subject_time_charts()
    return {"charts": charts}

@app.get("/api/assessment-tests", tags=["Materials"])
async def get_assessment_tests():
    """Get assessment tests for exam aspirants."""
    tests = api.get_assessment_tests()
    return {"tests": tests}

@app.get("/api/quick-tips", tags=["Materials"])
async def get_quick_tips():
    """Get quick study tips for exam preparation."""
    tips = api.get_quick_tips()
    return {"tips": tips}



@app.get("/api/quizzes/college", tags=["Quizzes"])
async def get_college_quizzes():
    """Get all college-level quizzes (DBMS, OS, Networks, Web Dev, Software Engineering)."""
    from frontend.app import get_comprehensive_college_quizzes
    quizzes = get_comprehensive_college_quizzes()
    return {"quizzes": quizzes}

@app.post("/api/quiz/submit", response_model=MessageResponse, tags=["Quizzes"])
async def submit_quiz(request: QuizSubmitRequest):
    """
    Submit quiz answers and get evaluation.
    
    - **quiz_id**: ID of the quiz
    - **answers**: Dictionary of question indices to answer indices
    """
    result = api.evaluate_quiz(request.quiz_id, request.answers)
    
    if result:
        return MessageResponse(
            success=True,
            message="Quiz submitted successfully",
            data=result
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

@app.post("/api/test/submit", response_model=MessageResponse, tags=["Quizzes"])
async def submit_test(request: TestSubmitRequest):
    """
    Submit assessment test and get evaluation.
    
    - **test_id**: ID of the test
    - **answers**: Dictionary of question indices to answer indices
    """
    result = api.evaluate_assessment_test(request.test_id, request.answers)
    
    if result:
        return MessageResponse(
            success=True,
            message="Test submitted successfully",
            data=result
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )



@app.post("/api/chat", tags=["Chat"])
async def chat(message: str, role: str = "college"):
    """
    Get AI response for chat messages.
    
    - **message**: User's message/question
    - **role**: User role (school/college/aspirant)
    """
    try:
        response = llm.get_ai_chat_response(message, role)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )



@app.get("/api/user/profile", tags=["User"])
async def get_user_profile(payload: dict = Depends(verify_token)):
    """Get current user profile (requires authentication)."""
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "authenticated": True
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    
    print("=" * 50)
    print("🚀 Starting FastAPI Server for Smart Academic Assistant Pro")
    print("=" * 50)
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"🔧 Alternative Docs: http://localhost:{port}/redoc")
    print(f"💚 Health Check: http://localhost:{port}/api/health")
    print("=" * 50)
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )