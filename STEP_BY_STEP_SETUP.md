# Step-by-Step Setup Guide for Bridgr

Follow these exact steps to set up all required accounts and services for your Bridgr career development platform.

---

## 🔑 Step 1: Anthropic Account Setup (Claude AI)

### 1.1 Create Account
1. Go to https://console.anthropic.com/
2. Click **"Sign up"** in the top right
3. Choose your signup method:
   - Google account (recommended)
   - Email with password
   - GitHub account

### 1.2 Verify Email
1. Check your email for verification link
2. Click the verification link
3. Return to the Anthropic console

### 1.3 Get API Key
1. Once logged in, you'll see the dashboard
2. Click **"API Keys"** in the left sidebar
3. Click **"Create Key"** button
4. Give your key a name (e.g., "Bridgr Development")
5. Copy the API key immediately (starts with `sk-ant-`)
6. **Important:** Save this key somewhere safe - you won't see it again

### 1.4 Check Usage Limits
1. In the dashboard, check your free tier limits
2. Note the monthly token limit for development
3. You can upgrade later if needed

---

## 🗄️ Step 2: Supabase Account Setup (Database & Auth)

### 2.1 Create Account
1. Go to https://supabase.com/
2. Click **"Start your project"** or **"Sign Up"**
3. Choose signup method:
   - GitHub account (recommended)
   - Google account
   - Email with password

### 2.2 Verify Email
1. Check your email for verification
2. Click the verification link
3. Complete your profile if prompted

### 2.3 Create New Project
1. After login, click **"New Project"** button
2. Choose your organization (or create one)
3. Fill in project details:
   - **Project Name:** `bridgr-dev` (or your preferred name)
   - **Database Password:** Create a strong password (save it!)
   - **Region:** Choose closest to your location
4. Click **"Create new project"**

### 2.4 Get Project Credentials
1. Wait for project to be created (2-3 minutes)
2. Go to **Project Settings** (gear icon ⚙️)
3. Click **"API"** in the sidebar
4. Copy these two values:
   - **Project URL:** (https://xxx.supabase.co)
   - **anon public** API Key (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

### 2.5 Set Up Database Tables (Optional for now)
1. Go to **"Table Editor"** in the sidebar
2. You can create tables later when needed
3. For now, the default setup is sufficient

---

## 📊 Step 3: O*NET Dataset Download

### 3.1 Access O*NET Database
1. Go to https://www.onetcenter.org/database.html
2. Scroll down to **"Database Downloads"** section
3. Look for the latest version (currently "Database 30.2")

### 3.2 Download the Dataset
1. Find **"Database 30.2 - Text"** (or latest version)
2. Click the download link for the ZIP file
3. The file will be named something like `db_30_2_text.zip`
4. Save it to your Downloads folder (it's about 50-100MB)

### 3.3 Extract the Dataset
1. Create the data directory structure:
   ```bash
   # In your project root (c:\Users\Dell\bridgr)
   mkdir data
   mkdir data\raw
   ```

2. Extract the ZIP file:
   - Right-click `db_30_2_text.zip`
   - Select **"Extract All..."**
   - Extract to `c:\Users\Dell\bridgr\data\raw\`
   - You should see files like `Occupations.txt`, `Skills.txt`, etc.

3. Verify the structure:
   ```
   data/
   └── raw/
       ├── Occupations.txt
       ├── Skills.txt
       ├── Knowledge.txt
       └── [other O*NET files]
   ```

---

## 🔧 Step 4: Environment Configuration

### 4.1 Create Environment File
1. In your project root (`c:\Users\Dell\bridgr`)
2. Copy the example file:
   ```bash
   copy .env.example .env
   ```

### 4.2 Fill in Environment Variables
Open `.env` file and replace the placeholder values:

```env
# Anthropic (Claude AI) - From Step 1
ANTHROPIC_API_KEY=sk-ant-your_actual_key_here

# Supabase - From Step 2
SUPABASE_URL=https://your_project_id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your_actual_key_here

# Development settings
DEBUG=true
APP_NAME=Bridgr

# O*NET dataset paths - From Step 3
ONET_ZIP_PATH=data/raw/db_30_2_text.zip
ONET_EXTRACT_PATH=data/

# ML tuning thresholds (keep defaults)
SEMANTIC_THRESHOLD=0.75
HIGH_DEMAND_THRESHOLD=0.15
```

### 4.3 Frontend Environment
1. Go to `frontend` directory
2. Copy the example:
   ```bash
   copy .env.example .env
   ```

3. Edit `frontend\.env`:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_ENV=development
   ```

---

## 📦 Step 5: Install Dependencies

### 5.1 Backend Dependencies
1. Open Command Prompt/PowerShell
2. Navigate to backend:
   ```bash
   cd c:\Users\Dell\bridgr\backend
   ```

3. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### 5.2 Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 5.3 Frontend Dependencies
1. Navigate to frontend:
   ```bash
   cd c:\Users\Dell\bridgr\frontend
   ```

2. Install Node.js packages:
   ```bash
   npm install
   ```

---

## 🚀 Step 6: Test Everything

### 6.1 Start Backend Server
1. Open a new terminal
2. Navigate to backend:
   ```bash
   cd c:\Users\Dell\bridgr\backend
   ```

3. Start the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Test it's working:
   - Open browser to http://localhost:8000
   - You should see: `{"message": "Bridgr API", "status": "running"}`

### 6.2 Start Frontend Server
1. Open another terminal
2. Navigate to frontend:
   ```bash
   cd c:\Users\Dell\bridgr\frontend
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Test it's working:
   - Browser should open to http://localhost:3000
   - You should see the Bridgr landing page

### 6.3 Test API Connection
1. In the frontend browser, open developer tools (F12)
2. In console, test the API:
   ```javascript
   fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
   ```
3. You should see: `{status: "ok"}`

---

## ✅ Step 7: Verify ML Components

### 7.1 Test ML Loading
1. In the backend terminal (where server is running)
2. You should see messages like:
   ```
   🌉 Starting Bridgr server...
   [ML models loading messages]
   🌉 Bridgr is ready!
   ```

### 7.2 Test Individual Components
Run these commands to verify everything works:

```bash
# Test spaCy
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy working!')"

# Test sentence transformers
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); print('✅ Transformers working!')"

# Test intelligence core
python -c "from backend.ml.model_loader import get_core; core = get_core(); print('✅ ML Core loaded!')"
```

---

## 🎯 Quick Start Checklist

Copy this checklist and mark each item as completed:

```
□ Anthropic account created
□ Anthropic API key obtained and saved
□ Supabase account created
□ Supabase project created
□ Supabase URL and API key obtained
□ O*NET dataset downloaded
□ O*NET dataset extracted to data/raw/
□ .env file created and filled
□ frontend/.env file created
□ Backend dependencies installed
□ spaCy model downloaded
□ Frontend dependencies installed
□ Backend server starts successfully
□ Frontend server starts successfully
□ API connection working
□ ML components loaded successfully
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions:

**API Key Errors:**
- Verify keys are copied correctly (no extra spaces)
- Check .env file is in the correct location
- Ensure keys don't have quote marks around them

**CORS Errors:**
- Make sure both servers are running
- Check that frontend URL matches backend CORS settings

**ML Model Errors:**
- Ensure spaCy model is downloaded: `python -m spacy download en_core_web_sm`
- Verify O*NET dataset is in the correct location
- Check that all Python packages installed successfully

**Port Conflicts:**
- If port 8000 is busy: change backend port with `--port 8001`
- If port 3000 is busy: frontend will automatically try 3001

---

## 🎉 You're Ready!

Once all steps above are completed, your Bridgr platform is fully operational:

- **Backend API:** http://localhost:8000
- **Frontend App:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **ML Features:** Resume analysis, skill gaps, career roadmaps
- **AI Chat:** Claude-powered career guidance

You can now start developing and testing your career development platform!
