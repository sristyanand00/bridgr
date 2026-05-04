import React, { useState, useEffect, createContext, useContext } from 'react';
import './styles/index.css';

import { Sidebar, Topbar, Cursor } from './components/layout';
import { Quiz, AuthModal, RoleGuidance } from './components/forms';
import FeaturesSection from './components/layout/FeaturesSection';
import {
  Dashboard,
  Resume,
  Chat,
  Roadmap,
  Market,
  Interview,
  Pricing,
  Settings,
  History,
} from './pages';
import { auth, signOut } from './config/firebase';

// ─────────────────────────────────────────────────────────────────────────────
// Global Analysis Context
// ─────────────────────────────────────────────────────────────────────────────
export const AnalysisContext = createContext({
  analysisData:    null,
  setAnalysisData: () => {},
  roadmapDays:     90,
  setRoadmapDays:  () => {},
  autoGenerate:    false,
  setAutoGenerate: () => {},
});

export const useAnalysis = () => useContext(AnalysisContext);

// ─────────────────────────────────────────────────────────────────────────────

// Pages that show a back button pointing to dashboard
const PAGES_WITH_BACK = ['resume', 'chat', 'roadmap', 'market', 'interview', 'pricing', 'settings'];

const App = () => {
  const [screen, setScreen]               = useState("loading"); // start in loading state
  const [currentPage, setCurrentPage]     = useState("dashboard");
  const [pageHistory, setPageHistory]     = useState(["dashboard"]);
  const [profile, setProfile]             = useState(null);
  const [user, setUser]                   = useState(null);
  const [analysisData, setAnalysisData]   = useState(null);
  const [roadmapDays,  setRoadmapDays]    = useState(90);
  const [autoGenerate, setAutoGenerate]   = useState(false);
  const [showAuth, setShowAuth]           = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // ── Sync with PostgreSQL backend ────────────────────────────────────────
  const syncUserWithBackend = async (firebaseUser) => {
    try {
      const token = await firebaseUser.getIdToken();
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/sync`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const dbUser = await response.json();
        if (dbUser.quiz_data) {
          setProfile(prev => ({ ...prev, ...dbUser.quiz_data }));
        }
      }
    } catch (err) {
      console.error("Failed to sync user with backend:", err);
    }
  };

  // ── Firebase persistent auth check ──────────────────────────────────────
  useEffect(() => {
    let unsubscribe = () => {};

    if (auth && typeof auth.onAuthStateChanged === 'function') {
      unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
        if (firebaseUser) {
          // User was previously logged in — restore session
          const userData = {
            uid:           firebaseUser.uid,
            name:          firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
            email:         firebaseUser.email,
            avatar:        (firebaseUser.displayName || firebaseUser.email || 'U').charAt(0).toUpperCase(),
            authenticated: true,
          };
          setUser(userData);
          setProfile(prev => ({ ...(prev || {}), ...userData }));
          
          setScreen("app");
          
          // Sync with DB in background
          syncUserWithBackend(firebaseUser);
        } else {
          // No active session — show landing
          if (screen === "loading") setScreen("landing");
        }
      });
    } else {
      // Mock auth — go straight to landing
      setScreen("landing");
    }

    return () => unsubscribe();
  }, []); // intentionally empty — only run on mount for auth state check


  // ── Navigation helpers ───────────────────────────────────────────────────
  const navigateTo = (page) => {
    setPageHistory(prev => [...prev, page]);
    setCurrentPage(page);
  };

  const navigateBack = () => {
    setPageHistory(prev => {
      if (prev.length <= 1) return prev;
      const newHistory = prev.slice(0, -1);
      setCurrentPage(newHistory[newHistory.length - 1]);
      return newHistory;
    });
  };

  const canGoBack = pageHistory.length > 1;

  // ── Auth handlers ────────────────────────────────────────────────────────
  const handleQuizComplete = (answers) => {
    // Navigate immediately to the app
    setScreen("app");
    setProfile(prev => ({ ...(prev || {}), ...answers }));
    
    // Save quiz to DB in the background if authenticated
    if (user?.authenticated || auth.currentUser) {
      const syncQuiz = async () => {
        try {
          const token = await auth.currentUser.getIdToken();
          await fetch(`${process.env.REACT_APP_API_URL}/api/user/quiz`, {
            method: 'POST',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify({ quiz_data: answers })
          });
        } catch (err) {
          console.error("Background sync failed:", err);
        }
      };
      syncQuiz();
    }
  };

  const handleSkipQuiz = () => {
    setProfile(prev => ({ ...(prev || {}), stage: "Not specified", timeline: "Exploring, no rush", city: "Bengaluru" }));
    setScreen("app");
  };

  const handleAuth = (userData) => {
    const enriched = { ...userData, authenticated: true };
    setUser(enriched);
    setProfile(prev => ({ ...(prev || {}), ...enriched }));
    setShowAuth(false);
    // First-time login → show quiz; returning (onAuthStateChanged fired) → already in app
    if (screen !== "app") {
      setScreen("quiz");
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
    } catch (err) {
      console.error("Sign-out error:", err);
    }
    setUser({ name: "Guest", avatar: "G", authenticated: false });
    setProfile(null);
    setScreen("landing");
    setCurrentPage("dashboard");
    setPageHistory(["dashboard"]);
  };

  const handleSignInFromSidebar = () => {
    setShowAuth(true);
  };

  const mergedProfile = { ...profile, ...user };

  // ── Pages ────────────────────────────────────────────────────────────────
  const pages = {
    dashboard: (
      <Dashboard
        setCurrentPage={navigateTo}
        profile={mergedProfile}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />
    ),
    resume: (
      <Resume
        profile={mergedProfile}
        onSaveGate={() => setShowAuth(true)}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        setCurrentPage={navigateTo}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
    chat: (
      <Chat
        profile={mergedProfile}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
    roadmap: (
      <Roadmap
        profile={mergedProfile}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
    market: (
      <Market
        profile={mergedProfile}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
    interview: (
      <Interview
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
    pricing: (
      <Pricing
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
    settings: (
      <Settings
        profile={mergedProfile}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
        onSignOut={handleSignOut}
      />
    ),
    history: (
      <History
        profile={mergedProfile}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
        setCurrentPage={navigateTo}
        onBack={canGoBack ? navigateBack : () => navigateTo("dashboard")}
      />
    ),
  };

  // ── Landing ──────────────────────────────────────────────────────────────
  const LandingPage = () => (
    <>
      <div style={{
        minHeight: "100vh", display: "flex", alignItems: "center",
        justifyContent: "center", flexDirection: "column", textAlign: "center",
        padding: "80px 24px", position: "relative", zIndex: 1,
      }}>
        {/* NAV */}
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0,
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "18px 48px",
          background: "rgba(0,0,5,.6)", backdropFilter: "blur(30px)",
          borderBottom: "1px solid var(--gb)", zIndex: 10,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <img src="/bridgr-logo.png" alt="bridgr logo" style={{ width: 32, height: 32, objectFit: "contain" }} />
            <span style={{ fontFamily: "'Fraunces',serif", fontWeight: 300, fontSize: 18, letterSpacing: "-.02em", color: "white" }}>
              bridgr
            </span>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn bgl bsm" onClick={() => setScreen("auth")}>Features</button>
            <button className="btn bgl bsm" onClick={() => setScreen("auth")}>Pricing</button>
            <button className="btn bgl bsm" onClick={() => setScreen("auth")}>Sign in</button>
            <button className="btn bg bsm" onClick={() => setScreen("auth")}>Start Free →</button>
          </div>
        </div>

        <h1 className="afu d1" style={{
          fontFamily: "'Fraunces',serif", fontWeight: 300,
          fontSize: "clamp(52px,7vw,88px)", lineHeight: 1.05,
          letterSpacing: "-.04em", maxWidth: 800, margin: "0 auto 28px", color: "var(--t1)",
        }}>
          Bridgr
        </h1>

        <p className="afu d2" style={{
          fontSize: 24, color: "var(--t2)", maxWidth: 800, margin: "0 auto 40px",
          lineHeight: 1.4, fontFamily: "'Fraunces',serif", fontWeight: 300,
        }}>
          Bridge between who you are and who you want to become
        </p>

        <div className="afu d3" style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
          <button className="btn bg" style={{ fontSize: 15, padding: "14px 32px" }} onClick={() => setScreen("auth")}>
            <span>Analyze My Resume — Free</span>
            <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </div>

      <FeaturesSection />
    </>
  );

  // ── Loading screen ───────────────────────────────────────────────────────
  const LoadingScreen = () => (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      flexDirection: "column", gap: 16,
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10,
        background: "linear-gradient(135deg,var(--p2),var(--i))",
        display: "flex", alignItems: "center", justifyContent: "center",
        boxShadow: "0 0 24px rgba(139,92,246,.45)",
        animation: "pulse 1.5s ease-in-out infinite",
      }}>
        <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9.5 2A2.5 2.5 0 017 4.5v1A2.5 2.5 0 014.5 8H4a2 2 0 00-2 2v4a2 2 0 002 2h.5A2.5 2.5 0 017 18.5v1a2.5 2.5 0 002.5 2.5h5a2.5 2.5 0 002.5-2.5v-1a2.5 2.5 0 012.5-2.5h.5a2 2 0 002-2v-4a2 2 0 00-2-2h-.5A2.5 2.5 0 0117 5.5v-1A2.5 2.5 0 0114.5 2h-5z"/>
        </svg>
      </div>
      <span style={{ fontFamily: "'Fraunces',serif", fontWeight: 300, fontSize: 18, color: "var(--t2)", letterSpacing: "-.02em" }}>
        bridgr
      </span>
      <div style={{ fontSize: 12, color: "var(--t3)", marginTop: -8 }}>Checking authentication…</div>
    </div>
  );

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <AnalysisContext.Provider value={{
      analysisData,  setAnalysisData,
      roadmapDays,   setRoadmapDays,
      autoGenerate,  setAutoGenerate,
    }}>
      <Cursor />
      <div className="o1 orb" />
      <div className="o2 orb" />
      <div className="o3 orb" />

      {screen === "loading" && <LoadingScreen />}

      {screen === "landing" && <LandingPage />}

      {screen === "quiz" && (
        <Quiz onComplete={handleQuizComplete} onSkip={handleSkipQuiz} />
      )}

      {screen === "auth" && (
        <AuthModal
          mode={profile ? "save" : "required"}
          onAuth={handleAuth}
          onSkip={() => {
            setUser({ name: "Guest", avatar: "G", authenticated: false });
            setScreen("app");
          }}
          onBack={() => setScreen("landing")}
        />
      )}

      {screen === "app" && (
        <div className="shell">
          {showAuth && (
            <AuthModal
              mode="save"
              onAuth={handleAuth}
              onSkip={() => setShowAuth(false)}
            />
          )}
          <div
            className={`mobile-menu-overlay ${mobileMenuOpen ? 'show' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          />
          <Sidebar
            currentPage={currentPage}
            setCurrentPage={navigateTo}
            user={user}
            mobileMenuOpen={mobileMenuOpen}
            setMobileMenuOpen={setMobileMenuOpen}
            onSignOut={handleSignOut}
            onSignIn={handleSignInFromSidebar}
          />
          {pages[currentPage] || pages.dashboard}
        </div>
      )}
    </AnalysisContext.Provider>
  );
};

export default App;