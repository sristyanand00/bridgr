# Bridgr - Career Development Platform

A comprehensive career development platform that bridges the gap between who you are and who you want to become.

## Project Structure

- **Frontend**: React application (Vite/React Scripts)
- **Backend**: FastAPI Python server with ML integration
- **ML Components**: Skill analysis, gap detection, career recommendations

## Setup Instructions

### 1. Required Accounts

Before starting, create accounts for these services:

1. **Anthropic** (Claude AI)
   - Visit: https://console.anthropic.com/
   - Create account and get API key
   - Required for AI-powered analysis and chat

2. **Supabase** (Database & Auth)
   - Visit: https://supabase.com/
   - Create new project
   - Get Project URL and Anon Key
   - Required for data storage and user authentication

### 2. Environment Setup

1. Clone the repository
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Fill in your API keys in `.env` file

### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Download O*NET dataset:
- Visit https://www.onetcenter.org/database.html
- Download the "Database 30.2" ZIP file
- Extract to `data/` directory as specified in config

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Running the Application

#### Development Mode:

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
# OR for Vite:
npm run dev
```

#### Quick Start Scripts:
```bash
# From project root
npm run dev:backend    # Starts backend server
npm run dev:frontend   # Starts frontend dev server
npm run dev:all        # Starts both (requires two terminals)
```

### 6. API Endpoints

Backend runs on `http://localhost:8000`
- `GET /` - API status
- `GET /health` - Health check
- `/api/analyze` - Resume/skill analysis
- `/api/chat` - AI chat interface
- `/api/roadmap` - Career roadmapping
- `/api/market-pulse` - Job market insights
- `/api/interview` - Interview preparation

Frontend runs on `http://localhost:3000` (React Scripts) or `http://localhost:5173` (Vite)

## Features

- **Resume Analysis**: Upload and analyze resumes for skill gaps
- **Career Roadmapping**: Generate personalized career development paths
- **Market Insights**: Real-time job market trends and demand analysis
- **AI Chat**: Claude-powered career advice and guidance
- **Interview Prep**: Practice questions and feedback

## Technology Stack

### Backend
- FastAPI (Python web framework)
- spaCy (NLP processing)
- Sentence Transformers (Semantic similarity)
- Scikit-learn (ML algorithms)
- Anthropic Claude (AI integration)
- Supabase (Database/Authentication)

### Frontend
- React 18
- Vite (Build tool)
- Modern CSS/JavaScript

### ML Components
- Semantic skill matching
- Gap analysis algorithms
- Market demand prediction
- Personalized recommendations

## Deployment

### Frontend (Vercel/Netlify)
1. Connect your GitHub repository
2. Configure build settings:
   - Build command: `cd frontend && npm run build`
   - Output directory: `frontend/build`

### Backend (Railway/Heroku)
1. Connect your GitHub repository
2. Set environment variables in platform settings
3. Configure start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure frontend URL is in `CORS_ORIGINS` in backend config
2. **API Key Errors**: Verify `.env` file has correct keys
3. **ML Model Loading**: Ensure O*NET dataset is properly extracted
4. **Port Conflicts**: Change ports if 8000/3000 are occupied

### Getting Help

- Check backend logs for detailed error messages
- Verify all environment variables are set
- Ensure all dependencies are installed
- Check network connectivity for external API calls

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

## License

MIT License - see LICENSE file for details
