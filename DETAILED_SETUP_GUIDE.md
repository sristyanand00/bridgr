# Detailed Step-by-Step Setup Guide

## 🔑 Step 1: OpenAI Account Setup (5 minutes)

### 1.1 Create Account
1. **Open your browser** and go to: https://platform.openai.com/
2. **Click "Sign up"** in the top right corner
3. **Choose your signup method:**
   - ✅ **Google** (recommended - fastest)
   - ✅ **Email** (use your email + password)
   - ✅ **Microsoft** (if you have Microsoft account)
   - ✅ **GitHub** (if you have GitHub account)

### 1.2 Verify Your Account
1. **Check your email** for verification link
2. **Click the verification link** in the email
3. **You may need to verify your phone number** (required for API access)
   - Enter your mobile number
   - You'll receive a 6-digit code via SMS
   - Enter the code to verify

### 1.3 Get Your API Key
1. **After login**, you'll see the OpenAI dashboard
2. **Look at the left sidebar** → Click **"API Keys"**
3. **Click the blue "Create new secret key" button**
4. **Give your key a name:** Type "Bridgr Development" 
5. **Click "Create secret key"**
6. **⚠️ IMPORTANT:** Copy the API key immediately!
   - Key format: `sk-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`
   - **You cannot see it again after closing this window**
   - Save it in Notepad or somewhere safe

### 1.4 Check Your Free Credits
1. **In the dashboard**, look for "Usage" or "Billing"
2. **You should see $5.00 in free credit**
3. **This is enough for extensive testing** of your Bridgr project

---

## 🗄️ Step 2: Supabase Account Setup (5 minutes)

### 2.1 Create Account
1. **Open your browser** and go to: https://supabase.com/
2. **Click "Start your project"** or "Sign Up"
3. **Choose your signup method:**
   - ✅ **GitHub** (recommended if you have GitHub)
   - ✅ **Google** (fastest option)
   - ✅ **Email** (use email + password)

### 2.2 Verify Email
1. **Check your email** for verification from Supabase
2. **Click the verification link**
3. **Complete your profile** if prompted (name, etc.)

### 2.3 Create Your First Project
1. **After login**, click **"New Project"** button
2. **Choose or create an organization:**
   - If asked, click "Create organization"
   - Name: "Personal" or your name
3. **Fill in project details:**
   - **Project Name:** `bridgr-dev`
   - **Database Password:** Create a strong password (e.g., `Bridgr2024!@#`)
   - **Region:** Choose the closest region to you
   - **Pricing Plan:** Leave as "Free" (default)
4. **Click "Create new project"**

### 2.4 Wait for Project Setup
1. **Wait 2-3 minutes** while Supabase sets up your project
2. **You'll see a progress bar**
3. **When done, you'll see your project dashboard**

### 2.5 Get Your Project Credentials
1. **Click the gear icon ⚙️** (Project Settings) in left sidebar
2. **Click "API"** in the settings menu
3. **Find these two values:**

#### **Project URL:**
- Look for: **Project URL**
- Copy the URL (format: `https://abcdefg.supabase.co`)
- Example: `https://xyzabc123.supabase.co`

#### **API Key:**
- Scroll down to **"Project API keys"**
- Find **"anon public"** key
- Copy the key (format: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
- **This is a long string - copy the entire thing**

### 2.6 Save Your Credentials
Save both values in Notepad:
```
Supabase URL: https://your-project-id.supabase.co
Supabase Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...very-long-string...
```

---

## 🔧 Step 3: Configure Your Project (3 minutes)

### 3.1 Create Environment File
1. **Open Command Prompt** or PowerShell
2. **Navigate to your project folder:**
   ```bash
   cd c:\Users\Dell\bridgr
   ```
3. **Copy the environment file:**
   ```bash
   copy .env.example .env
   ```

### 3.2 Fill in Your API Keys
1. **Open the .env file** with Notepad:
   ```bash
   notepad .env
   ```
2. **Replace the placeholder values:**

   **Find this line:**
   ```
   OPENAI_API_KEY=sk-your_openai_api_key_here
   ```
   **Replace with:**
   ```
   OPENAI_API_KEY=sk-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
   ```

   **Find this line:**
   ```
   SUPABASE_URL=your_supabase_project_url_here
   ```
   **Replace with:**
   ```
   SUPABASE_URL=https://xyzabc123.supabase.co
   ```

   **Find this line:**
   ```
   SUPABASE_KEY=your_supabase_anon_key_here
   ```
   **Replace with:**
   ```
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...very-long-string...
   ```

3. **Save the file** (Ctrl + S) and **close Notepad**

### 3.3 Setup Frontend Environment
1. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```
2. **Copy frontend environment file:**
   ```bash
   copy .env.example .env
   ```
3. **The frontend .env file is already correct** - no changes needed

---

## 🚀 Step 4: Install Dependencies (2 minutes)

### 4.1 Install All Dependencies
1. **Go back to project root:**
   ```bash
   cd ..
   ```
2. **Install everything with one command:**
   ```bash
   npm run install:all
   ```
3. **This will install:**
   - Python packages for backend
   - Node.js packages for frontend
   - spaCy language model

### 4.2 If Installation Fails
**If npm command doesn't work, install manually:**

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Frontend dependencies
cd ../frontend
npm install
```

---

## 🎯 Step 5: Test Your Setup (2 minutes)

### 5.1 Start Backend Server
1. **Open new terminal** (Ctrl + Shift + T in PowerShell)
2. **Navigate to backend:**
   ```bash
   cd c:\Users\Dell\bridgr\backend
   ```
3. **Start the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **You should see:**
   ```
   🌉 Starting Bridgr server...
   🚀 Initializing Bridgr Intelligence Core...
   🔧 Loading NLP models...
   ⚡ Precomputing embeddings...
   ✅ Bridgr Intelligence Core ready
   🌉 Bridgr is ready!
   ```

### 5.2 Test Backend
1. **Open your browser** and go to: http://localhost:8000
2. **You should see:** `{"message": "Bridgr API", "status": "running"}`

### 5.3 Start Frontend Server
1. **Open another new terminal**
2. **Navigate to frontend:**
   ```bash
   cd c:\Users\Dell\bridgr\frontend
   ```
3. **Start the frontend:**
   ```bash
   npm start
   ```
4. **Browser should open to:** http://localhost:3000
5. **You should see the Bridgr landing page**

---

## ✅ Success! Your AI Career Tutor is Running!

### What You Have Now:
- ✅ **Backend API:** http://localhost:8000
- ✅ **Frontend App:** http://localhost:3000
- ✅ **AI Chat Tutor:** Powered by OpenAI GPT
- ✅ **Resume Analysis:** ML + AI powered
- ✅ **Database:** Supabase storage

### Test the AI Tutor:
1. **Go to http://localhost:3000**
2. **Click "Start Free"**
3. **Complete the quick quiz**
4. **Try the chat feature** - ask career questions!
5. **Upload a resume** (if you have one) to test analysis

---

## 🔧 Troubleshooting

### Common Issues:

**"API Key Error"**
- Check your .env file has correct keys
- Make sure no extra quotes around keys
- Verify keys are copied correctly

**"Port Already in Use"**
- Change backend port: `--port 8001`
- Frontend will auto-change to 3001

**"Module Not Found"**
- Run: `pip install -r requirements.txt`
- Run: `python -m spacy download en_core_web_sm`

**"CORS Error"**
- Make sure both servers are running
- Check frontend URL matches backend settings

---

## 🎉 You're Done!

Your **Bridgr AI Career Tutor** is now fully operational with:
- **FREE OpenAI API** ($5 credit + ongoing free)
- **FREE Supabase database**
- **All ML features working**
- **AI chat tutor ready**

**Total setup time: ~15-20 minutes**

Now you can start building and testing your career development platform!
