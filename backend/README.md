# SkillSnap Backend API

FastAPI-powered backend for the SkillSnap Voice Challenge platform with AI-powered voice analysis.

## 🚀 Quick Start

```bash
# Clone and navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run setup script (creates .env, initializes database)
python setup.py

# Set up PostgreSQL database (recommended)
python setup_postgresql.py

# Start the development server
python run.py
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## 🔧 Features

- **Voice Processing**: OpenAI Whisper for speech-to-text
- **AI Scoring**: OpenAI GPT + spaCy for comprehensive voice analysis
- **Voice Interactions**: Omnidimension SDK integration for automated calls
- **RESTful API**: Complete CRUD operations for challenges and candidates
- **Real-time Processing**: Background tasks for audio processing
- **Analytics**: Detailed scoring analytics and performance metrics

## 📋 API Endpoints

### Core Endpoints
- `GET /` - API info and health check
- `GET /health` - Service health status
- `GET /docs` - Interactive API documentation

### Challenges
- `GET /api/v1/challenges` - List all challenges
- `POST /api/v1/challenges` - Create new challenge
- `GET /api/v1/challenges/{id}` - Get challenge details
- `PUT /api/v1/challenges/{id}` - Update challenge
- `DELETE /api/v1/challenges/{id}` - Delete challenge

### Candidates & Submissions
- `GET /api/v1/candidates` - List candidates
- `POST /api/v1/candidates` - Create candidate
- `POST /api/v1/submissions` - Create submission
- `POST /api/v1/candidates/search` - Search with filters

### Voice Processing
- `POST /api/v1/voice/upload/{submission_id}` - Upload audio file
- `POST /api/v1/voice/transcribe` - Standalone transcription
- `GET /api/v1/voice/submission/{id}/status` - Check processing status

### AI Scoring
- `POST /api/v1/scoring/score-text` - Score text directly
- `POST /api/v1/scoring/rescore/{submission_id}` - Re-score submission
- `GET /api/v1/scoring/submission/{id}/analysis` - Detailed analysis

### Analytics
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/scoring/analytics/performance` - Performance metrics

## 🔑 API Keys Setup

### 1. OpenAI (Required)
**Free Tier**: $5 credit for new accounts

```bash
# Visit: https://platform.openai.com/api-keys
# 1. Sign up for OpenAI account
# 2. Go to API Keys section
# 3. Create new secret key
# 4. Add to .env file:
OPENAI_API_KEY=sk-your-key-here
```

### 2. Google Cloud Speech (Optional)
**Free Tier**: 60 minutes per month

```bash
# Visit: https://cloud.google.com/speech-to-text
# 1. Create Google Cloud account
# 2. Enable Speech-to-Text API
# 3. Create service account
# 4. Download JSON key file
# 5. Add to .env file:
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
```

### 3. Omnidimension SDK (Optional)
**Check their pricing page for free tier**

```bash
# Visit: https://omnidimension.com/developers
# 1. Sign up for developer account
# 2. Get API key from dashboard
# 3. Add to .env file:
OMNIDIMENSION_API_KEY=your-api-key-here
```

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── database.py            # Database connection and setup
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic request/response schemas
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script for initialization
├── routers/              # API route handlers
│   ├── challenges.py     # Challenge CRUD operations
│   ├── candidates.py     # Candidate and submission management
│   ├── voice.py         # Audio upload and processing
│   └── scoring.py       # AI scoring and analytics
└── services/            # Business logic services
    ├── whisper_service.py   # OpenAI Whisper integration
    ├── scoring_service.py   # AI scoring with GPT + spaCy
    └── voice_service.py     # Omnidimension SDK integration
```

## 🗄️ Database Setup

### PostgreSQL (Recommended for Production)

**Step 1: Install PostgreSQL**
```bash
# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# CentOS/RHEL/Fedora
sudo dnf install postgresql postgresql-server
sudo postgresql-setup --initdb
sudo systemctl start postgresql
```

**Step 2: Set up SkillSnap Database**
```bash
# Automated setup (recommended)
python setup_postgresql.py

# Manual setup
sudo -u postgres psql
CREATE DATABASE skillsnap;
CREATE USER skillsnap_user WITH PASSWORD 'skillsnap_password';
GRANT ALL PRIVILEGES ON DATABASE skillsnap TO skillsnap_user;
\q
```

**Step 3: Update Connection String**
The setup script will automatically update your `.env` file with:
```
DATABASE_URL=postgresql://skillsnap_user:skillsnap_password@localhost:5432/skillsnap
```

### SQLite (Development Only)
For development, you can use SQLite by changing the `.env` file:
```
DATABASE_URL=sqlite:///./skillsnap.db
```

### Database Migrations
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## 🛠 Development

### Environment Setup
1. Run setup script: `python setup.py`
2. Set up database: `python setup_postgresql.py`
3. Fill in your API keys in `.env`
4. Install dependencies: `pip install -r requirements.txt`

### Database Management
```bash
# Initialize database tables
python -c "from database import create_tables; import asyncio; asyncio.run(create_tables())"

# Reset database (caution: deletes all data)
python -c "from database import reset_database; import asyncio; asyncio.run(reset_database())"

# Check database health
python -c "from database import check_database_health; import asyncio; print(asyncio.run(check_database_health()))"
```

### Running Tests
```bash
pip install pytest pytest-asyncio
pytest
```

### Code Quality
```bash
# Format code
black .

# Sort imports  
isort .

# Lint code
flake8 .
```

## 🔊 Voice Processing Pipeline

1. **Audio Upload**: Client uploads audio file via `/voice/upload/{submission_id}`
2. **Quality Analysis**: Analyze audio quality using librosa
3. **Transcription**: Convert speech to text using OpenAI Whisper or Google Speech
4. **Linguistic Analysis**: Extract features using spaCy (word count, filler words, etc.)
5. **AI Scoring**: Score response using OpenAI GPT across 5 dimensions:
   - **Fluency** (25%): Speaking rate, pauses, filler words
   - **Confidence** (20%): Linguistic patterns, certainty markers
   - **Relevance** (25%): How well response addresses the prompt
   - **Clarity** (20%): Communication effectiveness
   - **Tone** (10%): Professional language and appropriateness

## 📊 Scoring Algorithm

### Overall Score Calculation
```python
overall_score = (
    fluency_score * 0.25 +
    confidence_score * 0.20 +
    relevance_score * 0.25 +
    clarity_score * 0.20 +
    tone_score * 0.10
)
```

### Individual Score Components

**Fluency Score**
- Optimal speaking rate: 120-180 WPM
- Penalty for excessive filler words
- Consideration of natural pauses

**Confidence Score**
- Word count indicates elaboration
- Vocabulary diversity
- Presence of uncertainty vs. confident markers

**Relevance Score**
- AI analysis of prompt adherence
- Technical accuracy for role-specific content

**Clarity Score**
- Communication effectiveness
- Sentence structure and coherence

**Tone Score**
- Professional language usage
- Appropriate formality level
- Positive vs. negative language patterns

## 🚀 Production Deployment

### Environment Variables
```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# PostgreSQL for production
DATABASE_URL=postgresql://skillsnap_user:skillsnap_password@localhost:5432/skillsnap

# Production API keys
OPENAI_API_KEY=your-production-openai-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/production/credentials.json
OMNIDIMENSION_API_KEY=your-production-omnidimension-key

# Performance settings
MAX_AUDIO_FILE_SIZE=26214400
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=5000
```

### PostgreSQL Production Setup
```bash
# Create production database
sudo -u postgres psql
CREATE DATABASE skillsnap_prod;
CREATE USER skillsnap_prod_user WITH PASSWORD 'secure_production_password';
GRANT ALL PRIVILEGES ON DATABASE skillsnap_prod TO skillsnap_prod_user;

# Configure connection pooling (recommended)
# Install pgbouncer for connection pooling
sudo apt install pgbouncer

# Update DATABASE_URL with connection pooling
DATABASE_URL=postgresql://skillsnap_prod_user:secure_password@localhost:6432/skillsnap_prod
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Checks
- `GET /health` - Overall system health
- `GET /scoring/health-check` - AI services availability

## 📈 Monitoring & Analytics

### API Usage Tracking
All API calls are logged with:
- Service name (OpenAI, Google, Omnidimension)
- Tokens used and cost estimates
- Response times and success rates
- Error tracking

### Performance Metrics
- Average processing time per audio file
- Transcription accuracy rates
- Scoring consistency metrics
- System resource usage

## 🔧 Troubleshooting

### Common Issues

**OpenAI API Errors**
```bash
# Check API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Rate limit exceeded - wait or upgrade plan
# Authentication failed - verify API key
```

**spaCy Model Missing**
```bash
python -m spacy download en_core_web_sm
```

**Database Connection Issues**
```bash
# SQLite permissions
chmod 644 skillsnap.db

# PostgreSQL connection
psql -h localhost -U user -d skillsnap
```

### Logs
```bash
# View application logs
tail -f app.log

# Check FastAPI logs
uvicorn main:app --log-level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 Email: support@skillsnap.com
- 📚 Documentation: API docs at `/docs`
- 🐛 Issues: GitHub Issues
- 💬 Discord: SkillSnap Community 