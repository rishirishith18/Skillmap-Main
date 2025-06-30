# SkillSnap - Voice Challenge Platform

A modern AI-powered voice challenge platform for hiring, featuring both frontend and backend components with advanced voice recording capabilities.

## 🏗️ Project Structure

```
SkillMap-Main/
├── README.md                          # Project documentation
├── index.html                         # Main landing page
├── package.json                       # Frontend package configuration
├── package-lock.json                  # Package lock file
│
├── frontend/                          # Frontend application
│   ├── index.html                     # Frontend main page
│   ├── pages/                         # Page components
│   │   ├── candidate/                 # Candidate-specific pages
│   │   ├── recruiter/                 # Recruiter-specific pages
│   │   ├── voice/                     # Voice challenge pages
│   │   └── api-test.html             # API testing page
│   └── assets/                        # Static assets
│       ├── css/                       # Stylesheets
│       │   ├── main.css              # Main styles
│       │   ├── components.css        # Component styles
│       │   ├── responsive.css        # Responsive design
│       │   └── shared.css            # Shared styles
│       └── js/                        # JavaScript modules
│           ├── app.js                # Main application logic
│           ├── components.js         # UI components
│           ├── data.js               # Data management
│           ├── shared.js             # Shared utilities
│           ├── utils.js              # Utility functions
│           ├── voice-recorder.js     # Voice recording functionality
│           ├── omnidimension-core.js # Core AI integration
│           ├── omnidimension-integration.js # AI platform integration
│           ├── live-interview.js     # Live interview features
│           ├── recruiter-assistant.js # Recruiter tools
│           └── practice-assistant.js  # Practice mode features
│
├── backend/                           # Backend API server
│   ├── main.py                       # FastAPI main application
│   ├── run.py                        # Application runner
│   ├── config.py                     # Configuration settings
│   ├── database.py                   # Database connection
│   ├── models.py                     # Database models
│   ├── schemas.py                    # Pydantic schemas
│   ├── requirements.txt              # Python dependencies
│   ├── requirements-minimal.txt     # Minimal dependencies
│   ├── skillsnap.db                 # SQLite database
│   ├── setup_postgresql.py          # PostgreSQL setup
│   ├── simple_migration.py          # Database migrations
│   ├── add_candidate_password_migration.py # Password migration
│   ├── test_imports.py              # Import testing
│   ├── routers/                     # API route handlers
│   ├── services/                    # Business logic services
│   ├── uploads/                     # File upload storage
│   └── README.md                    # Backend documentation
│
├── fix_navigation.py                 # Navigation fix utility
├── quick_setup_pgadmin.sh           # pgAdmin quick setup
├── pgAdmin4_Setup_Guide.md          # pgAdmin setup guide
└── setup_database.sql               # Database setup script
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Modern web browser
- PostgreSQL (optional, SQLite included)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/rishirishith18/Skillmap-Main.git
   cd SkillMap-Main
   ```

2. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   python -m http.server 8080
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000

### Alternative Setup with npm
```bash
npm install
npm start  # Starts frontend on port 3000
npm run dev  # Starts frontend on port 8080
```

## ✨ Features

### 🎯 For Candidates
- **Voice Challenges**: Record responses to role-specific questions
- **Real-time Recording**: Advanced voice recording with timer and controls
- **Practice Mode**: Practice challenges with AI feedback
- **Personal Dashboard**: Track progress and view challenge history
- **Live Interviews**: Participate in real-time voice interviews
- **Performance Analytics**: Detailed scoring and improvement insights

### 👥 For Recruiters
- **Candidate Management**: Comprehensive candidate dashboard
- **Advanced Search**: Filter candidates by skills, scores, and criteria
- **Audio Playback**: Review candidate responses with enhanced controls
- **AI-Powered Scoring**: Automated assessment with detailed breakdowns
- **Live Interview Tools**: Conduct real-time voice interviews
- **Analytics Dashboard**: Performance metrics and hiring insights
- **Recruiter Assistant**: AI-powered recruitment recommendations

### 🤖 AI Integration
- **OmniDimension AI**: Advanced voice analysis and scoring
- **Real-time Processing**: Instant feedback and assessment
- **Multi-dimensional Analysis**: Communication, confidence, and technical skills
- **Bias-free Evaluation**: Objective, AI-driven candidate assessment

## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup and structure
- **CSS3** - Modern styling with Flexbox/Grid and responsive design
- **Vanilla JavaScript** - Modular ES6+ JavaScript
- **Web Audio API** - Advanced voice recording capabilities
- **Lucide Icons** - Beautiful, consistent iconography

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite/PostgreSQL** - Database options for development and production
- **Pydantic** - Data validation and serialization
- **Python 3.8+** - Core backend language

### AI & Voice Processing
- **OmniDimension AI** - Voice analysis and scoring platform
- **Web Audio API** - Browser-based voice recording
- **Real-time Processing** - Live audio analysis capabilities

## 📱 Responsive Design

Fully responsive design supporting:
- 🖥️ Desktop computers (1200px+)
- 📱 Mobile phones (320px+)
- 📟 Tablets (768px+)
- Dark/Light theme toggle

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
python -m http.server 8080
# or
npx http-server -p 8080
```

### Database Setup

**PostgreSQL (Production)**:
```bash
python backend/setup_postgresql.py
```

**SQLite (Development)**:
Database automatically created on first run.

### Running Migrations
```bash
cd backend
python simple_migration.py
python add_candidate_password_migration.py
```

## 📊 API Documentation

When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 Design System

### Color Palette
- **Primary Blue**: #2563eb
- **Success Green**: #16a34a  
- **Warning Yellow**: #ca8a04
- **Danger Red**: #dc2626
- **Purple**: #9333ea

### Typography
- **Font Family**: System fonts (SF Pro, Roboto, Segoe UI)
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## 🔐 Configuration

### Environment Variables
Create `.env` file in backend directory:
```env
DATABASE_URL=postgresql://user:password@localhost/skillsnap
SECRET_KEY=your-secret-key
AI_API_KEY=your-omnidimension-api-key
```

### Database Configuration
- **Development**: SQLite (automatic)
- **Production**: PostgreSQL (requires setup)

## 📈 Performance & Analytics

- **Voice Quality Analysis**: Real-time audio quality assessment
- **Response Time Tracking**: Measure candidate response times
- **Engagement Metrics**: Track user interaction patterns
- **Conversion Analytics**: Monitor candidate-to-hire success rates

## 🔮 Advanced Features

### Voice Recording Capabilities
- **High-quality Recording**: 44.1kHz sample rate
- **Real-time Visualization**: Audio waveform display
- **Noise Reduction**: Background noise filtering
- **Format Support**: WAV, MP3, and WebM formats

### AI-Powered Assessment
- **Communication Skills**: Clarity, pace, and articulation
- **Confidence Levels**: Voice tone and delivery analysis
- **Technical Accuracy**: Content relevance and correctness
- **Cultural Fit**: Communication style alignment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/backend/README.md` for detailed API docs
- **pgAdmin Setup**: See `pgAdmin4_Setup_Guide.md`
- **Issues**: Report bugs on GitHub Issues
- **Email**: Contact support for enterprise solutions

## 🔗 Links

- **Repository**: [https://github.com/rishirishith18/Skillmap-Main](https://github.com/rishirishith18/Skillmap-Main)
- **Live Demo**: Coming soon
- **API Docs**: http://localhost:8000/docs (when running)

---

**SkillSnap** - Revolutionizing hiring through AI-powered voice challenges. 🎤✨
