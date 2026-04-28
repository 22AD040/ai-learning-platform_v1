"""
FastAPI Server for Smart Academic Assistant Pro
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import os


try:
    from jose import jwt  
    JOSE_AVAILABLE = True
except ImportError:
    import jwt  
    JOSE_AVAILABLE = False
    print("⚠️ Using pyjwt instead of python-jose. Install python-jose for better security.")


from app.auth.auth import Authentication
from app.api.routes import API
from app.services.llm_service import LLMService
from app.config import Config

auth = Authentication()
api = API()
llm = LLMService()


SECRET_KEY = Config.SECRET_KEY if hasattr(Config, 'SECRET_KEY') else "your-secret-key-change-this"
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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: Optional[str] = None
    username: str
    role: str

class ContentRequest(BaseModel):
    topic: str
    level: str = "Intermediate"
    role: str = "college"

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 10

class QuizSubmitRequest(BaseModel):
    quiz_id: str
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
    # Startup
    print("🚀 FastAPI Server Starting...")
    print(f"✅ Authentication Service: Ready")
    print(f"✅ LLM Service: {'Available' if llm.gemini_available else 'Using Fallback'}")
    print(f"✅ API Service: Ready")
    yield
 
    print("👋 FastAPI Server Shutting Down...")

app = FastAPI(
    title="Smart Academic Assistant Pro API",
    description="REST API for academic content generation, quizzes, and authentication",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_access_token(data: dict):
    """Create JWT token for API authentication"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None



@app.post("/api/auth/login", response_model=MessageResponse)
async def api_login(request: LoginRequest):
    """
    Authenticate user and return JWT token
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

@app.post("/api/auth/register", response_model=MessageResponse)
async def api_register(request: RegisterRequest):
    """
    Register new user
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

@app.post("/api/auth/verify")
async def api_verify_token(token: str):
    """
    Verify JWT token
    """
    payload = verify_token(token)
    if payload:
        return {"valid": True, "username": payload.get("sub"), "role": payload.get("role")}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")



@app.post("/api/content/generate", response_model=MessageResponse)
async def api_generate_content(request: ContentRequest):
    """
    Generate study content using AI
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

@app.post("/api/mindmap/generate", response_model=MessageResponse)
async def api_generate_mindmap(topic: str):
    """
    Generate interactive mindmap for a topic
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

@app.post("/api/quiz/generate", response_model=MessageResponse)
async def api_generate_quiz(request: QuizRequest):
    """
    Generate AI-powered quiz on a topic
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



@app.get("/api/quizzes/college")
async def api_get_college_quizzes():
    """
    Get all college quizzes
    """

    from streamlit_app import get_comprehensive_college_quizzes
    quizzes = get_comprehensive_college_quizzes()
    return {"quizzes": quizzes}

@app.post("/api/quiz/submit", response_model=MessageResponse)
async def api_submit_quiz(request: QuizSubmitRequest):
    """
    Submit quiz answers and get evaluation
    """
   
    return MessageResponse(
        success=True,
        message="Quiz submitted",
        data={"score": 0, "total": 0, "percentage": 0, "results": []}
    )

@app.post("/api/test/submit", response_model=MessageResponse)
async def api_submit_test(request: TestSubmitRequest):
    """
    Submit assessment test and get evaluation
    """
    try:
        result = api.evaluate_assessment_test(request.test_id, request.answers)
        
        return MessageResponse(
            success=True,
            message="Test submitted successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test submission failed: {str(e)}"
        )



@app.get("/api/materials/school/{subject}")
async def api_get_school_materials(subject: str):
    """
    Get school study materials for a subject
    """
    materials = api.get_school_study_materials(subject)
    return {"subject": subject, "materials": materials}

@app.get("/api/placement-guides")
async def api_get_placement_guides():
    """
    Get placement preparation guides
    """
    guides = api.get_placement_guides()
    return {"guides": guides}

@app.get("/api/project-solutions")
async def api_get_project_solutions():
    """
    Get project solutions and examples
    """
    projects = api.get_project_solutions()
    return {"projects": projects}

@app.get("/api/subject-time-charts")
async def api_get_subject_time_charts():
    """
    Get subject-wise time allocation charts for exam aspirants
    """
    charts = api.get_subject_time_charts()
    return {"charts": charts}

@app.get("/api/assessment-tests")
async def api_get_assessment_tests():
    """
    Get assessment tests for exam aspirants
    """
    tests = api.get_assessment_tests()
    return {"tests": tests}



@app.get("/api/health")
async def api_health_check():
    """
    Check API health and service status
    """
    return {
        "status": "healthy",
        "services": {
            "authentication": "active",
            "llm_service": "active" if llm.gemini_available else "fallback_mode",
            "api_service": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """
    API root endpoint
    """
    return {
        "name": "Smart Academic Assistant Pro API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth/login, /api/auth/register",
            "content": "/api/content/generate, /api/mindmap/generate",
            "quizzes": "/api/quiz/generate, /api/quizzes/college",
            "tests": "/api/assessment-tests, /api/test/submit",
            "materials": "/api/materials/school/{subject}, /api/placement-guides"
        }
    }

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)