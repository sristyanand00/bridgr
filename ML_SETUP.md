# ML Model Setup Guide

This guide covers setting up the ML components for Bridgr.

## ML Components Overview

The Bridgr platform uses several ML models and datasets:

1. **IntelligenceCore** - Main ML orchestrator
2. **spaCy NLP** - Text processing and entity extraction
3. **Sentence Transformers** - Semantic similarity analysis
4. **O*NET Dataset** - Career skills and job data
5. **Anthropic Claude** - AI-powered analysis and chat

## Setup Instructions

### 1. Python Dependencies

All ML dependencies are already in `backend/requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

Key ML packages:
- `spacy==3.7.4` - NLP processing
- `sentence-transformers==2.7.0` - Semantic similarity
- `scikit-learn==1.4.2` - ML algorithms
- `anthropic==0.26.0` - AI integration

### 2. Download spaCy Model

```bash
# Download the English language model
python -m spacy download en_core_web_sm
```

### 3. O*NET Dataset Setup

The O*NET dataset provides comprehensive career information:

1. **Download Dataset:**
   - Visit: https://www.onetcenter.org/database.html
   - Download "Database 30.2" (or latest version)
   - Choose the "Text" version (.zip file)

2. **Extract Dataset:**
   ```bash
   # Create data directories
   mkdir -p data/raw
   
   # Extract the downloaded ZIP to data/raw/
   # The path should match your .env configuration
   ```

3. **Update Environment:**
   Ensure your `.env` file has correct paths:
   ```env
   ONET_ZIP_PATH=data/raw/db_30_2_text.zip
   ONET_EXTRACT_PATH=data/
   ```

### 4. ML Model Configuration

The ML components are configured through environment variables:

```env
# Semantic similarity threshold (0.0-1.0)
SEMANTIC_THRESHOLD=0.75

# High demand job threshold (0.0-1.0)
HIGH_DEMAND_THRESHOLD=0.15

# Anthropic API key (required for AI features)
ANTHROPIC_API_KEY=your_key_here
```

### 5. ML Component Architecture

#### IntelligenceCore (`backend/services/intelligence_core.py`)
- Main orchestrator for all ML operations
- Loads and caches models at startup
- Coordinates between different ML components

#### Key ML Modules:
- `dataset_loader.py` - Loads and processes O*NET data
- `gap_analyzer.py` - Analyzes skill gaps
- `similarity.py` - Semantic similarity calculations
- `skill_extractor.py` - Extracts skills from text
- `resume_parser.py` - Parses resume documents

### 6. Testing ML Components

Test individual components:

```bash
cd backend

# Test spaCy NLP
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy working!')"

# Test sentence transformers
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); print('Transformers working!')"

# Test intelligence core
python -c "from backend.ml.model_loader import get_core; core = get_core(); print('ML Core loaded!')"
```

### 7. Performance Optimization

#### Model Loading
- Models are loaded once at startup and cached
- Use the development server to test loading times

#### Memory Usage
- Sentence Transformers model: ~500MB RAM
- spaCy model: ~50MB RAM
- O*NET dataset: ~100MB RAM (when loaded)

#### Production Considerations
- Consider using GPU for sentence transformers if available
- Implement model versioning for production updates
- Monitor memory usage and implement cleanup if needed

### 8. Troubleshooting

#### Common Issues:

1. **spaCy Model Not Found:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **O*NET Dataset Not Found:**
   - Verify the ZIP file path in `.env`
   - Ensure the dataset is properly extracted

3. **Memory Issues:**
   - Reduce semantic threshold to limit comparisons
   - Consider using smaller sentence transformer models

4. **API Key Errors:**
   - Verify Anthropic API key in `.env`
   - Check API key permissions and usage limits

### 9. Model Updates

#### Updating spaCy:
```bash
python -m spacy download en_core_web_sm --upgrade
```

#### Updating Sentence Transformers:
```bash
pip install --upgrade sentence-transformers
```

#### Updating O*NET:
- Download latest version from O*NET website
- Update paths in `.env` if filename changes

### 10. Custom Models

You can extend the ML system by:

1. **Adding Custom Models:**
   - Create new modules in `backend/ml/`
   - Import and register in `IntelligenceCore`

2. **Custom Skill Taxonomies:**
   - Replace or supplement O*NET data
   - Update `dataset_loader.py` accordingly

3. **Alternative Embeddings:**
   - Swap sentence transformers for other models
   - Update `similarity.py` for new embedding methods

## Integration with Backend

The ML components integrate with FastAPI through:

- **Model Loader:** `backend/ml/model_loader.py`
- **Route Handlers:** Various routes in `backend/routes/`
- **Startup Process:** Loaded in `main.py` lifespan

All ML operations are centralized through the `IntelligenceCore` class for consistency and performance.
