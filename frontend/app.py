import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from app.auth.auth import Authentication
from app.api.routes import API
from app.services.llm_service import LLMService
from app.config import Config


auth = Authentication()
api = API()
llm = LLMService()


st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_background():
    """Apply background image - White text for sidebar, BLACK text for main content"""
    st.markdown("""
        <style>
        /* Main app background - full screen */
        .stApp {
            background-image: url("https://i.pinimg.com/1200x/ef/3a/9a/ef3a9a53d8523aba97ed1777e4215029.jpg") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }
        
        /* Remove white overlay */
        .stApp::before, .stApp::after {
            display: none !important;
        }
        
        /* Add dark overlay to main content area for readability */
        .stAppViewContainer {
            background-color: rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Header transparent */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        
        header[data-testid="stHeader"] > div {
            background-color: transparent !important;
        }
        
        .stApp header {
            background-color: transparent !important;
        }
        
        .st-emotion-cache-12fmjuu {
            background-color: transparent !important;
        }
        
        [class*="header"] {
            background-color: transparent !important;
        }
        
        /* Sidebar - dark semi-transparent */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.7) !important;
            backdrop-filter: blur(8px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        
        /* SIDEBAR TEXT - WHITE ONLY */
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* MAIN CONTENT TEXT - BLACK/DARK */
        .main * {
            color: #1a1a1a !important;
        }
        
        /* Headers in main content */
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            color: #0a0a0a !important;
        }
        
        /* Paragraphs in main content */
        .main p, .main span, .main div, .stMarkdown p {
            color: #2a2a2a !important;
        }
        
        /* Code blocks */
        .stCodeBlock, .stCodeBlock * {
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: #e0e0e0 !important;
        }
        
        /* Buttons - keep visible */
        button, .stButton button {
            color: white !important;
            background-color: rgba(0, 0, 0, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        
        /* Info boxes - light background with dark text */
        .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #1a1a1a !important;
        }
        
        .stAlert *, .stInfo *, .stSuccess *, .stWarning *, .stError * {
            color: #1a1a1a !important;
        }
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea {
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #1a1a1a !important;
            border: 1px solid rgba(0, 0, 0, 0.2) !important;
        }
        
        .stTextInput label, .stTextArea label {
            color: #1a1a1a !important;
        }
        
        /* Select boxes */
        .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #1a1a1a !important;
        }
        
        /* Radio buttons in main content */
        .stRadio label {
            color: #1a1a1a !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] button {
            color: #1a1a1a !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
        }
        
        /* Metric cards */
        [data-testid="stMetric"] label, [data-testid="stMetric"] div {
            color: #1a1a1a !important;
        }
        
        /* Expander headers */
        [data-testid="stExpander"] summary p {
            color: #1a1a1a !important;
        }
        
        /* Download buttons */
        .stDownloadButton button {
            background-color: rgba(0, 0, 0, 0.7) !important;
            color: white !important;
        }
        
        /* Links */
        a {
            color: #0066cc !important;
        }
        </style>
    """, unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'registration_success' not in st.session_state:
        st.session_state.registration_success = False
    if 'current_test' not in st.session_state:
        st.session_state.current_test = None
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = []
    if 'selected_quiz' not in st.session_state:
        st.session_state.selected_quiz = None
    if 'show_quiz' not in st.session_state:
        st.session_state.show_quiz = False
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'active_quiz' not in st.session_state:
        st.session_state.active_quiz = None
    if 'ai_content_school' not in st.session_state:
        st.session_state.ai_content_school = None
    if 'ai_mindmap_school' not in st.session_state:
        st.session_state.ai_mindmap_school = None
    if 'ai_content_college' not in st.session_state:
        st.session_state.ai_content_college = None
    if 'ai_mindmap_college' not in st.session_state:
        st.session_state.ai_mindmap_college = None
    if 'ai_content_aspirant' not in st.session_state:
        st.session_state.ai_content_aspirant = None
    if 'ai_mindmap_aspirant' not in st.session_state:
        st.session_state.ai_mindmap_aspirant = None
    if 'quiz_answers_store' not in st.session_state:
        st.session_state.quiz_answers_store = {}
    if 'test_answers_store' not in st.session_state:
        st.session_state.test_answers_store = {}


def display_quiz(quiz):
    """Display and evaluate a quiz - WITHOUT ST.RERUN()"""
    st.subheader(f"📝 {quiz['title']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Questions", len(quiz['questions']))
    with col2:
        st.metric("Time Limit", f"{len(quiz['questions']) * 2} mins")
    with col3:
        st.metric("Passing Score", "60%")
    
    st.markdown("---")
    
  
    quiz_key = f"quiz_{quiz['id']}"
    
   
    if quiz_key not in st.session_state.quiz_answers_store:
        st.session_state.quiz_answers_store[quiz_key] = {}
    
    answers = {}
    all_answered = True
    
   
    for i, q in enumerate(quiz['questions']):
        with st.container():
            st.markdown(f"### Question {i+1}")
            st.markdown(f"**{q['question']}**")
            
        
            current_answer = st.session_state.quiz_answers_store[quiz_key].get(i)
            

            selected_option = st.radio(
                "Select your answer:",
                q['options'],
                key=f"{quiz_key}_q_{i}",
                index=current_answer if current_answer is not None else None,
                horizontal=True,
                label_visibility="collapsed"
            )
            
          
            if selected_option is not None:
                answer_index = q['options'].index(selected_option)
                answers[str(i)] = answer_index
                st.session_state.quiz_answers_store[quiz_key][i] = answer_index
            elif current_answer is not None:
                answers[str(i)] = current_answer
            else:
                all_answered = False
            
            st.markdown("---")
    
  
    submit_key = f"submit_{quiz_key}"
    
    if st.button("📤 Submit Quiz", key=submit_key, use_container_width=True, type="primary"):
        if all_answered and len(answers) == len(quiz['questions']):
        
            score = 0
            detailed_results = []
            
            for i, q in enumerate(quiz['questions']):
                user_answer_idx = st.session_state.quiz_answers_store[quiz_key].get(i)
                
                if user_answer_idx is not None:
                    is_correct = (user_answer_idx == q.get('correct', 0))
                    if is_correct:
                        score += 1
                    
                    detailed_results.append({
                        'question': q['question'],
                        'user_answer': q['options'][user_answer_idx],
                        'correct_answer': q['options'][q.get('correct', 0)],
                        'is_correct': is_correct,
                        'explanation': q.get('explanation', 'No explanation available')
                    })
            
            percentage = (score / len(quiz['questions'])) * 100
            
          
            st.session_state.quiz_history.append({
                'quiz_title': quiz['title'],
                'score': score,
                'total': len(quiz['questions']),
                'percentage': percentage,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
           
            if quiz_key in st.session_state.quiz_answers_store:
                del st.session_state.quiz_answers_store[quiz_key]
            
          
            st.markdown("## 📊 Your Results")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=percentage,
                    title={'text': "Score Percentage"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 40], 'color': "red"},
                            {'range': [40, 60], 'color': "orange"},
                            {'range': [60, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': 60
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"""
                ### Score Details
                - ✅ Correct Answers: **{score}**
                - ❌ Incorrect Answers: **{len(quiz['questions']) - score}**
                - 📊 Percentage: **{percentage:.1f}%**
                """)
            
            with st.expander("🔍 View Detailed Results & Explanations"):
                for i, res in enumerate(detailed_results):
                    if res['is_correct']:
                        st.markdown(f"✅ **Q{i+1}** - Correct!")
                    else:
                        st.markdown(f"❌ **Q{i+1}** - Incorrect")
                        st.markdown(f"Your answer: {res['user_answer']}")
                        st.markdown(f"Correct answer: {res['correct_answer']}")
                        st.markdown(f"📖 **Explanation:** {res['explanation']}")
                    st.markdown("---")
            
            if percentage >= 80:
                st.markdown("🎉 **Excellent!** You're mastering this topic! Keep up the great work!")
            elif percentage >= 60:
                st.markdown("👍 **Good job!** You passed! Review the incorrect answers to improve further.")
            else:
                st.markdown("📚 **Keep practicing!** Focus on understanding the concepts and try again.")
            
           
            st.session_state.show_quiz_results = True
            st.session_state.quiz_completed = True
            
        else:
            remaining = len(quiz['questions']) - len(answers)
            st.warning(f"⚠️ Please answer {remaining} more question(s) before submitting.")
    
   
    if st.session_state.get('quiz_completed', False):
        if st.button("← Back to All Quizzes", key=f"back_{quiz_key}", use_container_width=True):
            st.session_state.selected_quiz = None
            st.session_state.quiz_completed = False
            st.session_state.show_quiz_results = False
       
            if quiz_key in st.session_state.quiz_answers_store:
                del st.session_state.quiz_answers_store[quiz_key]
            st.rerun()

def display_assessment_test(test):
    """Display and evaluate assessment test - SIMPLE WORKING VERSION"""
    st.subheader(f"📝 {test['name']}")
    st.info(f"⏱️ Duration: {test['duration']} | 🎯 Difficulty: {test['difficulty']}")
    st.markdown(f"**Topics Covered:** {', '.join(test['topics'])}")
    st.markdown("---")
    
    answers = {}
    
   
    for i, q in enumerate(test['questions']):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        
      
        answer = st.radio(
            "Select your answer:",
            q['options'],
            key=f"test_{test['id']}_q_{i}",
            index=None,
            horizontal=True
        )
        if answer:
            answers[str(i)] = q['options'].index(answer)
        st.markdown("---")
    
    if st.button("Submit Assessment Test", key=f"submit_test_{test['id']}", use_container_width=True):
        if len(answers) == len(test['questions']):
            result = api.evaluate_assessment_test(test['id'], answers)
            
            if result:
                st.success(f"🎯 Your Score: {result['score']}/{result['total']} ({result['percentage']:.1f}%)")
                
                if result['percentage'] >= 80:
                    st.markdown("🎉 Excellent performance! You're well prepared!")
                elif result['percentage'] >= 60:
                    st.markdown("👍 Good effort! Review the incorrect answers to improve.")
                elif result['percentage'] >= 40:
                    st.markdown("📚 Need more practice. Focus on weak areas and try again.")
                else:
                    st.markdown("💪 Keep working hard! Review all topics thoroughly.")
                
                with st.expander("🔍 View Detailed Results & Explanations"):
                    for i, res in enumerate(result['results']):
                        if res['is_correct']:
                            st.markdown(f"✅ **Q{i+1}** - Correct!")
                        else:
                            st.markdown(f"❌ **Q{i+1}** - Incorrect")
                            st.markdown(f"Your answer: {res['user_answer']}")
                            st.markdown(f"Correct answer: {res['correct_answer']}")
                            st.markdown(f"📖 **Explanation:** {res['explanation']}")
                        st.markdown("---")
                
                st.subheader("📚 Study Recommendations")
                if result['percentage'] < 60:
                    st.markdown("""
                    - Review the topics where you made mistakes
                    - Practice more questions on weak areas
                    - Take topic-wise tests before attempting full tests
                    - Watch video tutorials for difficult concepts
                    """)
                else:
                    st.markdown("""
                    - Keep practicing to maintain your performance
                    - Focus on time management
                    - Attempt more mock tests for better preparation
                    - Revise regularly to retain concepts
                    """)
                
               
                if st.button("← Back to Tests", use_container_width=True):
                    st.session_state.current_test = None
                    st.rerun()
        else:
            st.warning(f"⚠️ Please answer all {len(test['questions'])} questions before submitting.")

def generate_unique_quiz(topic, num_questions=10):
    """Generate unique quiz questions based on topic"""
    
  
    question_banks = {
        "python": [
            {"question": "What is the correct way to create a function in Python?", "options": ["function myFunction():", "def myFunction():", "create myFunction():", "new myFunction():"], "correct": 1, "explanation": "In Python, functions are defined using the 'def' keyword."},
            {"question": "What does 'PEP' stand for in Python?", "options": ["Python Enhancement Proposal", "Python Execution Protocol", "Python Error Prevention", "Python External Package"], "correct": 0, "explanation": "PEP stands for Python Enhancement Proposal, which are design documents for Python."},
            {"question": "Which of the following is a mutable data type in Python?", "options": ["Tuple", "String", "List", "Integer"], "correct": 2, "explanation": "Lists are mutable (can be changed), while tuples, strings, and integers are immutable."},
            {"question": "What is the output of print(2**3)?", "options": ["6", "8", "9", "5"], "correct": 1, "explanation": "** is the exponentiation operator, so 2**3 = 2*2*2 = 8."},
            {"question": "Which keyword is used to import a module in Python?", "options": ["import", "include", "using", "require"], "correct": 0, "explanation": "The 'import' keyword is used to import modules in Python."},
            {"question": "What is a lambda function in Python?", "options": ["Anonymous function", "Built-in function", "Recursive function", "Generator function"], "correct": 0, "explanation": "Lambda functions are small anonymous functions defined with the 'lambda' keyword."},
            {"question": "What does the 'self' parameter refer to in Python classes?", "options": ["The class itself", "The current instance", "A static method", "A class variable"], "correct": 1, "explanation": "self refers to the current instance of the class."},
            {"question": "Which method is used to add an element to the end of a list?", "options": ["add()", "append()", "insert()", "extend()"], "correct": 1, "explanation": "append() adds an element to the end of a list."},
            {"question": "What is the correct file extension for Python files?", "options": [".pyth", ".pt", ".py", ".p"], "correct": 2, "explanation": "Python files use the .py extension."},
            {"question": "What is list comprehension in Python?", "options": ["Creating lists using loops", "Copying lists", "Deleting lists", "Sorting lists"], "correct": 0, "explanation": "List comprehension provides a concise way to create lists using loops."}
        ],
        "mathematics": [
            {"question": "What is the value of π (pi) approximately?", "options": ["3.14", "3.41", "3.12", "3.21"], "correct": 0, "explanation": "π (pi) is approximately 3.14159, commonly rounded to 3.14."},
            {"question": "What is the square root of 144?", "options": ["10", "11", "12", "13"], "correct": 2, "explanation": "12 × 12 = 144, so the square root is 12."},
            {"question": "What is 15% of 200?", "options": ["20", "25", "30", "35"], "correct": 2, "explanation": "15% of 200 = (15/100) × 200 = 30."},
            {"question": "What is the area of a circle with radius 5?", "options": ["25π", "10π", "5π", "15π"], "correct": 0, "explanation": "Area of circle = πr² = π × 25 = 25π."},
            {"question": "What is the value of 2³?", "options": ["4", "6", "8", "10"], "correct": 2, "explanation": "2³ = 2 × 2 × 2 = 8."},
            {"question": "What is the Pythagorean theorem?", "options": ["a² + b² = c²", "a + b = c", "a × b = c", "a/b = c"], "correct": 0, "explanation": "In a right triangle, a² + b² = c² where c is the hypotenuse."},
            {"question": "What is the sum of angles in a triangle?", "options": ["90°", "180°", "270°", "360°"], "correct": 1, "explanation": "The sum of interior angles in any triangle is 180°."},
            {"question": "What is 7 × 8?", "options": ["48", "56", "64", "72"], "correct": 1, "explanation": "7 × 8 = 56."},
            {"question": "What is the formula for the circumference of a circle?", "options": ["2πr", "πr²", "πd²", "2πd"], "correct": 0, "explanation": "Circumference = 2πr or πd."},
            {"question": "What is 25% of 80?", "options": ["15", "20", "25", "30"], "correct": 1, "explanation": "25% of 80 = (25/100) × 80 = 20."}
        ],
        "science": [
            {"question": "What is the chemical symbol for Gold?", "options": ["Go", "Gd", "Au", "Ag"], "correct": 2, "explanation": "Au comes from the Latin word 'aurum' meaning gold."},
            {"question": "What is the hardest natural substance?", "options": ["Iron", "Diamond", "Platinum", "Steel"], "correct": 1, "explanation": "Diamond is the hardest naturally occurring substance."},
            {"question": "What is the process by which plants make food?", "options": ["Respiration", "Photosynthesis", "Digestion", "Fermentation"], "correct": 1, "explanation": "Photosynthesis is the process where plants use sunlight to make food."},
            {"question": "What is the boiling point of water at sea level?", "options": ["90°C", "100°C", "110°C", "120°C"], "correct": 1, "explanation": "Water boils at 100°C (212°F) at sea level."},
            {"question": "Which planet is known as the Red Planet?", "options": ["Jupiter", "Mars", "Venus", "Saturn"], "correct": 1, "explanation": "Mars is called the Red Planet due to iron oxide on its surface."},
            {"question": "What is the center of an atom called?", "options": ["Nucleus", "Proton", "Neutron", "Electron"], "correct": 0, "explanation": "The nucleus is the center of an atom containing protons and neutrons."},
            {"question": "What gas do plants absorb from the air?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], "correct": 2, "explanation": "Plants absorb carbon dioxide for photosynthesis."},
            {"question": "What is the largest organ in the human body?", "options": ["Heart", "Liver", "Skin", "Brain"], "correct": 2, "explanation": "The skin is the largest organ in the human body."},
            {"question": "What is the speed of light?", "options": ["300,000 km/s", "150,000 km/s", "450,000 km/s", "600,000 km/s"], "correct": 0, "explanation": "Light travels at approximately 300,000 kilometers per second."},
            {"question": "What is the chemical symbol for Oxygen?", "options": ["Ox", "Om", "O", "Oy"], "correct": 2, "explanation": "Oxygen's chemical symbol is O."}
        ],
        "history": [
            {"question": "Who painted the Mona Lisa?", "options": ["Van Gogh", "Picasso", "Da Vinci", "Rembrandt"], "correct": 2, "explanation": "Leonardo da Vinci painted the Mona Lisa."},
            {"question": "In which year did World War II end?", "options": ["1943", "1944", "1945", "1946"], "correct": 2, "explanation": "World War II ended in 1945."},
            {"question": "Who was the first man to walk on the moon?", "options": ["Buzz Aldrin", "Neil Armstrong", "Michael Collins", "Yuri Gagarin"], "correct": 1, "explanation": "Neil Armstrong was the first person to walk on the moon in 1969."},
            {"question": "Which ancient civilization built Machu Picchu?", "options": ["Aztecs", "Mayans", "Incas", "Olmecs"], "correct": 2, "explanation": "The Incas built Machu Picchu in the 15th century."},
            {"question": "Who wrote 'Romeo and Juliet'?", "options": ["Charles Dickens", "Jane Austen", "William Shakespeare", "Mark Twain"], "correct": 2, "explanation": "William Shakespeare wrote Romeo and Juliet."}
        ]
    }
    
   
    topic_lower = topic.lower()
    questions = []
    
    for key, bank in question_banks.items():
        if key in topic_lower or topic_lower in key:
            questions = bank.copy()
            break
    
   
    if not questions:
        questions = question_banks["python"] + question_banks["mathematics"]
    
  
    random.shuffle(questions)
    selected_questions = questions[:min(num_questions, len(questions))]
    
   
    while len(selected_questions) < num_questions:
        selected_questions.extend(selected_questions[:num_questions - len(selected_questions)])
    
    return {
        "topic": topic,
        "questions": selected_questions,
        "timestamp": datetime.now().timestamp()
    }

def display_ai_quiz_generator():
    """AI Quiz Generator with UNIQUE questions each time"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="color: white;">🎯 AI-Powered Quiz Generator</h3>
        <p style="color: white;">Generate unique quizzes with different questions each time!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('quiz_active') and st.session_state.get('active_quiz'):
        quiz = st.session_state.active_quiz
        st.markdown(f"## 📝 Quiz: {quiz.get('topic', 'Custom Quiz')}")
        st.info(f"📊 Total Questions: {len(quiz['questions'])} | ⏱️ Estimated time: {len(quiz['questions']) * 1.5:.0f} minutes | 🎯 Passing Score: 70%")
        st.markdown("---")
        
       
        ai_quiz_key = f"ai_quiz_{quiz.get('topic', 'custom')}_{quiz.get('timestamp', datetime.now().timestamp())}"
        
    
        if ai_quiz_key not in st.session_state.quiz_answers_store:
            st.session_state.quiz_answers_store[ai_quiz_key] = {}
        
        answers = {}
        
       
        for i, q in enumerate(quiz['questions']):
            with st.container():
                st.markdown(f"### Question {i+1}")
                st.markdown(f"**{q.get('question', 'Question')}**")
                
                radio_key = f"{ai_quiz_key}_q_{i}"
                current_value = st.session_state.quiz_answers_store[ai_quiz_key].get(i)
                
                selected_option = st.radio(
                    "Select your answer:",
                    q.get('options', ['A', 'B', 'C', 'D']),
                    key=radio_key,
                    index=current_value if current_value is not None else None,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                if selected_option is not None:
                    answer_index = q.get('options', []).index(selected_option)
                    answers[str(i)] = answer_index
                    st.session_state.quiz_answers_store[ai_quiz_key][i] = answer_index
                elif str(i) in st.session_state.quiz_answers_store[ai_quiz_key]:
                    answers[str(i)] = st.session_state.quiz_answers_store[ai_quiz_key][i]
                
                st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Submit Quiz", use_container_width=True, type="primary", key=f"submit_{ai_quiz_key}"):
                total_answered = len([k for k in st.session_state.quiz_answers_store.get(ai_quiz_key, {}).keys()])
                
                if total_answered == len(quiz['questions']):
                    
                    final_answers = {}
                    for i in range(len(quiz['questions'])):
                        if i in st.session_state.quiz_answers_store[ai_quiz_key]:
                            final_answers[str(i)] = st.session_state.quiz_answers_store[ai_quiz_key][i]
                    
                    score = 0
                    detailed_results = []
                    
                    for i, q in enumerate(quiz['questions']):
                        user_answer_idx = final_answers.get(str(i))
                        is_correct = (user_answer_idx == q.get('correct', 0))
                        if is_correct:
                            score += 1
                        detailed_results.append({
                            'question': q.get('question'),
                            'user_answer': q.get('options', [])[user_answer_idx] if user_answer_idx is not None else 'Not answered',
                            'correct_answer': q.get('options', [])[q.get('correct', 0)],
                            'is_correct': is_correct,
                            'explanation': q.get('explanation', 'No explanation')
                        })
                    
                    percentage = (score / len(quiz['questions'])) * 100
                    
                    st.session_state.quiz_history.append({
                        'quiz_title': f"AI Quiz: {quiz.get('topic', 'Custom')}",
                        'score': score,
                        'total': len(quiz['questions']),
                        'percentage': percentage,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    st.markdown("## 📊 Quiz Results")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("✅ Correct", f"{score}/{len(quiz['questions'])}")
                    with c2:
                        st.metric("❌ Incorrect", f"{len(quiz['questions']) - score}/{len(quiz['questions'])}")
                    with c3:
                        st.metric("📊 Percentage", f"{percentage:.1f}%")
                    with c4:
                        grade = "A" if percentage >= 90 else "B" if percentage >= 80 else "C" if percentage >= 70 else "D" if percentage >= 60 else "F"
                        st.metric("🏆 Grade", grade)
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=percentage,
                        title={'text': "Score"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 60], 'color': "red"},
                                {'range': [60, 70], 'color': "orange"},
                                {'range': [70, 80], 'color': "yellow"},
                                {'range': [80, 90], 'color': "#90EE90"},
                                {'range': [90, 100], 'color': "green"}
                            ],
                            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 70}
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("🔍 View Detailed Results & Explanations"):
                        for i, res in enumerate(detailed_results):
                            if res['is_correct']:
                                st.markdown(f"✅ **Q{i+1}** - Correct!")
                            else:
                                st.markdown(f"❌ **Q{i+1}** - Incorrect")
                                st.markdown(f"Your answer: `{res['user_answer']}`")
                                st.markdown(f"Correct answer: `{res['correct_answer']}`")
                                st.markdown(f"📖 **Explanation:** {res['explanation']}")
                            st.markdown("---")
                    
                    if percentage >= 90:
                        st.success("🏆 **Outstanding!** You're a master of this topic!")
                    elif percentage >= 80:
                        st.success("🎉 **Excellent!** Great understanding!")
                    elif percentage >= 70:
                        st.info("👍 **Good job!** You passed!")
                    else:
                        st.warning("📚 **Keep practicing!** Review the material and try again.")
                    
                  
                    if ai_quiz_key in st.session_state.quiz_answers_store:
                        del st.session_state.quiz_answers_store[ai_quiz_key]
                    
                    if st.button("Take Another Quiz", use_container_width=True, key="take_another"):
                        st.session_state.quiz_active = False
                        st.session_state.active_quiz = None
                        st.rerun()
                else:
                    remaining = len(quiz['questions']) - total_answered
                    st.warning(f"⚠️ Please answer {remaining} more question(s) before submitting.")
        
        with col2:
            if st.button("Cancel Quiz", use_container_width=True, key="cancel_ai"):
                st.session_state.quiz_active = False
                st.session_state.active_quiz = None
                if ai_quiz_key in st.session_state.quiz_answers_store:
                    del st.session_state.quiz_answers_store[ai_quiz_key]
                st.rerun()
    
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            quiz_topic = st.text_input("📚 Quiz Topic:", placeholder="e.g., Python, Mathematics, Science, History", key="ai_quiz_topic")
            num_questions = st.slider("Number of questions:", 5, 15, 10, key="ai_num_questions")
        
        with col2:
            st.markdown("### Quick Topics")
            quick_topics = ["Python", "Mathematics", "Science", "History"]
            for i, qt in enumerate(quick_topics):
                if st.button(qt, key=f"quick_{qt}_{i}"):
                    quiz_topic = qt
                    st.rerun()
        
        if st.button("🎲 Generate Unique Quiz", use_container_width=True, type="primary", key="gen_unique_quiz"):
            if quiz_topic:
                with st.spinner(f"Generating {num_questions} UNIQUE questions about '{quiz_topic}'..."):
                    quiz = generate_unique_quiz(quiz_topic, num_questions)
                    if quiz and quiz.get('questions'):
                        st.session_state.active_quiz = quiz
                        st.session_state.quiz_active = True
                        st.rerun()
                    else:
                        st.error("Failed to generate quiz. Please try again.")
            else:
                st.warning("Please enter a quiz topic")

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="login-header">
        <h1 style="text-align: center; margin: 0;">🎓 Smart Academic Assistant Pro</h1>
        <p style="text-align: center; margin: 10px 0 0 0;">Your Intelligent Learning Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_register:
            st.subheader("🔐 Login")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    result = auth.login_user(username, password)
                    if result['success']:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = result['user']['role']
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
            
            st.markdown("---")
            st.markdown("### New User?")
            if st.button("Register Here", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
        
        else:
            st.subheader("📝 Registration")
            
            with st.form("register_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                role = st.selectbox("Select Your Role", 
                                   ["School Student", "College Student", "Exam Aspirant"])
                
                submit = st.form_submit_button("Register", use_container_width=True)
                
                if submit:
                    if password != confirm_password:
                        st.error("Passwords do not match!")
                    elif not username or not email or not password:
                        st.error("Please fill all fields!")
                    else:
                        role_key = {
                            "School Student": "school",
                            "College Student": "college",
                            "Exam Aspirant": "aspirant"
                        }[role]
                        
                        result = auth.register_user(username, password, email, role_key)
                        if result['success']:
                            st.success(result['message'])
                            st.session_state.show_register = False
                            st.session_state.registration_success = True
                            st.rerun()
                        else:
                            st.error(result['message'])
            
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()


def display_ai_content_generator(role_key):
    """AI Content Generator with role-specific storage - UPDATED to show all fields"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="color: white;">🤖 AI-Powered Study Assistant</h3>
        <p style="color: white;">Get comprehensive explanations with key observations for any topic!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("📚 Enter topic:", placeholder="e.g., AI, Python, ML, API, Cloud Computing", key=f"content_topic_{role_key}")
        level = st.selectbox("📊 Difficulty Level:", ["Beginner", "Intermediate", "Advanced"], key=f"content_level_{role_key}")
        
        if st.button("✨ Generate Study Content", use_container_width=True, type="primary", key=f"gen_content_btn_{role_key}"):
            if topic:
                with st.spinner(f"Generating comprehensive content for '{topic}'..."):
                    content = api.generate_content_with_gemini(topic, level)
                    if content:
                        st.session_state[f'ai_content_{role_key}'] = content
                        st.success("✅ Content generated successfully!")
                    else:
                        st.error("Could not generate content. Please try again.")
            else:
                st.warning("Please enter a topic")
    
    with col2:
        st.markdown("### 💡 What you'll get:")
        st.markdown("""
        - 📖 **Full Form** (for abbreviations)
        - 📚 **Detailed Overview**
        - 🔬 **In-depth Explanation**
        - 👁️ **Key Observations** (NEW!)
        - 💼 **Real-world Applications**
        - 📌 **Summary**
        """)
        
        if st.button("🧠 Generate Mindmap", use_container_width=True, key=f"gen_mindmap_btn_{role_key}"):
            if topic:
                with st.spinner(f"Creating roadmap for '{topic}'..."):
                    mindmap = api.generate_mindmap_with_gemini(topic)
                    if mindmap:
                        st.session_state[f'ai_mindmap_{role_key}'] = mindmap
                        st.success("✅ Mindmap created!")
            else:
                st.warning("Please enter a topic first")
    
    
    ai_content = st.session_state.get(f'ai_content_{role_key}')
    if ai_content:
        st.markdown("---")
        st.markdown("## 📖 Generated Study Material")
        
      
        if ai_content.get('full_form') and ai_content.get('full_form') != "N/A":
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; color: white;">
                <b>🔤 Full Form:</b> {ai_content['full_form']}
            </div>
            """, unsafe_allow_html=True)
        
       
        st.markdown("### 📌 Overview")
        st.markdown(f'<div style="background-color: #f0f7ff; padding: 1.2rem; border-radius: 12px; color: #000000; line-height: 1.6;">{ai_content.get("overview", "No overview available")}</div>', unsafe_allow_html=True)
   
        st.markdown("### 📚 Detailed Explanation")
        st.markdown(f'<div style="background-color: #f8f9fa; padding: 1.2rem; border-radius: 12px; color: #000000; line-height: 1.6;">{ai_content.get("detailed_explanation", ai_content.get("detailed_notes", "No detailed explanation available"))}</div>', unsafe_allow_html=True)
        
        
        st.markdown("### 👁️ Key Observations & Insights")
        key_observations = ai_content.get('key_observations', [])
        if key_observations:
            if isinstance(key_observations, list):
                for obs in key_observations:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.8rem; border-radius: 10px; margin-bottom: 0.7rem; color: white;">
                        💡 {obs}
                    </div>
                    """, unsafe_allow_html=True)
            else:
               
                obs_text = str(key_observations)
                import re
                observations = re.split(r'\n|•|\*|\d+\.', obs_text)
                for obs in observations:
                    if obs.strip():
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.8rem; border-radius: 10px; margin-bottom: 0.7rem; color: white;">
                            💡 {obs.strip()}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No specific observations available for this topic.")
 
        st.markdown("### 💼 Real-World Applications")
        applications = ai_content.get('applications', 'No applications described')
        st.markdown(f'<div style="background-color: #e8f4f8; padding: 1.2rem; border-radius: 12px; color: #000000; line-height: 1.6;">{applications}</div>', unsafe_allow_html=True)
        
  
        st.markdown("### 📌 Summary")
        st.markdown(f'<div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.2rem; border-radius: 12px; color: white; line-height: 1.6;">{ai_content.get("summary", "No summary available")}</div>', unsafe_allow_html=True)
        
      
        examples = ai_content.get('examples', [])
        if examples:
            st.markdown("### 💡 Examples")
            for ex in examples:
                st.markdown(f"""
                <div style="background-color: #f0f8f0; padding: 0.8rem; border-radius: 10px; margin-bottom: 0.5rem; border-left: 4px solid #11998e; color: #000000;">
                    {ex}
                </div>
                """, unsafe_allow_html=True)
    
  
    ai_mindmap = st.session_state.get(f'ai_mindmap_{role_key}')
    if ai_mindmap:
        st.markdown("---")
        st.markdown(f"## 🧠 Learning Roadmap: {ai_mindmap.get('topic', 'Topic')}")
        
        branches = ai_mindmap.get('branches', [])
        if branches:
            cols = st.columns(min(len(branches), 3))
            for idx, branch in enumerate(branches):
                with cols[idx % 3]:
                    with st.expander(f"{branch.get('name', 'Branch')}", expanded=(idx == 0)):
                        for sub in branch.get('subtopics', []):
                            st.markdown(f"• {sub}")

def add_ai_logo_to_sidebar():
    """Add AI logo to the top of sidebar"""
    st.sidebar.markdown("""
    <div class="ai-logo">
        <div class="ai-logo-text">
            🤖 AI <span style="font-size: 18px;">Smart Assistant</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")


def get_comprehensive_college_quizzes():
    """Return comprehensive college quizzes with complete answers"""
    return [
        {
            "id": 1,
            "title": "Database Management Systems",
            "questions": [
                {"question": "What does SQL stand for?", "options": ["Structured Query Language", "Simple Query Language", "System Query Language", "Standard Query Language"], "correct": 0, "explanation": "SQL stands for Structured Query Language, used to communicate with databases."},
                {"question": "What is a primary key?", "options": ["Unique identifier for each record", "Foreign key reference", "Index for faster queries", "Constraint for null values"], "correct": 0, "explanation": "A primary key uniquely identifies each record in a database table."},
                {"question": "What is normalization?", "options": ["Organizing data to reduce redundancy", "Adding duplicate data", "Deleting data", "Backing up data"], "correct": 0, "explanation": "Normalization reduces data redundancy and improves data integrity."},
                {"question": "What is a foreign key?", "options": ["References primary key in another table", "Always unique", "Can be null", "Used for indexing"], "correct": 0, "explanation": "A foreign key establishes a link between two tables."},
                {"question": "What is ACID?", "options": ["Atomicity, Consistency, Isolation, Durability", "Atomic, Consistent, Isolated, Durable", "Access, Control, Integrity, Data", "All Commands In Database"], "correct": 0, "explanation": "ACID ensures reliable processing of database transactions."}
            ]
        },
        {
            "id": 2,
            "title": "Operating Systems",
            "questions": [
                {"question": "What is a process?", "options": ["Program in execution", "Program on disk", "Memory location", "CPU register"], "correct": 0, "explanation": "A process is a program that is currently being executed."},
                {"question": "What is deadlock?", "options": ["Processes waiting indefinitely", "Process completed", "Memory full", "CPU overload"], "correct": 0, "explanation": "Deadlock occurs when processes wait for resources held by each other."},
                {"question": "What is paging?", "options": ["Memory management scheme", "Page replacement", "Process scheduling", "File system"], "correct": 0, "explanation": "Paging divides memory into fixed-size blocks."},
                {"question": "What is a semaphore?", "options": ["Synchronization tool", "Variable type", "Memory unit", "File descriptor"], "correct": 0, "explanation": "Semaphores control access to shared resources."},
                {"question": "What is thrashing?", "options": ["Excessive paging", "Process termination", "Memory failure", "CPU error"], "correct": 0, "explanation": "Thrashing occurs when system spends more time paging than executing."}
            ]
        },
        {
            "id": 3,
            "title": "Computer Networks",
            "questions": [
                {"question": "What does TCP/IP stand for?", "options": ["Transmission Control Protocol/Internet Protocol", "Transfer Control Protocol", "Transmission Communication Protocol", "Transfer Communication Protocol"], "correct": 0, "explanation": "TCP/IP is the fundamental protocol suite for the Internet."},
                {"question": "What is an IP address?", "options": ["Unique identifier for network devices", "Web address", "Email identifier", "Domain name"], "correct": 0, "explanation": "IP address uniquely identifies devices on a network."},
                {"question": "What is DNS?", "options": ["Domain Name System", "Data Network Service", "Digital Name Server", "Domain Naming Service"], "correct": 0, "explanation": "DNS translates domain names to IP addresses."},
                {"question": "What is HTTP?", "options": ["HyperText Transfer Protocol", "High Transfer Text Protocol", "Hyper Transfer Text Protocol", "High Text Transfer Protocol"], "correct": 0, "explanation": "HTTP is used for transmitting web pages."},
                {"question": "What is a firewall?", "options": ["Network security system", "Virus scanner", "Web browser", "Email client"], "correct": 0, "explanation": "Firewall monitors and controls network traffic."}
            ]
        },
        {
            "id": 4,
            "title": "Web Development",
            "questions": [
                {"question": "What does HTML stand for?", "options": ["HyperText Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"], "correct": 0, "explanation": "HTML is the standard markup language for web pages."},
                {"question": "What is CSS used for?", "options": ["Styling web pages", "Database queries", "Server-side scripting", "Network protocols"], "correct": 0, "explanation": "CSS controls the presentation of HTML elements."},
                {"question": "What is JavaScript?", "options": ["Programming language for web", "Database system", "Server software", "Markup language"], "correct": 0, "explanation": "JavaScript adds interactivity to web pages."},
                {"question": "What is React?", "options": ["JavaScript library for UIs", "Database system", "Backend framework", "CSS framework"], "correct": 0, "explanation": "React builds component-based user interfaces."},
                {"question": "What is REST API?", "options": ["Architectural style for web services", "Database protocol", "Programming language", "Web server"], "correct": 0, "explanation": "REST API enables client-server communication using HTTP."}
            ]
        },
        {
            "id": 5,
            "title": "Software Engineering",
            "questions": [
                {"question": "What is Agile?", "options": ["Iterative development approach", "Waterfall model", "Spiral model", "V-model"], "correct": 0, "explanation": "Agile focuses on iterative development with collaboration."},
                {"question": "What is a sprint?", "options": ["Time-boxed development cycle", "Code compilation", "Testing phase", "Deployment phase"], "correct": 0, "explanation": "A sprint is a fixed time period for completing work."},
                {"question": "What is unit testing?", "options": ["Testing individual components", "Testing entire system", "User testing", "Performance testing"], "correct": 0, "explanation": "Unit testing verifies individual code units."},
                {"question": "What is version control?", "options": ["System tracking code changes", "Database management", "Testing framework", "Deployment tool"], "correct": 0, "explanation": "Version control manages changes to source code."},
                {"question": "What is CI/CD?", "options": ["Continuous Integration/Deployment", "Code Integration/Deployment", "Continuous Implementation/Delivery", "Code Implementation/Delivery"], "correct": 0, "explanation": "CI/CD automates building, testing, and deployment."}
            ]
        }
    ]


def school_student_dashboard():
    """Dashboard for school students"""
    add_ai_logo_to_sidebar()
    
    st.markdown(f'<div class="main-header"><h1>📚 Welcome, {st.session_state.username}!</h1><p>School Student Dashboard</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### 👨‍🎓 {st.session_state.username}")
        st.markdown("---")
        
        menu = st.radio("Navigation", 
                       ["📖 Study Materials", "⏰ Exam Time Chart", "📊 Progress", "🤖 AI Learning"])
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['authenticated', 'username', 'role', 'show_register', 'registration_success']:
                if key in st.session_state:
                    st.session_state[key] = None if key != 'show_register' else False
            st.rerun()
    
    if menu == "📖 Study Materials":
        st.header("📖 Download Study Materials")
        subject = st.selectbox("Select Subject", Config.SCHOOL_SUBJECTS)
        materials = api.get_school_study_materials(subject)
        
        if materials:
            for topic, pdf_data in materials.items():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{topic}**")
                    with col2:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=f"{topic}.pdf",
                            mime="application/pdf",
                            key=f"download_{topic}"
                        )
        else:
            st.info("Materials coming soon for this subject!")
    
    elif menu == "⏰ Exam Time Chart":
        st.header("📅 Exam Preparation Schedule")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📅 Daily Schedule", "📊 Weekly Plan", "🎯 Study Goals", "📈 Progress Tracking"])
        
        with tab1:
            st.markdown("### ⏰ Daily Study Schedule")
            
            daily_schedule = [
                {"time": "6:00 AM - 7:00 AM", "activity": "🌅 Morning Revision", "details": "Review yesterday's topics"},
                {"time": "7:00 AM - 8:00 AM", "activity": "🍳 Breakfast & Break", "details": "Refresh your mind"},
                {"time": "8:00 AM - 10:00 AM", "activity": "📖 Core Subject Study", "details": "Focus on difficult topics"},
                {"time": "10:00 AM - 10:30 AM", "activity": "☕ Short Break", "details": "Rest and recharge"},
                {"time": "10:30 AM - 12:30 PM", "activity": "✍️ Practice Problems", "details": "Solve worksheets"},
                {"time": "12:30 PM - 2:00 PM", "activity": "🍽️ Lunch Break", "details": "Healthy meal & rest"},
                {"time": "2:00 PM - 4:00 PM", "activity": "🎯 Subject Practice", "details": "Apply concepts"},
                {"time": "4:00 PM - 4:30 PM", "activity": "🧘 Evening Break", "details": "Stretch & refresh"},
                {"time": "4:30 PM - 6:30 PM", "activity": "📚 Revision & Notes", "details": "Make summary notes"},
                {"time": "6:30 PM - 8:00 PM", "activity": "🏃 Free Time", "details": "Hobbies & relaxation"},
                {"time": "8:00 PM - 10:00 PM", "activity": "🎯 Mock Tests", "details": "Practice under time limit"},
                {"time": "10:00 PM", "activity": "😴 Bed Time", "details": "Get 8 hours of sleep"}
            ]
            
            for slot in daily_schedule:
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 2])
                    with col1:
                        st.markdown(f"<div class='time-slot'>{slot['time']}</div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**{slot['activity']}**")
                    with col3:
                        st.markdown(f"<small>{slot['details']}</small>", unsafe_allow_html=True)
                    st.markdown("---")
        
        with tab2:
            st.markdown("### 📊 Weekly Study Plan")
            
            weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
            subjects = ["Mathematics", "Science", "English", "Social Studies", "Computer Science"]
            
            study_data = pd.DataFrame({
                'Subject': subjects,
                'Week 1': [4, 3, 2, 2, 1],
                'Week 2': [4, 3, 2, 2, 2],
                'Week 3': [5, 4, 3, 3, 2],
                'Week 4': [5, 4, 3, 3, 3]
            })
            
            fig = px.imshow(
                study_data[weeks].T,
                x=subjects,
                y=weeks,
                labels=dict(x="Subjects", y="Week", color="Study Hours"),
                title="Weekly Study Intensity (Hours per day)",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 📅 Detailed Weekly Schedule")
            
            weekly_schedule = {
                "Monday": ["Mathematics", "Science", "Practice", "Revision"],
                "Tuesday": ["English", "Social Studies", "Computer Science", "Practice"],
                "Wednesday": ["Mathematics", "Science", "English", "Mock Test"],
                "Thursday": ["Social Studies", "Computer Science", "Mathematics", "Revision"],
                "Friday": ["Science", "English", "Practice", "Doubt Clearing"],
                "Saturday": ["Full Syllabus Revision", "Mock Test", "Error Analysis", "Weak Topic Focus"],
                "Sunday": ["Light Revision", "Rest & Recreation", "Plan Next Week", "Goal Setting"]
            }
            
            for day, topics in weekly_schedule.items():
                with st.expander(f"📌 {day}"):
                    cols = st.columns(4)
                    for i, topic in enumerate(topics):
                        with cols[i]:
                            st.markdown(f"**{topic}**")
                            st.markdown(f"🕒 {2 + i} hours")
            
            st.markdown("#### 💪 Weekly Motivation")
            st.info("""
            🎯 **Week 1-2:** Focus on understanding concepts
            📈 **Week 3:** Increase practice and problem-solving
            🏆 **Week 4:** Take full-length mock tests and analyze performance
            """)
        
        with tab3:
            st.markdown("### 🎯 Study Goals & Milestones")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Short-term Goals (Daily)")
                daily_goals = [
                    "Complete 2 chapters",
                    "Solve 20 practice problems",
                    "Revise 1 previous topic",
                    "Take 1 mini test"
                ]
                for goal in daily_goals:
                    st.checkbox(goal, key=f"daily_{goal}")
            
            with col2:
                st.markdown("#### Long-term Goals (Weekly)")
                weekly_goals = [
                    "Complete 3 subjects",
                    "Score 80% in mock test",
                    "Finish all assignments",
                    "Create revision notes"
                ]
                for goal in weekly_goals:
                    st.checkbox(goal, key=f"weekly_{goal}")
            
            st.markdown("### 📊 Goal Progress Tracker")
            
            goal_progress = {
                "Chapters Completed": 15,
                "Practice Problems": 245,
                "Mock Tests Taken": 8,
                "Revision Hours": 32
            }
            
            for goal, value in goal_progress.items():
                st.markdown(f"**{goal}:** {value}")
                st.progress(min(value/100, 1.0))
        
        with tab4:
            st.markdown("### 📈 Progress Tracking Dashboard")
            
            progress_data = pd.DataFrame({
                'Subject': Config.SCHOOL_SUBJECTS,
                'Progress': [75, 60, 85, 40, 50],
                'Target': [100, 100, 100, 100, 100]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Current Progress', x=progress_data['Subject'], y=progress_data['Progress'], marker_color='#667eea'))
            fig.add_trace(go.Bar(name='Target', x=progress_data['Subject'], y=progress_data['Target'], marker_color='#e0e0e0'))
            fig.update_layout(title="Subject-wise Progress", barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### ⏰ Weekly Study Hours")
            hours_data = pd.DataFrame({
                'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'Hours': [4, 5, 3, 6, 4, 7, 2]
            })
            
            fig = px.line(hours_data, x='Day', y='Hours', title="Study Hours Tracker", markers=True)
            fig.update_traces(line_color='#667eea', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📚 Topics Completed", "24/40", "60%")
            with col2:
                st.metric("⏰ Total Study Hours", "128 hrs", "+12 this week")
            with col3:
                st.metric("📝 Tests Taken", "12", "+3 this week")
            with col4:
                st.metric("📈 Average Score", "75%", "+5%")
    
    elif menu == "📊 Progress":
        st.header("📊 Your Progress")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Subjects Completed", "3/5")
        with col2:
            st.metric("⏰ Study Hours", "45 hrs")
        with col3:
            st.metric("📝 Tests Taken", "12")
        
        progress_data = pd.DataFrame({
            'Subject': Config.SCHOOL_SUBJECTS,
            'Progress': [75, 60, 85, 40, 50]
        })
        fig = px.bar(progress_data, x='Subject', y='Progress', 
                    title="Subject-wise Progress", color='Progress')
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "🤖 AI Learning":
        tab1, tab2 = st.tabs(["📚 Content & Mindmap", "🎯 Quiz Generator"])
        with tab1:
            display_ai_content_generator("school")
        with tab2:
            display_ai_quiz_generator()


def college_student_dashboard():
    """Dashboard for college students"""
    add_ai_logo_to_sidebar()
    
    st.markdown(f'<div class="main-header"><h1>🎓 Welcome, {st.session_state.username}!</h1><p>College Student Dashboard</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### 👨‍🎓 {st.session_state.username}")
        st.markdown("---")
        
        menu = st.radio("Navigation", 
                       ["💼 Placement Guides", "📝 Quizzes", "💻 Project Solutions", "📊 Progress", "🤖 AI Learning"])
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['authenticated', 'username', 'role', 'show_register', 'registration_success']:
                if key in st.session_state:
                    st.session_state[key] = None if key != 'show_register' else False
            st.rerun()
    
    if menu == "💼 Placement Guides":
        st.header("💼 Placement Preparation Guides")
        guides = api.get_placement_guides()
        for guide_name, pdf_data in guides.items():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{guide_name}**")
                with col2:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=f"{guide_name.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"guide_{guide_name}"
                    )
    
    elif menu == "📝 Quizzes":
        st.header("📝 Practice Quizzes")
        
      
        if 'quiz_completed' not in st.session_state:
            st.session_state.quiz_completed = False
        
        if st.session_state.selected_quiz and not st.session_state.get('quiz_completed', False):
          
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("← Back", key="back_from_quiz", use_container_width=True):
                   
                    quiz_key = f"quiz_{st.session_state.selected_quiz['id']}"
                    if quiz_key in st.session_state.quiz_answers_store:
                        del st.session_state.quiz_answers_store[quiz_key]
                    st.session_state.selected_quiz = None
                    st.session_state.quiz_completed = False
                    st.rerun()
            
            st.markdown("---")
            display_quiz(st.session_state.selected_quiz)
        
        elif st.session_state.selected_quiz and st.session_state.get('quiz_completed', False):
           
            if st.button("← Back to All Quizzes", key="back_after_quiz", use_container_width=True):
                st.session_state.selected_quiz = None
                st.session_state.quiz_completed = False
                st.rerun()
        
        else:
            all_quizzes = get_comprehensive_college_quizzes()
            
            if st.session_state.quiz_history:
                with st.expander("📜 Your Quiz History"):
                    history_df = pd.DataFrame(st.session_state.quiz_history[-10:])
                    st.dataframe(history_df, use_container_width=True)
            
          
            for i, quiz in enumerate(all_quizzes):
                if i % 2 == 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.container():
                            st.markdown(f"### {quiz['title']}")
                            st.markdown(f"📊 {len(quiz['questions'])} Questions | ⏱️ {len(quiz['questions']) * 2} minutes")
                            if st.button(f"Start {quiz['title']}", key=f"start_quiz_{quiz['id']}"):
                               
                                quiz_key = f"quiz_{quiz['id']}"
                                if quiz_key in st.session_state.quiz_answers_store:
                                    del st.session_state.quiz_answers_store[quiz_key]
                                st.session_state.selected_quiz = quiz
                                st.session_state.quiz_completed = False
                                st.rerun()
                            st.markdown("---")
                    if i + 1 < len(all_quizzes):
                        next_quiz = all_quizzes[i + 1]
                        with col2:
                            with st.container():
                                st.markdown(f"### {next_quiz['title']}")
                                st.markdown(f"📊 {len(next_quiz['questions'])} Questions | ⏱️ {len(next_quiz['questions']) * 2} minutes")
                                if st.button(f"Start {next_quiz['title']}", key=f"start_quiz_{next_quiz['id']}"):
                                    quiz_key = f"quiz_{next_quiz['id']}"
                                    if quiz_key in st.session_state.quiz_answers_store:
                                        del st.session_state.quiz_answers_store[quiz_key]
                                    st.session_state.selected_quiz = next_quiz
                                    st.session_state.quiz_completed = False
                                    st.rerun()
                                st.markdown("---")
    
    elif menu == "💻 Project Solutions":
        st.header("💻 Real-time Project Examples")
        projects = api.get_project_solutions()
        for project in projects:
            with st.expander(f"📁 {project['title']}"):
                st.markdown(f"**Description:** {project['description']}")
                st.markdown(f"**Technologies:** {', '.join(project['technologies'])}")
                st.markdown(f"**Features:**")
                for feature in project['features']:
                    st.markdown(f"  • {feature}")
    
    elif menu == "📊 Progress":
        st.header("📊 Your Progress")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Projects Completed", "4/8")
        with col2:
            st.metric("📝 Quizzes Taken", len(st.session_state.quiz_history))
        with col3:
            st.metric("💼 Applications Sent", "15")
        
        if st.session_state.quiz_history:
            st.subheader("Quiz Performance Trend")
            quiz_df = pd.DataFrame(st.session_state.quiz_history)
            fig = px.line(quiz_df, x='date', y='percentage', title="Quiz Scores Over Time")
            st.plotly_chart(fig, use_container_width=True)
    
    elif menu == "🤖 AI Learning":
        tab1, tab2 = st.tabs(["📚 Content & Mindmap", "🎯 Quiz Generator"])
        with tab1:
            display_ai_content_generator("college")
        with tab2:
            display_ai_quiz_generator()

def exam_aspirant_dashboard():
    """Dashboard for exam aspirants"""
    add_ai_logo_to_sidebar()
    
    st.markdown(f'<div class="main-header"><h1>🎯 Welcome, {st.session_state.username}!</h1><p>Exam Aspirant Dashboard</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### 👨‍🎓 {st.session_state.username}")
        st.markdown("---")
        
        menu = st.radio("Navigation", 
                       ["⏰ Time Charts", "💡 Quick Tips", "📝 Assessment Tests", "📊 Progress", "🤖 AI Learning"])
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['authenticated', 'username', 'role', 'show_register', 'registration_success']:
                if key in st.session_state:
                    st.session_state[key] = None if key != 'show_register' else False
            st.rerun()
    
    if menu == "⏰ Time Charts":
        st.header("⏰ Detailed Exam Preparation Time Charts")
        
        tab1, tab2, tab3 = st.tabs(["📊 Subject-wise Plan", "📅 Monthly Schedule", "🎯 Weekly Targets"])
        
        with tab1:
            st.markdown("### 📊 Comprehensive Subject-wise Study Plan")
            
            time_charts = api.get_subject_time_charts()
            
            for subject, details in time_charts.items():
                with st.expander(f"📚 {subject} - Detailed Plan", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📖 Topics to Cover")
                        for topic in details.get('Topics', []):
                            st.markdown(f"• {topic}")
                    
                    with col2:
                        st.markdown("#### ⏰ Time Allocation")
                        st.info(f"**Total:** {details.get('Time Allocation', 'N/A')}")
                        st.info(f"**Weekly:** {details.get('Weekly Plan', 'N/A')}")
                        st.info(f"**Daily:** {details.get('Daily Schedule', 'N/A')}")
        
        with tab2:
            st.markdown("### 📅 Monthly Study Calendar")
            
            months = ['January', 'February', 'March', 'April', 'May', 'June']
            subjects = ['Quantitative Aptitude', 'Logical Reasoning', 'English', 'General Knowledge']
            
            intensity_data = pd.DataFrame([
                [3, 4, 5, 4, 3, 2],
                [2, 3, 4, 4, 3, 2],
                [2, 2, 3, 3, 4, 3],
                [1, 2, 3, 4, 5, 5]
            ], index=subjects, columns=months)
            
            fig = px.imshow(intensity_data, 
                           labels=dict(x="Month", y="Subject", color="Study Hours"),
                           title="Monthly Study Intensity (Hours per day)",
                           color_continuous_scale="Viridis")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 📌 Important Milestones")
            milestones = {
                "Month 1-2": "Complete 50% syllabus",
                "Month 3-4": "Complete 80% syllabus + Start mock tests",
                "Month 5": "Revision + Intensive practice",
                "Month 6": "Full-length mock tests + Final revision"
            }
            
            for period, milestone in milestones.items():
                st.markdown(f"**{period}:** {milestone}")
        
        with tab3:
            st.markdown("### 🎯 Weekly Study Targets")
            
            weeks_data = []
            for week in range(1, 13):
                weeks_data.append({
                    'Week': f'Week {week}',
                    'Quantitative': min(25, week * 2),
                    'Reasoning': min(25, week * 2),
                    'English': min(25, week * 1.5),
                    'GK': min(25, week * 2)
                })
            
            weekly_df = pd.DataFrame(weeks_data)
            
            fig = px.line(weekly_df, x='Week', y=['Quantitative', 'Reasoning', 'English', 'GK'],
                         title="12-Week Study Plan Progress Tracker",
                         markers=True)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 📋 This Week's Study Plan")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Morning Session (6 AM - 12 PM)**")
                st.markdown("""
                - Monday: Quantitative Aptitude (Number System)
                - Tuesday: Logical Reasoning (Analytical)
                - Wednesday: Quantitative Aptitude (Algebra)
                - Thursday: English (Grammar)
                - Friday: Quantitative Aptitude (Geometry)
                - Saturday: General Knowledge (Current Affairs)
                - Sunday: Revision + Mock Test
                """)
            
            with col2:
                st.markdown("**Evening Session (2 PM - 8 PM)**")
                st.markdown("""
                - Monday: Logical Reasoning (Puzzles)
                - Tuesday: English (Vocabulary)
                - Wednesday: General Knowledge (History)
                - Thursday: Quantitative Aptitude (Statistics)
                - Friday: Logical Reasoning (Data Sufficiency)
                - Saturday: Practice Questions
                - Sunday: Error Analysis + Planning
                """)
            
            st.markdown("#### ✅ Weekly Checklist")
            checklist_items = [
                "Complete weekly targets for all subjects",
                "Take 2 full-length mock tests",
                "Analyze mistakes and note weak areas",
                "Revise previous week's topics",
                "Practice 50 questions per subject"
            ]
            
            for item in checklist_items:
                st.checkbox(item)
    
    elif menu == "💡 Quick Tips":
        st.header("💡 Comprehensive Exam Preparation Tips")
        
        tip_categories = {
            "📚 Study Strategies": [
                "Create a realistic study schedule and stick to it consistently",
                "Use the Pomodoro Technique: 25 minutes study, 5 minutes break",
                "Practice active recall instead of passive reading",
                "Make concise notes for quick revision before exams",
                "Use spaced repetition for better long-term retention"
            ],
            "⏰ Time Management": [
                "Prioritize topics based on weightage and difficulty",
                "Allocate more time to weak areas while maintaining strong ones",
                "Take regular breaks to avoid burnout (5 min every hour)",
                "Set daily, weekly, and monthly goals",
                "Use time-blocking technique for different subjects"
            ],
            "📝 Practice Techniques": [
                "Solve previous year question papers (last 5 years)",
                "Take weekly mock tests under exam conditions",
                "Analyze mistakes and maintain an error log",
                "Focus on accuracy before speed",
                "Practice time-bound question solving"
            ],
            "🧠 Memory Enhancement": [
                "Use mnemonics and visualization techniques",
                "Create mind maps for complex topics",
                "Teach concepts to others to reinforce learning",
                "Use flashcards for formulas and facts",
                "Connect new information with known concepts"
            ],
            "💪 Health & Wellness": [
                "Get 7-8 hours of quality sleep daily",
                "Stay hydrated and eat brain-healthy foods",
                "Exercise or meditate for 30 minutes daily",
                "Take short walks during study breaks",
                "Avoid caffeine and heavy meals before study sessions"
            ],
            "🎯 Exam Strategy": [
                "Read all questions before starting the exam",
                "Attempt easy questions first, then difficult ones",
                "Manage time by allocating minutes per question",
                "Don't spend too much time on one question",
                "Review answers if time permits"
            ]
        }
        
        for category, tips in tip_categories.items():
            st.markdown(f"## {category}")
            for tip in tips:
                st.markdown(f"💡 {tip}")
            st.markdown("---")
        
        import random
        motivational_quotes = [
            "Success is the sum of small efforts, repeated day in and day out.",
            "The expert in anything was once a beginner.",
            "Don't study until you get it right, study until you can't get it wrong.",
            "Your future self will thank you for the hard work you do today.",
            "Consistency is more important than intensity."
        ]
        quote = random.choice(motivational_quotes)
        st.info(f"✨ **Quote of the Day:** {quote}")
    
    elif menu == "📝 Assessment Tests":
        st.header("📝 Assessment Tests")
        tests = api.get_assessment_tests()
        
        if st.session_state.current_test:
            st.markdown("---")
            display_assessment_test(st.session_state.current_test)
            if st.button("← Back to Tests", use_container_width=True):
             
                for key in list(st.session_state.test_answers_store.keys()):
                    if key.startswith("test_"):
                        del st.session_state.test_answers_store[key]
                st.session_state.current_test = None
                st.rerun()
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Quantitative", "🧠 Reasoning", "📖 English", "🎯 Full Mock"])
            
            with tab1:
                test = tests[0]
                with st.expander(f"📋 {test['name']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Questions", len(test['questions']))
                    with col2:
                        st.metric("Duration", test['duration'])
                    with col3:
                        st.metric("Difficulty", test['difficulty'])
                    
                    if st.button(f"Start {test['name']}", key="start_quant", use_container_width=True):
                        st.session_state.current_test = test
                        st.rerun()
            
            with tab2:
                test = tests[1]
                with st.expander(f"📋 {test['name']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Questions", len(test['questions']))
                    with col2:
                        st.metric("Duration", test['duration'])
                    with col3:
                        st.metric("Difficulty", test['difficulty'])
                    
                    if st.button(f"Start {test['name']}", key="start_reasoning", use_container_width=True):
                        st.session_state.current_test = test
                        st.rerun()
            
            with tab3:
                test = tests[2]
                with st.expander(f"📋 {test['name']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Questions", len(test['questions']))
                    with col2:
                        st.metric("Duration", test['duration'])
                    with col3:
                        st.metric("Difficulty", test['difficulty'])
                    
                    if st.button(f"Start {test['name']}", key="start_english", use_container_width=True):
                        st.session_state.current_test = test
                        st.rerun()
            
            with tab4:
                test = tests[3]
                with st.expander(f"📋 {test['name']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Questions", len(test['questions']))
                    with col2:
                        st.metric("Duration", test['duration'])
                    with col3:
                        st.metric("Difficulty", test['difficulty'])
                    
                    if st.button(f"Start {test['name']}", key="start_mock", use_container_width=True):
                        st.session_state.current_test = test
                        st.rerun()
    
    elif menu == "📊 Progress":
        st.header("📊 Your Preparation Progress")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Topics Covered", "45/120")
        with col2:
            st.metric("📝 Tests Taken", "8")
        with col3:
            st.metric("⏰ Study Hours", "120 hrs")
        
        subjects = list(api.get_subject_time_charts().keys())
        progress = [65, 45, 70, 50]
        
        progress_df = pd.DataFrame({
            'Subject': subjects,
            'Progress': progress
        })
        
        fig = px.bar(progress_df, x='Subject', y='Progress', 
                    title="Subject-wise Preparation Progress",
                    color='Progress',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    elif menu == "🤖 AI Learning":
        tab1, tab2 = st.tabs(["📚 Content & Mindmap", "🎯 Quiz Generator"])
        with tab1:
            display_ai_content_generator("aspirant")
        with tab2:
            display_ai_quiz_generator()



def main_app():
    """Main application router"""
    apply_background()  
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.role == "school":
            school_student_dashboard()
        elif st.session_state.role == "college":
            college_student_dashboard()
        elif st.session_state.role == "aspirant":
            exam_aspirant_dashboard()
        else:
            st.error("Invalid role detected!")
            if st.button("Logout"):
                for key in ['authenticated', 'username', 'role']:
                    st.session_state[key] = None
                st.rerun()

if __name__ == "__main__":
    main_app()