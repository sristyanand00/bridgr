# Backend Folder Structure

```
backend/
├── .env                           # Environment variables (API keys, paths)
├── __init__.py                    # Package initialization
├── __pycache__/                   # Python bytecode cache
├── main-simple.py                 # Simplified main entry point
├── main.py                        # Main FastAPI application entry point
├── main_minimal.py                # Minimal main entry point
├── requirements-compatible.txt    # Compatible Python dependencies
├── requirements-simple.txt         # Simple dependencies list
├── requirements.txt               # Full dependencies list
├── venv/                          # Virtual environment
│
├── core/                          # Core configuration and utilities
│   ├── __init__.py
│   ├── config.py                  # Settings and environment configuration
│   └── exceptions.py              # Custom exception classes
│
├── ml/                            # Machine learning components
│   ├── __init__.py
│   ├── dataset_loader.py          # O*NET dataset loading and processing
│   ├── gap_analyzer.py            # Skill gap analysis and prioritization
│   ├── model_loader.py            # ML model singleton management
│   ├── resume_parser.py           # PDF resume parsing
│   ├── similarity.py              # Skill matching and similarity calculation
│   └── skill_extractor.py         # Three-tier skill extraction from text
│
├── models/                        # Pydantic data models
│   ├── __init__.py
│   └── analysis.py                # Analysis result models and request/response schemas
│
├── routes/                        # API route handlers
│   ├── __init__.py
│   ├── analyze.py                 # Resume analysis endpoint
│   ├── chat.py                    # Career coaching chat endpoint
│   ├── interview.py               # Mock interview simulator
│   ├── market_pulse.py            # Market demand insights
│   └── roadmap.py                 # Learning roadmap generation
│
├── services/                      # Business logic services
│   ├── __init__.py
│   └── intelligence_core.py        # Main ML pipeline orchestrator
│
└── tests/                         # Test files
    └── __init__.py
```

## Key Components Overview

### **Core Layer** (`core/`)
- **config.py**: Environment settings, API keys, database URLs
- **exceptions.py**: Custom exception classes for consistent error handling

### **ML Layer** (`ml/`)
- **dataset_loader.py**: O*NET database loading, skill market demand calculation
- **gap_analyzer.py**: Skill gap analysis, learning time estimation, salary bands
- **model_loader.py**: Singleton pattern for ML model management
- **resume_parser.py**: PDF text extraction and section detection
- **similarity.py**: Semantic skill matching and transferable skill detection
- **skill_extractor.py**: Three-tier skill extraction (phrase, semantic, LLM)

### **Models Layer** (`models/`)
- **analysis.py**: Pydantic models for API requests/responses, data validation

### **Routes Layer** (`routes/`)
- **analyze.py**: Resume upload and analysis endpoint
- **chat.py**: Streaming career coaching with OpenAI
- **interview.py**: Mock interview question generation and evaluation
- **market_pulse.py**: Market demand data and salary insights
- **roadmap.py**: Personalized learning roadmap generation

### **Services Layer** (`services/`)
- **intelligence_core.py**: Main orchestrator that coordinates all ML components

## Data Flow

1. **Request** → Routes → Services → ML Components
2. **ML Pipeline**: Resume Parser → Skill Extractor → Dataset Loader → Gap Analyzer → Similarity Engine
3. **AI Integration**: OpenAI for chat, interview, and roadmap generation
4. **Response**: Structured AnalysisResult with all insights and recommendations

## Configuration Files

- **.env**: API keys (OpenAI, Supabase), dataset paths, ML thresholds
- **requirements-compatible.txt**: Dependencies compatible with Python 3.8+
- **main.py**: FastAPI app with CORS, middleware, and route registration
