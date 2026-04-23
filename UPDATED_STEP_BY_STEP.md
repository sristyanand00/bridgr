# Updated Step-by-Step Setup Guide (Free AI Version)

Follow these steps to set up Bridgr with **FREE** AI services.

---

## 🔑 Step 1: OpenAI Account Setup (FREE - $5 Credit)

### 1.1 Create Account
1. Go to https://platform.openai.com/
2. Click **"Sign up"** in the top right
3. Choose signup method:
   - Google account (recommended)
   - Email with password
   - Microsoft account

### 1.2 Verify Email & Phone
1. Check your email for verification link
2. You may need to verify your phone number
3. Return to the OpenAI dashboard

### 1.3 Get FREE API Key
1. Once logged in, you'll see the dashboard
2. Click **"API Keys"** in the left sidebar
3. Click **"Create new secret key"** button
4. Give your key a name (e.g., "Bridgr Development")
5. Copy the API key immediately (starts with `sk-`)
6. **Important:** Save this key somewhere safe - you won't see it again

### 1.4 Check FREE Credits
1. In the dashboard, you should see **$5.00 USD** in free credits
2. This is enough for extensive testing and development
3. After using the $5, you still get ongoing free usage

---

## 🗄️ Step 2: Supabase Account Setup (FREE)

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

### 2.3 Create FREE Project
1. After login, click **"New Project"** button
2. Choose your organization (or create one)
3. Fill in project details:
   - **Project Name:** `bridgr-dev`
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

---

## 📊 Step 3: O*NET Dataset Download (FREE)

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
# OpenAI (GPT) - From Step 1 (FREE)
OPENAI_API_KEY=sk-your_actual_openai_key_here

# Supabase - From Step 2 (FREE)
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

3. Install Python packages (updated with OpenAI):
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

---

## ✅ Step 7: Verify AI Integration

### 7.1 Test OpenAI Connection
1. In the backend terminal, you should see:
   ```
   🌉 Starting Bridgr server...
   🌉 Bridgr is ready!
   ```

2. Test the AI with a simple request:
   ```bash
   curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d "{\"message\": \"Hello, can you give me career advice?\"}"
   ```

### 7.2 Test Components
Run these commands to verify everything works:

```bash
# Test spaCy
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy working!')"

# Test sentence transformers
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); print('✅ Transformers working!')"

# Test OpenAI
python -c "import openai; print('✅ OpenAI working!')"
```

---

## 💰 Cost Summary

### **Total Cost: $0** (FREE!)

| Service | Cost | Free Tier |
|---------|------|-----------|
| OpenAI GPT | $5 credit + ongoing free | ✅ FREE |
| Supabase | $0 for development | ✅ FREE |
| O*NET Dataset | $0 | ✅ FREE |
| All other tools | $0 | ✅ FREE |

---

## 🎯 Quick Start Checklist

```
□ OpenAI account created (FREE - $5 credit)
□ OpenAI API key obtained and saved
□ Supabase account created (FREE)
□ Supabase project created (FREE)
□ Supabase URL and API key obtained
□ O*NET dataset downloaded (FREE)
□ O*NET dataset extracted to data/raw/
□ .env file created and filled with OpenAI key
□ frontend/.env file created
□ Backend dependencies installed (with OpenAI)
□ spaCy model downloaded
□ Frontend dependencies installed
□ Backend server starts successfully
□ Frontend server starts successfully
□ OpenAI AI integration working
□ All ML components loaded successfully
```

---

## 🔧 Troubleshooting

### OpenAI Issues:
- **API Key Errors:** Verify key starts with `sk-` and has no quotes
- **Credit Issues:** Check you have $5 free credit in dashboard
- **Rate Limits:** Free tier has generous limits for development

### Common Issues:
- **CORS Errors:** Ensure both servers are running
- **Import Errors:** Make sure all packages installed with updated requirements.txt
- **Port Conflicts:** Change ports if needed (8001 for backend, 3001 for frontend)

---

## 🎉 You're Ready!

Your **FREE** Bridgr platform is now fully operational:

- **Backend API:** http://localhost:8000
- **Frontend App:** http://localhost:3000
- **AI Features:** Powered by OpenAI GPT (FREE)
- **Database:** Supabase (FREE)
- **ML Features:** Resume analysis, skill gaps, career roadmaps

**All features work exactly the same, but now completely free!**

---

## 🔄 Alternative Free Options

If you want alternatives to OpenAI:

1. **Google Gemini:** $300 free credit at https://ai.google.dev/
2. **Groq:** High rate limits at https://groq.com/
3. **Local Models:** 100% free with Ollama (no API key needed)

I can help you switch to any of these alternatives if needed!
