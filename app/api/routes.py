import json
import os
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from app.config import Config
from typing import Dict, List, Any, Optional 

class API:
    """API routes for handling data operations"""
    
    def __init__(self):
   
        self.gemini_available = False
        self.gemini_model = None
        
       
        self.chats_file = Config.CHATS_FILE
        self._ensure_chats_file()
        self._ensure_pdf_directory()
        self._init_gemini()
    
    def _ensure_chats_file(self):
        """Ensure the chats data file exists"""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        if not os.path.exists(self.chats_file):
            with open(self.chats_file, 'w') as f:
                json.dump([], f)
    
    def _ensure_pdf_directory(self):
        """Ensure PDF directory exists"""
        pdf_dir = os.path.join(Config.DATA_DIR, "pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        return pdf_dir
    
    def _load_chats(self):
        """Load chats from JSON file"""
        try:
            with open(self.chats_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_chats(self, chats):
        """Save chats to JSON file"""
        with open(self.chats_file, 'w') as f:
            json.dump(chats, f, indent=2)
    
    def save_chat_message(self, username, message, response, role):
        """Save chat interaction"""
        chats = self._load_chats()
        chat_entry = {
            "username": username,
            "role": role,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        chats.append(chat_entry)
        self._save_chats(chats)
    
    def get_user_chats(self, username):
        """Get chat history for a user"""
        chats = self._load_chats()
        return [chat for chat in chats if chat['username'] == username]
    
    def generate_pdf(self, title, content, filename):
        """Generate a real PDF file"""
        pdf_dir = self._ensure_pdf_directory()
        pdf_path = os.path.join(pdf_dir, filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
        story.append(Spacer(1, 20))
        
        for section in content:
            if isinstance(section, dict):
                story.append(Paragraph(section.get('title', ''), styles['Heading2']))
                story.append(Spacer(1, 10))
                for key, value in section.get('items', {}).items():
                    story.append(Paragraph(f"• <b>{key}</b>: {value}", styles['Normal']))
                    story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(section, styles['Normal']))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        return pdf_path
    
    
    def get_school_study_materials(self, subject):
        """Get study materials for school students with real PDFs for ALL subjects"""
        materials_content = {
            "Mathematics": {
                "Algebra": {
                    "title": "Algebra Study Guide",
                    "content": [
                        {"title": "Chapter 1: Linear Equations", 
                         "items": {
                             "Definition": "Linear equations are equations of the first degree",
                             "Examples": "2x + 3 = 7, 5y - 2 = 13",
                             "Solution Methods": "Isolation method, Substitution method",
                             "Practice Problems": "1) 3x + 5 = 20, 2) 2y - 7 = 11"
                         }},
                        {"title": "Chapter 2: Quadratic Equations",
                         "items": {
                             "Standard Form": "ax² + bx + c = 0",
                             "Quadratic Formula": "x = [-b ± √(b² - 4ac)] / 2a",
                             "Discriminant": "D = b² - 4ac",
                             "Nature of Roots": "If D>0: Real roots, D=0: Equal roots, D<0: No real roots"
                         }},
                        {"title": "Chapter 3: Polynomials",
                         "items": {
                             "Degree": "Highest power of variable",
                             "Types": "Linear, Quadratic, Cubic",
                             "Operations": "Addition, Subtraction, Multiplication"
                         }}
                    ]
                },
                "Geometry": {
                    "title": "Geometry Fundamentals",
                    "content": [
                        {"title": "Basic Shapes",
                         "items": {
                             "Triangle": "Area = ½ × base × height, Sum of angles = 180°",
                             "Circle": "Area = πr², Circumference = 2πr",
                             "Rectangle": "Area = length × width, Perimeter = 2(l+w)",
                             "Square": "Area = side², Perimeter = 4 × side"
                         }},
                        {"title": "Important Theorems",
                         "items": {
                             "Pythagorean Theorem": "a² + b² = c² (for right triangles)",
                             "Angle Sum Property": "Sum of angles in triangle = 180°",
                             "Circle Theorems": "Angle in semicircle = 90°"
                         }}
                    ]
                },
                "Calculus": {
                    "title": "Introduction to Calculus",
                    "content": [
                        {"title": "Differentiation",
                         "items": {
                             "Derivative": "Rate of change of a function",
                             "Basic Rules": "d/dx(x^n) = nx^(n-1)",
                             "Applications": "Finding maxima/minima, velocity, acceleration"
                         }},
                        {"title": "Integration",
                         "items": {
                             "Integral": "Area under a curve",
                             "Basic Rules": "∫x^n dx = x^(n+1)/(n+1) + C",
                             "Applications": "Area, volume, work done"
                         }}
                    ]
                }
            },
            "Science": {
                "Physics": {
                    "title": "Physics Fundamentals",
                    "content": [
                        {"title": "Newton's Laws of Motion",
                         "items": {
                             "First Law": "Law of Inertia - Objects resist change in motion",
                             "Second Law": "F = ma (Force = mass × acceleration)",
                             "Third Law": "Action-Reaction - Every action has equal opposite reaction"
                         }},
                        {"title": "Work, Energy & Power",
                         "items": {
                             "Work": "W = F × d × cosθ",
                             "Kinetic Energy": "KE = ½mv²",
                             "Potential Energy": "PE = mgh",
                             "Power": "P = W/t"
                         }},
                        {"title": "Electricity",
                         "items": {
                             "Ohm's Law": "V = IR",
                             "Resistance": "R = ρL/A",
                             "Power": "P = VI = I²R"
                         }}
                    ]
                },
                "Chemistry": {
                    "title": "Chemistry Basics",
                    "content": [
                        {"title": "Atomic Structure",
                         "items": {
                             "Proton": "Positive charge, in nucleus",
                             "Neutron": "Neutral charge, in nucleus",
                             "Electron": "Negative charge, orbits nucleus"
                         }},
                        {"title": "Chemical Bonding",
                         "items": {
                             "Ionic Bond": "Transfer of electrons",
                             "Covalent Bond": "Sharing of electrons",
                             "Metallic Bond": "Sea of electrons"
                         }},
                        {"title": "Chemical Reactions",
                         "items": {
                             "Combination": "A + B → AB",
                             "Decomposition": "AB → A + B",
                             "Displacement": "A + BC → AC + B"
                         }}
                    ]
                },
                "Biology": {
                    "title": "Biology Essentials",
                    "content": [
                        {"title": "Cell Structure",
                         "items": {
                             "Nucleus": "Control center of cell",
                             "Mitochondria": "Power house of cell",
                             "Ribosomes": "Protein synthesis",
                             "Cell Membrane": "Semi-permeable barrier"
                         }},
                        {"title": "Human Body Systems",
                         "items": {
                             "Digestive System": "Breaks down food",
                             "Respiratory System": "Gas exchange",
                             "Circulatory System": "Transport of nutrients"
                         }}
                    ]
                }
            },
            "English": {
                "Grammar": {
                    "title": "English Grammar Guide",
                    "content": [
                        {"title": "Parts of Speech",
                         "items": {
                             "Noun": "Person, place, or thing",
                             "Verb": "Action or state of being",
                             "Adjective": "Describes noun",
                             "Adverb": "Describes verb"
                         }},
                        {"title": "Tenses",
                         "items": {
                             "Present": "I eat, I am eating, I have eaten",
                             "Past": "I ate, I was eating, I had eaten",
                             "Future": "I will eat, I will be eating, I will have eaten"
                         }}
                    ]
                },
                "Literature": {
                    "title": "Literature Study Guide",
                    "content": [
                        {"title": "Literary Devices",
                         "items": {
                             "Metaphor": "Direct comparison",
                             "Simile": "Comparison using 'like' or 'as'",
                             "Personification": "Giving human qualities to objects"
                         }},
                        {"title": "Writing Skills",
                         "items": {
                             "Essay Writing": "Introduction, Body, Conclusion",
                             "Letter Writing": "Formal and informal letters",
                             "Story Writing": "Plot, characters, setting, theme"
                         }}
                    ]
                }
            },
            "Social Studies": {
                "History": {
                    "title": "World History",
                    "content": [
                        {"title": "Ancient Civilizations",
                         "items": {
                             "Indus Valley": "Advanced urban planning",
                             "Egyptian": "Pyramids and hieroglyphics",
                             "Greek": "Democracy and philosophy"
                         }},
                        {"title": "Modern History",
                         "items": {
                             "Industrial Revolution": "Machines and factories",
                             "World Wars": "Global conflicts",
                             "Independence Movements": "Freedom from colonial rule"
                         }}
                    ]
                },
                "Geography": {
                    "title": "Geography Guide",
                    "content": [
                        {"title": "Physical Geography",
                         "items": {
                             "Mountains": "Fold mountains, volcanic mountains",
                             "Rivers": "Upper, middle, lower course",
                             "Climate": "Tropical, temperate, polar zones"
                         }},
                        {"title": "Human Geography",
                         "items": {
                             "Population": "Distribution and density",
                             "Urbanization": "City growth and planning",
                             "Resources": "Renewable and non-renewable"
                         }}
                    ]
                }
            },
            "Computer Science": {
                "Programming Basics": {
                    "title": "Programming Fundamentals",
                    "content": [
                        {"title": "Programming Concepts",
                         "items": {
                             "Variables": "Store data values",
                             "Data Types": "Integer, float, string, boolean",
                             "Control Structures": "If-else, loops, functions"
                         }},
                        {"title": "Algorithms",
                         "items": {
                             "Sorting": "Bubble sort, Quick sort",
                             "Searching": "Linear search, Binary search",
                             "Complexity": "Time and space complexity"
                         }}
                    ]
                },
                "Web Development": {
                    "title": "Web Development Basics",
                    "content": [
                        {"title": "HTML",
                         "items": {
                             "Tags": "html, head, body, div, p",
                             "Attributes": "class, id, src, href",
                             "Forms": "input, select, textarea"
                         }},
                        {"title": "CSS",
                         "items": {
                             "Selectors": "Element, class, ID selectors",
                             "Properties": "color, margin, padding, display",
                             "Layout": "Flexbox, Grid"
                         }}
                    ]
                }
            }
        }
        
        subject_data = materials_content.get(subject, {})
        if subject_data:
            pdf_files = {}
            for topic, content in subject_data.items():
                filename = f"{subject}_{topic}_{datetime.now().strftime('%Y%m%d')}.pdf"
                pdf_path = self.generate_pdf(content['title'], content['content'], filename)
                with open(pdf_path, 'rb') as f:
                    pdf_files[topic] = f.read()
            return pdf_files
        return {}
    
    def get_exam_time_chart(self):
        """Get exam preparation time chart"""
        return {
            "Daily Study Plan": {
                "Morning (6-8 AM)": "Revision & Practice",
                "Mid-Morning (9-12 PM)": "New Topics",
                "Afternoon (2-4 PM)": "Problem Solving",
                "Evening (5-7 PM)": "Mock Tests",
                "Night (8-10 PM)": "Light Revision"
            },
            "Weekly Schedule": {
                "Monday": "Mathematics",
                "Tuesday": "Science",
                "Wednesday": "English",
                "Thursday": "Social Studies",
                "Friday": "Computer Science",
                "Saturday": "Practice Tests",
                "Sunday": "Revision & Rest"
            }
        }
    

    def get_placement_guides(self):
        """Get placement preparation guides with real PDFs"""
        guides_content = {
            "Resume Building": {
                "title": "Professional Resume Building Guide",
                "content": [
                    {"title": "Resume Sections",
                     "items": {
                         "Contact Info": "Name, phone, email, LinkedIn profile",
                         "Professional Summary": "2-3 sentences highlighting your profile",
                         "Education": "Degrees, institutions, GPA, relevant courses",
                         "Experience": "Internships, projects, work experience",
                         "Technical Skills": "Programming languages, tools, technologies",
                         "Achievements": "Awards, certifications, publications"
                     }},
                    {"title": "Tips for Success",
                     "items": {
                         "Length": "1 page for freshers, 2 pages for experienced",
                         "Format": "PDF format preferred for submission",
                         "Keywords": "Use ATS-friendly keywords from job description",
                         "Action Verbs": "Use strong action verbs (developed, managed, created)",
                         "Quantify": "Use numbers to show impact (increased by 20%)"
                     }}
                ]
            },
            "Aptitude Tests": {
                "title": "Aptitude Test Preparation Guide",
                "content": [
                    {"title": "Quantitative Aptitude",
                     "items": {
                         "Percentages": "Profit/Loss, Discount, Interest",
                         "Ratios": "Proportions, Mixtures, Partnerships",
                         "Averages": "Mean, Median, Mode",
                         "Time & Work": "Work efficiency, Pipes & cisterns",
                         "Time & Distance": "Speed, Distance, Time relationships"
                     }},
                    {"title": "Logical Reasoning",
                     "items": {
                         "Blood Relations": "Family tree problems",
                         "Syllogisms": "Deductive reasoning",
                         "Analogies": "Word and number analogies",
                         "Coding-Decoding": "Pattern recognition",
                         "Series Completion": "Number and letter series"
                     }}
                ]
            },
            "Technical Interviews": {
                "title": "Technical Interview Preparation",
                "content": [
                    {"title": "Data Structures",
                     "items": {
                         "Arrays": "Operations, sorting, searching",
                         "Linked Lists": "Singly, doubly, circular",
                         "Stacks & Queues": "LIFO and FIFO implementations",
                         "Trees": "Binary trees, BST, traversals",
                         "Graphs": "BFS, DFS, shortest path"
                     }},
                    {"title": "Algorithms",
                     "items": {
                         "Sorting": "Bubble, Quick, Merge, Heap sort",
                         "Searching": "Linear, Binary, Interpolation search",
                         "Dynamic Programming": "Memoization, tabulation",
                         "Greedy Algorithms": "Activity selection, Huffman coding"
                     }}
                ]
            },
            "HR Interview Tips": {
                "title": "HR Interview Success Guide",
                "content": [
                    {"title": "Common Questions",
                     "items": {
                         "Tell me about yourself": "30-second elevator pitch focusing on achievements",
                         "Strengths & Weaknesses": "Be honest but strategic with improvement plan",
                         "Why this company": "Show research and alignment with goals",
                         "Where do you see yourself in 5 years": "Show ambition and growth mindset",
                         "Why should we hire you": "Highlight unique value proposition"
                     }},
                    {"title": "Preparation Tips",
                     "items": {
                         "Company Research": "Know their products, culture, values",
                         "Dress Code": "Formal business attire",
                         "Body Language": "Maintain eye contact, sit straight",
                         "Follow-up": "Send thank you email within 24 hours",
                         "Questions to Ask": "Ask about growth, culture, expectations"
                     }}
                ]
            },
            "Group Discussion": {
                "title": "Group Discussion Mastery",
                "content": [
                    {"title": "GD Topics",
                     "items": {
                         "Current Affairs": "Politics, economy, technology trends",
                         "Abstract Topics": "Creative thinking and innovation",
                         "Case Studies": "Business scenarios and problem-solving",
                         "Controversial Topics": "Handle with maturity and facts"
                     }},
                    {"title": "Success Tips",
                     "items": {
                         "Initiate": "Start the discussion if you're confident",
                         "Listen Actively": "Acknowledge others' valid points",
                         "Be Relevant": "Stay on topic, avoid deviation",
                         "Summarize": "Conclude with key points discussed",
                         "Be Polite": "Don't interrupt, respect others"
                     }}
                ]
            }
        }
        
       
        pdf_guides = {}
        for guide_name, content in guides_content.items():
            filename = f"Placement_Guide_{guide_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            pdf_path = self.generate_pdf(content['title'], content['content'], filename)
            with open(pdf_path, 'rb') as f:
                pdf_guides[guide_name] = f.read()
        return pdf_guides
    
    def get_quizzes(self):
        """Get quizzes with actual questions"""
        return [
            {
                "id": 1,
                "title": "Data Structures Quiz",
                "questions": [
                    {
                        "question": "What is the time complexity of binary search?",
                        "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                        "correct": 1,
                        "explanation": "Binary search has O(log n) time complexity as it divides the search space in half each time."
                    },
                    {
                        "question": "Which data structure uses LIFO (Last In First Out)?",
                        "options": ["Queue", "Stack", "Array", "Linked List"],
                        "correct": 1,
                        "explanation": "Stack follows LIFO principle - last element added is first to be removed."
                    },
                    {
                        "question": "What is a hash table used for?",
                        "options": ["Sorting", "Searching", "Key-value storage", "Graph traversal"],
                        "correct": 2,
                        "explanation": "Hash tables store key-value pairs for efficient lookup with O(1) average time."
                    },
                    {
                        "question": "Which of the following is a linear data structure?",
                        "options": ["Tree", "Graph", "Array", "Hash Table"],
                        "correct": 2,
                        "explanation": "Array is a linear data structure where elements are stored in contiguous memory locations."
                    }
                ]
            },
            {
                "id": 2,
                "title": "Aptitude Test",
                "questions": [
                    {
                        "question": "If a car travels 60 km in 1 hour, how far will it travel in 2.5 hours?",
                        "options": ["120 km", "150 km", "180 km", "200 km"],
                        "correct": 1,
                        "explanation": "Speed = 60 km/h, Distance = Speed × Time = 60 × 2.5 = 150 km"
                    },
                    {
                        "question": "What is 15% of 200?",
                        "options": ["15", "20", "30", "35"],
                        "correct": 2,
                        "explanation": "15% of 200 = (15/100) × 200 = 30"
                    },
                    {
                        "question": "If 5 workers can complete a task in 10 days, how many workers needed to complete it in 5 days?",
                        "options": ["5", "7", "10", "12"],
                        "correct": 2,
                        "explanation": "Work = Workers × Days, so 5 × 10 = 50 worker-days. For 5 days: 50/5 = 10 workers"
                    },
                    {
                        "question": "What is the next number in the sequence: 2, 6, 12, 20, ?",
                        "options": ["28", "30", "32", "34"],
                        "correct": 1,
                        "explanation": "Pattern: 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30"
                    }
                ]
            },
            {
                "id": 3,
                "title": "Programming Concepts",
                "questions": [
                    {
                        "question": "What does OOP stand for?",
                        "options": ["Object-Oriented Programming", "Order of Operations", "Object Organization Protocol", "Output Optimization Process"],
                        "correct": 0,
                        "explanation": "OOP stands for Object-Oriented Programming, a programming paradigm based on objects."
                    },
                    {
                        "question": "Which of these is NOT an OOP concept?",
                        "options": ["Inheritance", "Polymorphism", "Encapsulation", "Compilation"],
                        "correct": 3,
                        "explanation": "Compilation is a process, not an OOP concept. The main OOP concepts are inheritance, polymorphism, encapsulation, and abstraction."
                    },
                    {
                        "question": "What is a constructor?",
                        "options": ["A function to destroy objects", "A special method to initialize objects", "A type of variable", "A loop structure"],
                        "correct": 1,
                        "explanation": "A constructor is a special method that is automatically called when an object is created to initialize it."
                    }
                ]
            }
        ]
    
    def evaluate_quiz(self, quiz_id, answers):
        """Evaluate quiz answers and return score"""
        quizzes = self.get_quizzes()
        quiz = next((q for q in quizzes if q['id'] == quiz_id), None)
        
        if not quiz:
            return None
        
        score = 0
        results = []
        
        for i, question in enumerate(quiz['questions']):
            is_correct = (answers.get(str(i)) == question['correct'])
            if is_correct:
                score += 1
            results.append({
                'question': question['question'],
                'user_answer': question['options'][answers.get(str(i), 0)],
                'correct_answer': question['options'][question['correct']],
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
        
        return {
            'score': score,
            'total': len(quiz['questions']),
            'percentage': (score / len(quiz['questions'])) * 100,
            'results': results
        }
    
    def get_project_solutions(self):
        """Get real-time project examples"""
        return [
            {
                "title": "E-commerce Website",
                "description": "Full-stack e-commerce solution with payment integration, user authentication, and product management.",
                "technologies": ["React", "Node.js", "MongoDB", "Express", "Stripe"],
                "features": ["User login/signup", "Product search/filter", "Shopping cart", "Payment gateway", "Order tracking", "Admin dashboard"],
                "github_link": "https://github.com/example/ecommerce",
                "demo_link": "https://ecommerce-demo.example.com"
            },
            {
                "title": "Chat Application",
                "description": "Real-time chat app with WebSocket, user rooms, and file sharing capabilities.",
                "technologies": ["Socket.io", "Express", "React", "MongoDB"],
                "features": ["Real-time messaging", "User rooms", "File sharing", "Message history", "Typing indicators", "Online status"],
                "github_link": "https://github.com/example/chatapp",
                "demo_link": "https://chat-demo.example.com"
            },
            {
                "title": "Task Management System",
                "description": "Project management tool with task assignment, deadlines, and progress tracking.",
                "technologies": ["Django", "PostgreSQL", "Bootstrap", "JavaScript", "Chart.js"],
                "features": ["Task creation/assignment", "Deadline tracking", "Progress reports", "Team collaboration", "File attachments", "Email notifications"],
                "github_link": "https://github.com/example/taskmanager",
                "demo_link": "https://tasks-demo.example.com"
            },
            {
                "title": "Weather App",
                "description": "Real-time weather application with location-based forecasts and interactive maps.",
                "technologies": ["React", "OpenWeather API", "Chart.js", "CSS3"],
                "features": ["Current weather", "5-day forecast", "Search by city", "Temperature conversion", "Weather maps", "Responsive design"],
                "github_link": "https://github.com/example/weatherapp",
                "demo_link": "https://youtu.be/sn6GLgaTY0M?si=-CfCb2HtbGcZZTlW"
            }
        ]
    
   
    def get_subject_time_charts(self):
        """Get time chart guidance for each subject"""
        return {
            "Quantitative Aptitude": {
                "Topics": ["Number System", "Algebra", "Geometry", "Trigonometry", "Statistics", "Probability"],
                "Time Allocation": "40 hours",
                "Weekly Plan": "8 hours/week for 5 weeks",
                "Daily Schedule": "2 hours daily for Math practice",
                "Important Chapters": ["Percentages", "Ratios", "Averages", "Time & Work", "Time & Distance"]
            },
            "Logical Reasoning": {
                "Topics": ["Analytical Reasoning", "Verbal Reasoning", "Data Sufficiency", "Blood Relations", "Syllogisms", "Coding-Decoding"],
                "Time Allocation": "30 hours",
                "Weekly Plan": "6 hours/week for 5 weeks",
                "Daily Schedule": "1.5 hours daily for Reasoning",
                "Important Chapters": ["Puzzles", "Seating Arrangement", "Direction Sense", "Clock & Calendar"]
            },
            "English": {
                "Topics": ["Vocabulary", "Grammar", "Reading Comprehension", "Sentence Correction", "Para Jumbles", "Cloze Test"],
                "Time Allocation": "25 hours",
                "Weekly Plan": "5 hours/week for 5 weeks",
                "Daily Schedule": "1 hour daily for English",
                "Important Chapters": ["Synonyms/Antonyms", "Idioms & Phrases", "Active/Passive Voice", "Direct/Indirect Speech"]
            },
            "General Knowledge": {
                "Topics": ["Current Affairs", "History", "Geography", "Polity", "Economics", "Science & Technology"],
                "Time Allocation": "35 hours",
                "Weekly Plan": "7 hours/week for 5 weeks",
                "Daily Schedule": "1.5 hours daily for GK",
                "Important Chapters": ["Indian Constitution", "World Organizations", "Awards & Honors", "Sports"]
            }
        }
    
    def get_quick_tips(self):
        """Get quick tips to cover syllabus"""
        return [
            "📅 Create a realistic study schedule and stick to it",
            "📝 Practice previous year question papers regularly",
            "🧠 Focus on understanding concepts, not memorization",
            "⏰ Take regular breaks using Pomodoro technique (25 min study, 5 min break)",
            "👥 Join study groups for collaborative learning",
            "🎯 Use mnemonic devices for memorizing facts",
            "🔄 Review and revise regularly (spaced repetition)",
            "📰 Stay updated with current affairs daily",
            "📊 Take weekly mock tests to track progress",
            "💪 Maintain a healthy lifestyle - exercise, sleep, and diet matter!",
            "📱 Use educational apps for on-the-go learning",
            "🎯 Set daily, weekly, and monthly goals",
            "📹 Watch video tutorials for difficult topics",
            "📚 Make your own notes for quick revision"
        ]
    
    def get_assessment_tests(self):
        """Get assessment tests for aspirants with actual questions"""
        return [
            {
                "id": 1,
                "name": "Quantitative Assessment",
                "questions": [
                    {
                        "question": "If 15% of x = 45, then x = ?",
                        "options": ["200", "250", "300", "350"],
                        "correct": 2,
                        "explanation": "15% of x = 45 → x × 15/100 = 45 → x = 45 × 100/15 = 300"
                    },
                    {
                        "question": "What is the average of first 10 natural numbers?",
                        "options": ["5", "5.5", "6", "6.5"],
                        "correct": 1,
                        "explanation": "Sum of first 10 natural numbers = 55, Average = 55/10 = 5.5"
                    },
                    {
                        "question": "If a : b = 2 : 3 and b : c = 4 : 5, find a : c",
                        "options": ["8:15", "6:15", "8:12", "6:12"],
                        "correct": 0,
                        "explanation": "a:b = 2:3 = 8:12, b:c = 4:5 = 12:15, therefore a:c = 8:15"
                    },
                    {
                        "question": "A train travels 360 km in 4 hours. What is its speed in m/s?",
                        "options": ["20 m/s", "25 m/s", "30 m/s", "35 m/s"],
                        "correct": 1,
                        "explanation": "Speed = 360/4 = 90 km/h = 90 × 5/18 = 25 m/s"
                    },
                    {
                        "question": "If 20 workers can complete a work in 15 days, how many workers needed to complete it in 10 days?",
                        "options": ["25", "30", "35", "40"],
                        "correct": 1,
                        "explanation": "Work = 20 × 15 = 300 worker-days, Workers needed = 300/10 = 30 workers"
                    }
                ],
                "duration": "45 minutes",
                "difficulty": "Medium",
                "topics": ["Arithmetic", "Algebra", "Averages", "Ratio & Proportion"]
            },
            {
                "id": 2,
                "name": "Reasoning Assessment",
                "questions": [
                    {
                        "question": "If 'MAN' is coded as 'NBO', how is 'BOY' coded?",
                        "options": ["CPZ", "CPY", "COZ", "BPZ"],
                        "correct": 0,
                        "explanation": "Each letter is replaced by the next letter: M→N, A→B, N→O, so BOY→CPZ"
                    },
                    {
                        "question": "Find the odd one out: Apple, Mango, Orange, Banana, Potato",
                        "options": ["Apple", "Potato", "Banana", "Orange"],
                        "correct": 1,
                        "explanation": "Potato is a vegetable, all others are fruits"
                    },
                    {
                        "question": "If 3 + 4 = 21, 5 + 6 = 55, then 4 + 5 = ?",
                        "options": ["20", "36", "45", "41"],
                        "correct": 1,
                        "explanation": "Pattern: (3+4)×3 = 21, (5+6)×5 = 55, (4+5)×4 = 36"
                    },
                    {
                        "question": "Complete the series: 2, 6, 12, 20, ?",
                        "options": ["28", "30", "32", "34"],
                        "correct": 1,
                        "explanation": "Pattern: 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30"
                    }
                ],
                "duration": "30 minutes",
                "difficulty": "Medium",
                "topics": ["Coding-Decoding", "Series", "Odd One Out", "Pattern Recognition"]
            },
            {
                "id": 3,
                "name": "English Proficiency",
                "questions": [
                    {
                        "question": "Choose the correct spelling:",
                        "options": ["Accommodate", "Acommodate", "Accommodate", "Acomodate"],
                        "correct": 0,
                        "explanation": "Accommodate has double 'c' and double 'm'"
                    },
                    {
                        "question": "Select the synonym of 'Happy':",
                        "options": ["Sad", "Joyful", "Angry", "Tired"],
                        "correct": 1,
                        "explanation": "Joyful means feeling happiness"
                    },
                    {
                        "question": "Fill in the blank: She ______ to the store yesterday.",
                        "options": ["go", "goes", "went", "going"],
                        "correct": 2,
                        "explanation": "Past tense of go is went"
                    },
                    {
                        "question": "Identify the antonym of 'Increase':",
                        "options": ["Grow", "Rise", "Decrease", "Expand"],
                        "correct": 2,
                        "explanation": "Decrease is the opposite of increase"
                    }
                ],
                "duration": "40 minutes",
                "difficulty": "Easy",
                "topics": ["Vocabulary", "Grammar", "Spelling", "Synonyms/Antonyms"]
            },
            {
                "id": 4,
                "name": "Full Mock Test",
                "questions": [
                    {
                        "question": "What is the value of sin 90°?",
                        "options": ["0", "1", "-1", "Not defined"],
                        "correct": 1,
                        "explanation": "sin 90° = 1"
                    },
                    {
                        "question": "Who wrote 'Mahabharata'?",
                        "options": ["Valmiki", "Tulsidas", "Ved Vyasa", "Kalidas"],
                        "correct": 2,
                        "explanation": "Mahabharata was written by Maharishi Ved Vyasa"
                    },
                    {
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Madrid", "Paris"],
                        "correct": 3,
                        "explanation": "Paris is the capital of France"
                    },
                    {
                        "question": "Which of the following is not a programming language?",
                        "options": ["Python", "Java", "HTML", "C++"],
                        "correct": 2,
                        "explanation": "HTML is a markup language, not a programming language"
                    },
                    {
                        "question": "Who invented the light bulb?",
                        "options": ["Newton", "Einstein", "Edison", "Tesla"],
                        "correct": 2,
                        "explanation": "Thomas Edison invented the practical light bulb"
                    }
                ],
                "duration": "180 minutes",
                "difficulty": "Hard",
                "topics": ["All subjects covered - Mathematics, Reasoning, English, GK"]
            }
        ]
    
    def evaluate_assessment_test(self, test_id, answers):
        """Evaluate assessment test and return score"""
        tests = self.get_assessment_tests()
        test = next((t for t in tests if t['id'] == test_id), None)
        
        if not test:
            return None
        
        score = 0
        results = []
        
        for i, question in enumerate(test['questions']):
            user_answer = answers.get(str(i))
            is_correct = (user_answer == question['correct'])
            if is_correct:
                score += 1
            results.append({
                'question': question['question'],
                'user_answer': question['options'][user_answer] if user_answer is not None else "Not answered",
                'correct_answer': question['options'][question['correct']],
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
        
        return {
            'score': score,
            'total': len(test['questions']),
            'percentage': (score / len(test['questions'])) * 100,
            'results': results,
            'test_name': test['name']
        }
    
    
    
    def _init_gemini(self):
        """Initialize Gemini AI if available"""
        self.gemini_available = False
        self.gemini_model = None
        
        try:
            api_key = getattr(Config, 'GEMINI_API_KEY', None)
            
            if api_key and api_key.strip() and api_key != "AIzaSyDXyRJAMGDLiSo3M1vwRcz0BuGYnOqaADc":
                import google.generativeai as genai
                genai.configure(api_key=api_key.strip())
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_available = True
                print("✅ Gemini AI initialized successfully")
            else:
                print("⚠️ No valid Gemini API key found - using elaborate static content")
                self.gemini_available = False
        except Exception as e:
            print(f"⚠️ Gemini init error: {e} - using elaborate static content")
            self.gemini_available = False
    
    def generate_content_with_gemini(self, topic: str, level: str) -> Dict:
        """Generate elaborate study content"""
        if not hasattr(self, 'gemini_available') or self.gemini_model is None:
            self._init_gemini()
        
     
        return self._get_elaborate_static_content(topic, level)
    
    
    def _get_elaborate_static_content(self, topic: str, level: str) -> Dict:
        """ELABORATE PARAGRAPH-STYLE CONTENT for ANY topic at ANY level"""
        
        topic_capitalized = topic.title()
        level_lower = level.lower()
        
     
        if level_lower == "beginner":
            return {
                "overview": f"""## 🌟 Welcome to {topic_capitalized}! A Friendly Introduction

Have you ever wondered how things work in the world around you? {topic_capitalized} is your gateway to understanding an exciting and important field of knowledge. Whether you're curious about technology, science, business, or any other domain, {topic_capitalized} provides the foundation for deeper understanding.

**Why Should You Learn About {topic_capitalized}?** Every day, from the moment you wake up to when you go to sleep, {topic_capitalized} influences your life in ways you might not even realize. The apps on your phone, the recommendations on Netflix, the weather forecast you check, and even the way your bank detects fraud - all of these rely on principles of {topic_capitalized}.

**The Magic of Learning:** When you begin studying {topic_capitalized}, you're not just memorizing facts. You're developing a new way of thinking - a framework for analyzing problems, identifying patterns, and creating solutions. These skills will serve you well in school, in your career, and in everyday decision-making.

**What Makes This Topic Special:** {topic_capitalized} connects to virtually every aspect of modern life. Artists use it to create stunning visual effects, doctors apply it to diagnose diseases, engineers rely on it to build bridges and buildings, and teachers use it to help students learn more effectively. No matter what career path interests you, understanding {topic_capitalized} will give you an advantage.

**Your Journey Begins Here:** This guide is designed specifically for beginners - no prior knowledge required! We'll start with the absolute basics and build up gradually. Each concept will be explained with real-world examples you can relate to. By the time you finish, you'll have a solid foundation in {topic_capitalized} and the confidence to explore further on your own.""",

                "key_concepts": [
                    f"**🔍 Concept 1: Observation and Pattern Recognition** - The first step in understanding {topic_capitalized} is simply paying attention to how it appears in the world around you. Notice patterns, ask questions about why things work the way they do, and stay curious. Every expert in {topic_capitalized} started exactly where you are now - by noticing something interesting and wanting to learn more.",
                    
                    f"**🎯 Concept 2: Building Block Thinking** - Complex ideas in {topic_capitalized} are built from simpler components. Think of it like building with LEGO bricks - you start with basic pieces, and as you learn how they connect, you can create increasingly complex structures. This guide will help you identify and master the fundamental building blocks of {topic_capitalized}.",
                    
                    f"**💪 Concept 3: Learning Through Practice** - Reading about {topic_capitalized} is valuable, but true understanding comes from active engagement. Try to apply what you learn, discuss concepts with others, and look for opportunities to use {topic_capitalized} in your daily life. Your brain builds stronger neural connections when you actively use new knowledge rather than just reading about it.",
                    
                    f"**🤝 Concept 4: Making Connections** - {topic_capitalized} doesn't exist in isolation. It connects to many subjects you may already know something about. Look for these connections - they serve as bridges that help new information cross into your existing knowledge framework more easily. The more connections you make, the stronger your understanding becomes."
                ],
                
                "detailed_notes": f"""
## 📚 Your Complete Beginner's Guide to {topic_capitalized}

### Why {topic_capitalized} Matters

We live in an age of information and rapid change. Every day, new discoveries are made, new technologies emerge, and new challenges arise. Understanding {topic_capitalized} gives you a framework for making sense of this complex world. Think of it as a pair of special glasses - once you put them on, you start seeing patterns and connections you never noticed before.

**The Real-World Impact:** Consider how {topic_capitalized} affects your daily routine. When you wake up to an alarm on your phone, when you check the weather before dressing, when you follow a recipe to make breakfast - all of these activities involve principles related to {topic_capitalized}. Understanding these principles helps you make better decisions, solve problems more effectively, and appreciate the technology and systems that surround you.

### The Learning Journey

Learning {topic_capitalized} is like climbing a mountain. From the bottom, the peak might seem impossibly far away. The key is not to focus on how far you have to go, but rather on taking the next step in front of you. Each small step builds on the previous one, and before you know it, you'll have covered significant ground.

**Week 1-2: Building Your Foundation** - During your first days of learning, focus on understanding the core vocabulary and most fundamental concepts of {topic_capitalized}. Don't worry about mastering everything - just aim for familiarity. Think of this as learning the alphabet before you try to write a novel.

**Week 3-4: Active Application** - Once you understand the basics, start looking for ways to apply your knowledge. This could be as simple as explaining a concept to a friend, finding examples of {topic_capitalized} in your environment, or working through practice problems. Active engagement transforms passive knowledge into usable skill.

**Week 5-8: Building Confidence** - As your understanding grows, take on slightly more challenging material. Connect new concepts to ones you already understand. Start seeing how different ideas in {topic_capitalized} relate to each other. This is where learning becomes genuinely exciting - you'll start seeing the bigger picture.

### Common Questions from Beginners

**"Is {topic_capitalized} difficult to learn?"** Like any worthwhile skill, {topic_capitalized} requires patience and consistent effort. However, millions of people have successfully learned {topic_capitalized} - and you can too. The difficulty is not in the concepts themselves, but in building new mental habits and ways of thinking.

**"How long will it take me to become proficient?"** This depends on your goals and how much time you can dedicate. You can grasp the fundamentals in a few weeks of consistent study. Developing deeper expertise takes longer - measured in months or years rather than weeks. But remember: every hour you invest builds toward your understanding.

**"What if I make mistakes?"** Celebrate your mistakes! Every error teaches you something valuable. The most successful people in any field, including {topic_capitalized}, have made countless mistakes - they just didn't let those mistakes stop them from continuing to learn and grow.

### Your Path to Success

The single most important factor in learning {topic_capitalized} isn't innate intelligence or talent - it's consistency. Studying for 30 minutes every single day is far more effective than studying for 5 hours once a week. Make learning {topic_capitalized} a daily habit, and you'll be amazed at your progress over time.

**Create a Learning Routine:** Set aside a specific time each day for studying {topic_capitalized}. Morning works well for many people, as your mind is fresh. Others prefer evening study sessions. Choose whatever time works best for you, but stick to it consistently.

**Find Your Learning Community:** Learning with others accelerates progress and makes the journey more enjoyable. Join online forums, find study partners, or participate in local meetups related to {topic_capitalized}. Explaining concepts to others is one of the most effective ways to deepen your own understanding.""",

                "examples": [
                    f"**📱 Example 1: {topic_capitalized} in Your Smartphone** - Every time you use facial recognition to unlock your phone, {topic_capitalized} is at work. The phone's camera captures an image of your face, software analyzes specific features (distance between your eyes, shape of your jawline, etc.), and compares this information to stored data. All of this happens in less than a second! This same technology is used in security systems, photo organization apps, and even some medical diagnostic tools.",
                    
                    f"**🎬 Example 2: {topic_capitalized} in Entertainment** - When Netflix recommends a show you might enjoy, when Spotify creates a personalized playlist, or when YouTube suggests videos similar to ones you've watched - that's {topic_capitalized} in action. These systems analyze your viewing or listening history, identify patterns in your preferences, and compare your behavior to millions of other users to make accurate predictions about what you'll enjoy.",
                    
                    f"**🏥 Example 3: {topic_capitalized} in Healthcare** - Doctors use principles of {topic_capitalized} to diagnose diseases more accurately and quickly. By analyzing medical images like X-rays or MRIs, computer systems can identify subtle patterns that might indicate early-stage cancer, often detecting problems before they would be visible to the human eye. This technology saves lives by enabling earlier intervention and treatment.",
                    
                    f"**🚗 Example 4: {topic_capitalized} in Transportation** - Self-driving cars represent one of the most exciting applications of {topic_capitalized}. Sensors on the vehicle collect massive amounts of data about the surrounding environment - other vehicles, pedestrians, traffic signals, road conditions. Sophisticated systems process this information in real-time to make driving decisions: when to stop, when to go, when to change lanes, and how to avoid obstacles."
                ],
                
                "practice_questions": [
                    "**Question 1:** Look around your home or workplace. Can you identify three different examples of how {topic_capitalized} is being used? Describe each one briefly.\n\n**Sample Answer:** Possible examples include your smartphone (apps and features), your computer (software and internet browsing), your smart TV (recommendation systems), your thermostat (automatic temperature control), or even your microwave (programmed cooking settings).",
                    
                    "**Question 2:** If you could use {topic_capitalized} to solve any problem in the world, what problem would you choose to solve and why? What would your solution look like?\n\n**Sample Answer:** This question encourages creative thinking. Students might suggest using {topic_capitalized} for climate change prediction, disease detection, traffic optimization, personalized education, or resource allocation for disaster relief.",
                    
                    "**Question 3:** Explain {topic_capitalized} to a friend who has never studied it before. Use an analogy or real-world example to help them understand why it's important and interesting.\n\n**Sample Answer:** Good analogies include comparing {topic_capitalized} to learning a new language (opens new ways to communicate), training a pet (providing examples until patterns are learned), or solving puzzles (breaking complex problems into manageable pieces)."
                ],
                
                "summary": f"""
## 🎯 Your Learning Roadmap for {topic_capitalized}

✅ **Start with Curiosity:** The very best learners are those who ask questions. Why does this work? How could I use this? What would happen if I tried something different? Cultivate your natural curiosity - it's your most powerful learning tool.

✅ **Build a Strong Foundation:** Don't rush past the basics. Understanding fundamental concepts thoroughly will make everything that follows much easier. Strong foundations support everything you'll build later.

✅ **Practice Actively and Regularly:** Reading about {topic_capitalized} is not enough. Write about it, discuss it with others, apply it to problems you encounter, and experiment with your own ideas. Active engagement transforms information into genuine understanding.

✅ **Connect Learning to Your Life:** Find ways that {topic_capitalized} relates to your existing interests, hobbies, and goals. Personal connections make learning more meaningful and memorable.

✅ **Join a Learning Community:** You don't have to learn alone! Find study groups, online forums, or local meetups focused on {topic_capitalized}. Learning with others provides motivation, support, and diverse perspectives.

✅ **Be Patient and Persistent:** Progress in learning is not always linear. Some days you'll feel like you're making great strides; other days you might feel stuck. Both experiences are completely normal. Keep going, and you will continue to grow.

**Your Next Step:** Choose one small action to take today - read an article, watch a video, explain {topic_capitalized} to someone, or try a simple practice exercise. That single step starts your journey toward understanding and mastery! 🌟"""
            }
        
      
        elif level_lower == "intermediate":
            return {
                "overview": f"""## 📊 Understanding {topic_capitalized} at an Intermediate Level

### Moving Beyond the Fundamentals

Congratulations on mastering the basics of {topic_capitalized}! You've built a solid foundation, and now it's time to deepen your understanding. At the intermediate level, we shift focus from "what" to "how" and "why." Instead of simply knowing that something works, you'll understand the mechanisms behind it, the trade-offs involved in different approaches, and the practical considerations that determine success in real-world applications.

### The Intermediate Mindset

Here's an important truth: beginners memorize facts, but intermediates understand systems. When you reach the intermediate level in {topic_capitalized}, you stop simply collecting information and start thinking critically. You can look at a complex problem, break it down into its component parts, analyze the relationships between those parts, and design effective solutions.

**What This Means for You:** At this level, {topic_capitalized} transforms from an academic subject into a practical tool. You'll develop the ability to:
- Analyze complex situations and identify the key factors that matter most
- Choose appropriate methods and approaches based on context and constraints
- Understand trade-offs between different options (speed vs. accuracy, simplicity vs. power, etc.)
- Implement solutions that work reliably in imperfect, real-world conditions
- Troubleshoot problems when things don't go as expected
- Communicate your reasoning and decisions effectively to others

These skills translate directly to career advancement, academic success, and successful personal projects. Employers consistently seek professionals who can apply {topic_capitalized} effectively, not just recite facts about it.

### The Value of Intermediate Knowledge

Companies across every industry pay premium salaries for professionals who have moved beyond basic familiarity with {topic_capitalized} to genuine working proficiency. Why? Because these individuals don't just know about {topic_capitalized} - they can use it to solve real problems, create value, and drive innovation. As you develop your intermediate skills, you're not just learning - you're investing in your future capabilities and career opportunities.""",

                "key_concepts": [
                    f"**🎯 Systems Thinking in {topic_capitalized}:** At the beginner level, you learned individual concepts. At the intermediate level, you learn how those concepts connect into systems. Every element of {topic_capitalized} relates to others - changing one thing affects many others. Understanding these relationships allows you to predict outcomes, diagnose problems, and design more elegant solutions. Systems thinking transforms you from someone who knows facts into someone who understands how things work.",
                    
                    f"**⚖️ Trade-offs and Decision Making:** In the real world, there is rarely a single 'correct' answer in {topic_capitalized}. Instead, you face trade-offs: speed versus accuracy, simplicity versus capability, cost versus quality, flexibility versus efficiency. Intermediate practitioners learn to evaluate these trade-offs systematically and make informed decisions based on specific contexts and priorities.",
                    
                    f"**🔧 Practical Application Frameworks:** Knowing theory is valuable, but applying it effectively requires structured approaches. Intermediate {topic_capitalized} introduces frameworks and methodologies that guide you from problem identification through solution implementation. These frameworks provide step-by-step processes that have been refined through years of practical experience.",
                    
                    f"**📊 Evaluation and Metrics:** How do you know if your approach to a {topic_capitalized} problem is working? Intermediate practitioners define clear metrics, collect relevant data, and analyze results systematically. This scientific approach transforms {topic_capitalized} from art into engineering - measurable, improvable, and reliable.",
                    
                    f"**🔄 Iterative Improvement:** The best solutions rarely emerge perfectly formed. Intermediate practitioners embrace iteration: create an initial solution, gather feedback, analyze results, make improvements, and repeat. This cycle of continuous improvement leads to increasingly effective outcomes.",
                    
                    f"**🌐 Cross-Domain Connections:** {topic_capitalized} does not exist in isolation. Intermediate learners actively seek connections to other fields and disciplines. How does {topic_capitalized} apply to business? To science? To art? To social issues? These cross-domain insights often lead to breakthrough innovations and unique solutions that others miss."
                ],
                
                "abbreviations": f"""
## 📖 Key Terminology for Intermediate {topic_capitalized}

**Foundation Concept:** This represents the core building block of {topic_capitalized}. Understanding this term is essential because it appears throughout advanced discussions of the field. Professionals use this concept constantly to communicate complex ideas efficiently and precisely.

**Process Methodology:** This describes the structured approach to solving problems in {topic_capitalized}. When practitioners say they're "following this methodology," they're referring to a proven, step-by-step process that leads to reliable, reproducible results.

**Evaluation Framework:** How do you measure success in {topic_capitalized} applications? This framework provides specific metrics and assessment approaches. Without clear evaluation, improvement is guesswork rather than engineering.

**Optimization Technique:** Once you have a working solution, how do you make it better? Optimization techniques are systematic methods for improving speed, reducing resource consumption, or increasing accuracy in {topic_capitalized} applications.

**Edge Case Handling:** Real-world applications of {topic_capitalized} inevitably encounter unusual situations that don't fit standard patterns. These "edge cases" often reveal limitations and drive innovation. Identifying and properly handling edge cases separates intermediate practitioners from beginners.

**Scalability Consideration:** A solution that works well for small problems might fail completely when applied to larger ones. Scalability refers to how well {topic_capitalized} approaches perform as problem size grows. This is critical for real-world applications that must handle large-scale data or users.

**Robustness Engineering:** How well does your {topic_capitalized} solution handle unexpected inputs, changing conditions, or system errors? Robust systems continue functioning acceptably even when things go wrong. Building robustness requires intermediate-level thinking and techniques.

**Trade-off Analysis:** Every decision in {topic_capitalized} involves trade-offs between competing priorities. Trade-off analysis is the systematic evaluation of pros and cons to make informed decisions. This structured approach prevents oversight and hidden assumptions.""",
                
                "detailed_notes": f"""
## 📚 In-Depth Intermediate Guide to {topic_capitalized}

### Section 1: Transitioning from Theory to Practice

The journey from beginner to intermediate in {topic_capitalized} is marked by a fundamental shift: you stop learning ABOUT {topic_capitalized} and start DOING {topic_capitalized}. This transition requires three key changes in your approach:

**Change 1: Active Problem-Solving** - Beginners learn definitions and memorized examples. Intermediates take vague, messy real-world problems and transform them into specific, solvable challenges. When faced with "Improve customer satisfaction" or "Reduce manufacturing defects," an intermediate practitioner systematically breaks this down: What data do we have? What metrics will define success? What interventions can we test? This translation from fuzzy goals to concrete actions is the essence of applied {topic_capitalized}.

**Change 2: Embracing Constraints** - In academic settings, you typically have unlimited time, perfect data, and ideal conditions. Reality is different. Intermediates learn to work effectively within real constraints - limited time, imperfect data, budget restrictions, organizational politics, and technical limitations. Rather than complaining about constraints, they view them as creative challenges that often lead to innovative solutions.

**Change 3: Iterative Development** - Perfection is often the enemy of progress. Intermediates embrace "good enough for now, safe enough to try." They build minimum viable solutions, gather real-world feedback quickly, and improve continuously. This agile approach delivers value faster and adapts as conditions change.

### Section 2: The Intermediate Toolkit

**Tool 1: Problem Decomposition** - Any complex problem becomes manageable when broken into smaller pieces. Intermediates excel at decomposition: identifying sub-problems, understanding how they relate, prioritizing them appropriately, and solving them systematically.

**Tool 2: Pattern Recognition** - As you gain experience with {topic_capitalized}, you'll notice that similar patterns appear across different problems. Recognizing these patterns allows you to apply solutions you've used before, saving time and avoiding common pitfalls.

**Tool 3: Critical Evaluation** - Not every approach to a {topic_capitalized} problem is equally good. Intermediates develop the ability to critically evaluate different options, identifying strengths and weaknesses before committing significant resources.

**Tool 4: Communication and Documentation** - A solution that no one understands or can't be maintained has limited value. Intermediates learn to document their work clearly and communicate their reasoning effectively to both technical and non-technical audiences.

### Section 3: Common Intermediate Challenges

As you advance in {topic_capitalized}, you'll encounter new types of challenges:

**The Complexity Trap** - It's tempting to add features, handle more cases, and build more sophisticated solutions. However, complexity increases costs and failure risks. Learning when "good enough" is truly good enough is a crucial intermediate skill.

**The Analysis Paralysis** - With more knowledge comes awareness of more options and considerations. Some intermediates get stuck trying to find the perfect approach. Learning to make timely decisions with available information is essential.

**The Confidence Gap** - As you learn more, you also become more aware of what you don't know. This can temporarily reduce confidence. Remember: this awareness is actually a sign of growth, not a problem to be solved.""",

                "examples": [
                    f"**🏢 Business Application:** A retail company uses {topic_capitalized} to optimize inventory management. By analyzing sales data, seasonal patterns, and supply chain variables, they reduce stockouts by 30% while decreasing inventory holding costs by 15%. This translates to millions in annual savings and improved customer satisfaction.",
                    
                    f"**🔬 Research Application:** Scientists apply {topic_capitalized} to analyze genomic data, identifying genetic markers associated with disease risk. This research enables earlier intervention and personalized treatment plans, improving patient outcomes while reducing healthcare costs.",
                    
                    f"**💻 Technology Application:** A software company implements {topic_capitalized} techniques to personalize user experiences. By analyzing behavior patterns, they increase user engagement by 40% and reduce churn by 25%, directly impacting revenue and growth.",
                    
                    f"**🏭 Manufacturing Application:** A factory uses {topic_capitalized} for predictive maintenance, analyzing sensor data to predict equipment failures before they occur. This reduces unplanned downtime by 50% and extends equipment life by 20%, generating substantial cost savings."
                ],
                
                "practice_questions": [
                    "**Question 1:** Describe a real-world problem that could be addressed using {topic_capitalized}. What data would you need? What approach would you take? How would you measure success?\n\n**Answer Framework:** Identify a specific problem, list required data sources, outline a solution approach with key steps, define measurable success metrics, and anticipate potential challenges.",
                    
                    "**Question 2:** Compare two different approaches to solving a common {topic_capitalized} problem. What are the trade-offs between them? When would you choose one over the other?\n\n**Answer Framework:** Describe both approaches, list their respective advantages and disadvantages, discuss performance characteristics, and provide specific criteria for choosing between them.",
                    
                    "**Question 3:** How would you evaluate whether a {topic_capitalized} solution is working effectively? What metrics would you track, and how would you know if improvements are needed?\n\n**Answer Framework:** Define key performance indicators, establish baseline measurements, set target thresholds, describe monitoring processes, and outline response procedures for issues."
                ],
                
                "summary": f"""
## 🎯 Intermediate Mastery Checklist for {topic_capitalized}

✅ **Systems Thinking Applied:** You can analyze how different elements of {topic_capitalized} interact and affect each other, predicting outcomes and diagnosing problems systematically.

✅ **Trade-off Analysis:** You can evaluate different approaches, understanding their respective strengths and weaknesses, and make informed decisions based on context and priorities.

✅ **Practical Frameworks:** You have structured approaches for taking {topic_capitalized} problems from initial concept through implementation and evaluation.

✅ **Metrics-Driven:** You define clear success criteria, collect relevant data, and use evidence to guide decisions and improvements.

✅ **Iterative Approach:** You embrace continuous improvement, building solutions incrementally and refining based on real-world feedback.

✅ **Effective Communication:** You can explain {topic_capitalized} concepts and solutions clearly to both technical and non-technical audiences.

✅ **Constraint Navigation:** You work effectively within real-world limitations - time, budget, data quality, and organizational factors.

✅ **Continuous Learning:** You actively seek new knowledge, stay current with developments, and recognize that expertise is a journey, not a destination.

**Your Next Step:** Apply your intermediate {topic_capitalized} knowledge to a real project. Choose a problem that matters to you - at work, in your community, or for personal interest. Document your process, measure your results, and reflect on what you learn. Nothing builds skill like practical application!"""
            }
        
     
        else:  
            return {
                "overview": f"""## 🎓 Advanced {topic_capitalized}: Deep Expertise and Innovation

### The Expert's Perspective

You've reached an advanced level in {topic_capitalized} - congratulations! At this stage, you're not just applying existing knowledge; you're pushing boundaries, innovating, and contributing to the field itself. Advanced practitioners don't just solve problems - they identify which problems are worth solving, develop novel approaches, and advance the state of the art.

### What Advanced Expertise Enables

At the advanced level, {topic_capitalized} becomes a lens through which you can view virtually any challenge. You develop the ability to:

- **Identify opportunities** that others miss, seeing potential applications where others see only obstacles
- **Design novel solutions** that combine existing elements in creative new ways or invent entirely new approaches
- **Lead teams and projects**, guiding others and making strategic decisions about direction and resource allocation
- **Contribute to the field** through research, publications, open-source contributions, or innovative products
- **Mentor others**, accelerating their development and multiplying your impact
- **Navigate ambiguity**, making progress even when requirements are unclear or conditions are uncertain

### The Advanced Mindset

Advanced practitioners share several characteristics:

**Intellectual Curiosity** - They never stop learning, constantly exploring new developments at the intersection of {topic_capitalized} and other fields.

**Healthy Skepticism** - They question assumptions, including their own, and verify claims rather than accepting them at face value.

**Comfort with Uncertainty** - They acknowledge what they don't know and make decisions with incomplete information, updating as new evidence emerges.

**Systems Orientation** - They see beyond individual components to understand how entire systems behave, including unexpected emergent behaviors.

**Long-Term Perspective** - They balance short-term results with long-term capability building, investing in foundations while delivering immediate value.

**Collaborative Spirit** - They recognize that the most challenging problems require diverse perspectives and actively seek collaboration across disciplines.""",

                "advanced_concepts": [
                    f"**🏗️ Architectural Thinking:** Advanced practitioners design systems, not just solutions. This means considering not just immediate requirements but also future needs, scalability, maintainability, and evolution over time. Architectural thinking anticipates change rather than merely reacting to it.",
                    
                    f"**🔬 Research Methods:** Contributing to {topic_capitalized} requires rigorous research skills: formulating testable hypotheses, designing controlled experiments, collecting and analyzing data properly, and drawing valid conclusions. Advanced practitioners can evaluate research critically and conduct their own investigations.",
                    
                    f"**📊 Advanced Analytics:** Basic analysis answers \"what happened.\" Advanced analytics answers \"what will happen\" (prediction), \"what should we do\" (prescription), and \"why did this happen\" (causal inference). These capabilities transform data into strategic advantage.",
                    
                    f"**⚙️ Optimization at Scale:** Solutions that work for thousands may fail for millions. Advanced practitioners understand scalability challenges and optimization techniques that maintain performance as problems grow. This includes distributed systems, parallel processing, and algorithmic efficiency.",
                    
                    f"**🎯 Strategic Leadership:** Technical expertise alone is insufficient for maximum impact. Advanced practitioners develop leadership skills: setting vision, aligning stakeholders, managing resources, building teams, and navigating organizational dynamics.",
                    
                    f"**🔄 Innovation Processes:** Creating breakthrough solutions requires systematic innovation processes: identifying opportunities, generating possibilities, testing hypotheses, refining approaches, and scaling successes. Advanced practitioners don't wait for inspiration - they create conditions that breed innovation."
                ],
                
                "technical_terminology": f"""
## 📚 Advanced Terminology in {topic_capitalized}

**Emergent Behavior:** Complex systems often exhibit properties that aren't present in their individual components. Understanding emergence is crucial for predicting how {topic_capitalized} systems will behave in novel situations.

**Non-linear Dynamics:** Many {topic_capitalized} systems have non-linear relationships where small changes can produce disproportionately large effects (or vice versa). Advanced practitioners understand and work with these dynamics rather than being surprised by them.

**Trade-off Surface:** Rather than simple binary trade-offs, advanced problems involve multi-dimensional trade-off surfaces where optimizing one factor affects many others. Navigating these surfaces requires sophisticated analysis and judgment.

**Robustness-Fragility Trade-off:** Systems made robust to certain types of failures often become fragile to others. Understanding this relationship is crucial for designing resilient {topic_capitalized} solutions.

**Coupled vs. Decoupled Systems:** How components interact determines system behavior. Tight coupling enables efficiency but increases cascade risk. Loose coupling increases flexibility but may reduce performance. Advanced practitioners make intentional architectural choices about coupling.

**Antifragility:** Beyond robustness (resisting shocks) lies antifragility - systems that actually improve when stressed or challenged. This concept, while advanced, represents an emerging frontier in {topic_capitalized} system design.

**Red Teaming:** The practice of systematically challenging your own assumptions and solutions by actively trying to break them. Essential for identifying blind spots before they become problems.

**Second-Order Effects:** Every action has consequences, which have their own consequences. Advanced practitioners consider not just immediate effects but also the longer-term, indirect implications of their decisions.""",

                "research_notes": f"""
## 🔬 Current Research Directions in {topic_capitalized}

### Emerging Frontiers

The field of {topic_capitalized} continues to evolve rapidly. Several research directions hold particular promise:

**Interdisciplinary Integration:** The most exciting advances increasingly occur at the boundaries between {topic_capitalized} and other disciplines - biology, physics, social science, economics. Researchers who can bridge multiple domains are making breakthrough contributions.

**Explainable Systems:** As {topic_capitalized} systems become more powerful, understanding why they make particular decisions becomes more critical. Research into explainable, interpretable systems is advancing rapidly, driven by regulatory requirements and practical needs.

**Resource Efficiency:** The most sophisticated {topic_capitalized} solutions often require significant computational resources. Research into more efficient algorithms and architectures reduces environmental impact and enables broader access.

**Human-AI Collaboration:** Rather than fully automated systems, many successful applications combine human judgment with computational power. Understanding optimal collaboration patterns is an active research area.

### Open Problems

Despite significant progress, important challenges remain:

**Generalization vs. Specialization:** Systems that excel at specific tasks often fail when conditions change. Creating {topic_capitalized} solutions that generalize well across diverse situations without sacrificing specialized performance remains challenging.

**Causality vs. Correlation:** Most current approaches excel at finding correlations but struggle with establishing causation. Advancing causal inference methods would dramatically expand capabilities.

**Value Alignment:** Ensuring that {topic_capitalized} systems pursue goals aligned with human values, especially in novel situations not anticipated by designers, remains an unsolved challenge.

**Scalability Limitations:** Many promising approaches don't scale to real-world sizes, data volumes, or time constraints. Finding theoretically elegant solutions that also work practically at scale is an ongoing challenge.""",

                "advanced_examples": [
                    f"**🏥 Healthcare Innovation:** Advanced {topic_capitalized} is being used to discover new drugs by analyzing molecular structures and predicting how potential compounds will interact with disease targets. This approach reduces drug discovery timelines from years to months and has already produced treatments entering clinical trials.",
                    
                    f"**🌍 Climate Science:** Researchers apply advanced {topic_capitalized} techniques to climate modeling, improving prediction accuracy for extreme weather events, sea-level rise, and agricultural impacts. These models inform policy decisions worth billions and affect millions of lives.",
                    
                    f"**🔐 Cybersecurity:** Advanced {topic_capitalized} systems detect novel cyber threats by identifying behavioral anomalies rather than matching known attack signatures. This approach catches previously unknown attacks that traditional methods miss entirely.",
                    
                    f"**🚀 Space Exploration:** NASA and other space agencies use advanced {topic_capitalized} for mission planning, rover navigation, and astronomical data analysis. These systems operate autonomously in environments where real-time human control is impossible due to communication delays."
                ],
                
                "challenges": f"""
## ⚠️ Current Limitations and Open Challenges in {topic_capitalized}

### Technical Limitations

**Computational Requirements:** The most powerful {topic_capitalized} techniques often require massive computational resources, limiting accessibility and raising environmental concerns. Research into more efficient approaches is essential for democratizing access.

**Data Dependency:** Many advanced techniques require large, high-quality datasets that don't exist for many important problems. Developing methods that work well with limited or imperfect data remains an active research area.

**Interpretability Black Box:** Some powerful approaches produce results that even their creators struggle to explain. This lack of interpretability limits adoption in regulated domains like healthcare and finance where explanation is required.

**Brittleness:** Advanced systems sometimes fail catastrophically when encountering situations outside their training distribution, unlike simpler systems that fail more gracefully. Improving robustness without sacrificing performance is challenging.

### Practical Challenges

**Organizational Adoption:** Even technically superior solutions often fail due to organizational resistance, incentive misalignment, or implementation difficulties. Technical excellence alone is insufficient for real-world impact.

**Talent Scarcity:** Advanced {topic_capitalized} expertise remains rare and expensive. Organizations struggle to find and retain practitioners with deep skills, limiting what's possible regardless of technical potential.

**Ethical Considerations:** Powerful capabilities raise ethical concerns about privacy, bias, transparency, and accountability. Addressing these concerns requires not just technical solutions but also policy frameworks and organizational practices.

**Integration Complexity:** Advanced solutions don't operate in isolation - they must integrate with existing systems, processes, and workflows. Integration often consumes more time and resources than initial development.""",

                "future_trends": f"""
## 🔮 Future Trends and Emerging Directions

### Near-Term Developments (1-3 Years)

**Democratization of Advanced Tools:** What once required specialized expertise is becoming accessible through user-friendly platforms and services. This trend will continue, enabling more people to apply advanced {topic_capitalized} techniques.

**Regulatory Frameworks:** Governments worldwide are developing regulations for {topic_capitalized} applications, particularly in sensitive domains like healthcare, finance, and employment. Navigating these regulations will become an important skill.

**Hybrid Approaches:** Combining multiple techniques leverages their respective strengths while compensating for weaknesses. Hybrid approaches will become increasingly sophisticated and common.

### Mid-Term Developments (3-5 Years)

**Automated Machine Learning:** Systems that automatically select, configure, and optimize {topic_capitalized} approaches will reduce the expertise required for good results, further democratizing access.

**Edge Computing:** More processing will move to edge devices (phones, sensors, vehicles), reducing latency and privacy concerns while creating new architectural patterns.

**Continuous Learning:** Rather than static models, systems that continuously learn and adapt will become more common, better handling changing conditions and new information.

### Long-Term Possibilities (5-10+ Years)

**Artificial General Intelligence:** The ultimate long-term goal - systems that can perform any intellectual task that humans can. While significant challenges remain, steady progress continues toward this frontier.

**Scientific Discovery Acceleration:** {topic_capitalized} systems that generate and test hypotheses could dramatically accelerate scientific progress across all disciplines.

**Human-AI Symbiosis:** Rather than humans or AI alone, the most powerful future systems will combine human judgment with computational capabilities in seamless, intuitive partnerships.

**Constitutional AI:** Systems designed with explicit ethical frameworks and limitations, providing built-in safeguards against harmful applications or outcomes.""",

                "expert_questions": [
                    "**Question 1:** Analyze a current limitation in {topic_capitalized} and propose a research direction that could address it. What experiments would you conduct to test your hypothesis?\n\n**Answer Framework:** Identify specific limitation, explain why it matters, propose novel approach with theoretical basis, design experimental validation, discuss potential impact if successful.",
                    
                    "**Question 2:** Design a {topic_capitalized} system for a complex, high-stakes application (e.g., medical diagnosis, financial trading, autonomous vehicles). Address architecture, training data, validation, safety mechanisms, and fallback procedures.\n\n**Answer Framework:** Describe application context, propose system architecture, specify data requirements and collection strategy, design validation protocol, implement safety measures, plan for edge cases and failures.",
                    
                    "**Question 3:** Evaluate emerging trends in {topic_capitalized}. Which do you believe will have the most significant impact over the next five years, and why? What evidence supports your prediction?\n\n**Answer Framework:** Identify 2-3 emerging trends, evaluate their potential impact, cite supporting evidence (research papers, industry investments, early results), acknowledge uncertainties, explain reasoning for final assessment."
                ]
            }
    
    def generate_mindmap_with_gemini(self, topic: str) -> Dict:
        """Generate creative mindmap using Gemini AI"""
        if not hasattr(self, 'gemini_available') or self.gemini_model is None:
            self._init_gemini()
        
        if not self.gemini_available or self.gemini_model is None:
            return self._get_fallback_mindmap(topic)
        
        try:
            prompt = f"""Create a mindmap for "{topic}".

Return ONLY valid JSON:
{{
    "topic": "{topic}",
    "branches": [
        {{"name": "Branch 1", "subtopics": ["subtopic1", "subtopic2", "subtopic3"]}},
        {{"name": "Branch 2", "subtopics": ["subtopic1", "subtopic2", "subtopic3"]}},
        {{"name": "Branch 3", "subtopics": ["subtopic1", "subtopic2", "subtopic3"]}},
        {{"name": "Branch 4", "subtopics": ["subtopic1", "subtopic2"]}}
    ]
}}"""

            response = self.gemini_model.generate_content(prompt)
            
            text = response.text.strip()
            
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                mindmap = json.loads(json_str)
                return mindmap
            
            return self._get_fallback_mindmap(topic)
            
        except Exception as e:
            print(f"Mindmap error: {e}")
            return self._get_fallback_mindmap(topic)
    
    def generate_quiz_with_gemini(self, topic: str, num_questions: int = 10) -> Dict:
        """Generate quiz with questions"""
        if not hasattr(self, 'gemini_available') or self.gemini_model is None:
            self._init_gemini()
        
        if not self.gemini_available or self.gemini_model is None:
            return self._get_fallback_quiz(topic, num_questions)
        
        try:
            prompt = f"""Generate {num_questions} multiple choice questions about "{topic}".

Return ONLY valid JSON array:
[
    {{
        "question": "Question text?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct": 0,
        "explanation": "Explanation of the correct answer"
    }}
]"""

            response = self.gemini_model.generate_content(prompt)
            
            text = response.text.strip()
            
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            start = text.find('[')
            end = text.rfind(']') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                questions = json.loads(json_str)
                return {"topic": topic, "questions": questions[:num_questions]}
            
            return self._get_fallback_quiz(topic, num_questions)
            
        except Exception as e:
            print(f"Quiz error: {e}")
            return self._get_fallback_quiz(topic, num_questions)
    
    def get_ai_chat_response(self, message: str, role: str) -> str:
        """Get AI response for chat using Gemini"""
        if not hasattr(self, 'gemini_available') or self.gemini_model is None:
            self._init_gemini()
        
        if not self.gemini_available or self.gemini_model is None:
            return "I'm here to help! What would you like to learn about?"
        
        try:
            role_context = {
                "school": "a young school student (ages 12-16). Use simple, fun, encouraging language.",
                "college": "a college student. Provide detailed, practical, career-oriented explanations.",
                "aspirant": "an exam aspirant. Focus on exam strategies and key concepts."
            }
            
            prompt = f"""You are an AI academic assistant for {role_context.get(role, 'a student')}.

User question: {message}

Provide a helpful, accurate, and concise response. Be supportive and educational."""
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Chat error: {e}")
            return f"I'm here to help with your studies! What would you like to know about?"
    
  
    
    def _get_fallback_content(self, topic: str, level: str) -> Dict:
        """Fallback content - redirects to elaborate static content"""
        return self._get_elaborate_static_content(topic, level)
    
    def _get_genai_elaborate_content(self, topic: str, level: str) -> Dict:
        """Generative AI content redirect"""
        return self._get_elaborate_static_content(topic, level)
    
    def _get_python_elaborate_content(self, topic: str, level: str) -> Dict:
        """Python content redirect"""
        return self._get_elaborate_static_content(topic, level)
    
    def _get_ml_elaborate_content(self, topic: str, level: str) -> Dict:
        """Machine Learning content redirect"""
        return self._get_elaborate_static_content(topic, level)
    
    def _get_datascience_elaborate_content(self, topic: str, level: str) -> Dict:
        """Data Science content redirect"""
        return self._get_elaborate_static_content(topic, level)
    
    def _get_dynamic_elaborate_content(self, topic: str, level: str) -> Dict:
        """Dynamic content redirect"""
        return self._get_elaborate_static_content(topic, level)
    
    
    def _get_fallback_mindmap(self, topic: str) -> Dict:
        """Fallback mindmap when AI is unavailable"""
        return {
            "topic": topic,
            "branches": [
                {"name": "📖 Introduction", "subtopics": [f"What is {topic}?", f"History of {topic}", f"Why {topic} matters"]},
                {"name": "🎯 Core Concepts", "subtopics": [f"Key principles", f"Important theories", f"Fundamental rules"]},
                {"name": "💡 Applications", "subtopics": [f"Real-world uses", f"Examples in daily life", f"Industry applications"]},
                {"name": "📚 Study Resources", "subtopics": ["Recommended books", "Online courses", "Practice materials"]}
            ]
        }
    
    def _get_fallback_quiz(self, topic: str, num_questions: int) -> Dict:
        """Fallback quiz when AI is unavailable"""
        questions = []
        for i in range(min(num_questions, 5)):
            questions.append({
                "question": f"What is an important concept in {topic}?",
                "options": [f"Concept A", f"Concept B", f"Concept C", f"All of the above"],
                "correct": 3,
                "explanation": f"All of these concepts are important when studying {topic}."
            })
        return {"topic": topic, "questions": questions}
    