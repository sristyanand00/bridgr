import React, { useState } from 'react';
import './styles/index.css';

// Import components
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
  Settings 
} from './pages';

const App = () => {
  // screen: landing → quiz → auth → app
  const [screen, setScreen] = useState("landing");
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [user, setUser] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleQuizComplete = (answers) => {
    setProfile(answers);
    // Go directly to app after quiz, auth can happen later
    setScreen("app");
  };

  const handleSkipQuiz = () => {
    // Skip quiz and go directly to app with minimal profile
    setProfile({
      stage: "Not specified",
      timeline: "Exploring, no rush",
      city: "Bengaluru"
    });
    setScreen("app");
  };

  const handleAuth = (userData) => {
    setUser({ ...userData, authenticated: true });
    setProfile(prev => ({ ...prev, ...userData, authenticated: true }));
    setShowAuth(false);
    // Always show questionnaire after authentication
    setScreen("quiz");
  };

  const handleSkipAuth = () => {
    setShowAuth(false);
    setScreen("app");
  };

  const pages = {
    dashboard: <Dashboard 
      setCurrentPage={setCurrentPage} 
      profile={{...profile, ...user}} 
      analysisData={analysisData}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
    resume: <Resume 
      profile={{...profile, ...user}} 
      onSaveGate={() => setShowAuth(true)} 
      analysisData={analysisData} 
      setAnalysisData={setAnalysisData}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
      setCurrentPage={setCurrentPage}
    />,
    chat: <Chat 
      profile={{...profile, ...user}} 
      analysisData={analysisData}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
    roadmap: <Roadmap 
      profile={{...profile, ...user}}
      analysisData={analysisData}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
    market: <Market 
      profile={{...profile, ...user}} 
      analysisData={analysisData}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
    interview: <Interview 
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
    pricing: <Pricing 
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
    settings: <Settings 
      profile={{...profile, ...user}}
      mobileMenuOpen={mobileMenuOpen}
      setMobileMenuOpen={setMobileMenuOpen}
    />,
  };

  const handleLandingNavigation = (page) => {
    if (page === "pricing") {
      // For now, just go to auth since pricing is in the app
      setScreen("auth");
    }
  };

  const LandingPage = () => (
    <>
      <div style={{ 
        minHeight:"100vh", 
        display:"flex", 
        alignItems:"center", 
        justifyContent:"center", 
        flexDirection:"column", 
        textAlign:"center", 
        padding:"80px 24px", 
        position:"relative", 
        zIndex:1 
      }}>
        {/* NAV */}
        <div style={{ 
          position:"fixed", 
          top:0, 
          left:0, 
          right:0, 
          display:"flex", 
          alignItems:"center", 
          justifyContent:"space-between", 
          padding:"18px 48px", 
          background:"rgba(0,0,5,.6)", 
          backdropFilter:"blur(30px)", 
          borderBottom:"1px solid var(--gb)", 
          zIndex:10 
        }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ display:"flex", alignItems:"center", gap:8 }}>
              <img 
                src="/bridgr-logo.png" 
                alt="bridgr logo" 
                style={{ 
                  width:32, 
                  height:32, 
                  objectFit:"contain"
                }}
              />
            </div>
            <span style={{ 
              fontFamily:"'Fraunces',serif", 
              fontWeight:300, 
              fontSize:18, 
              letterSpacing:"-.02em",
              color:"white"
            }}>
              bridgr
            </span>
          </div>
          <div style={{ display:"flex", gap:8 }}>
            <button className="btn bgl bsm" onClick={() => handleLandingNavigation("pricing")}>
              Features
            </button>
            <button className="btn bgl bsm" onClick={() => handleLandingNavigation("pricing")}>
              Pricing
            </button>
            <button className="btn bgl bsm" onClick={() => setScreen("auth")}>
              Sign in
            </button>
            <button className="btn bg bsm" onClick={() => setScreen("auth")}>
              Start Free →
            </button>
          </div>
        </div>

        <h1 className="afu d1" style={{ 
          fontFamily:"'Fraunces',serif", 
          fontWeight:300, 
          fontSize:"clamp(52px,7vw,88px)", 
          lineHeight:1.05, 
          letterSpacing:"-.04em", 
          maxWidth:800, 
          margin:"0 auto 28px", 
          color:"var(--t1)" 
        }}>
          Bridgr
        </h1>
        
        <p className="afu d2" style={{ 
          fontSize:24, 
          color:"var(--t2)", 
          maxWidth:800, 
          margin:"0 auto 40px", 
          lineHeight:1.4,
          fontFamily:"'Fraunces',serif",
          fontWeight:300
        }}>
          Bridge between who you are and who you want to become
        </p>
        
        <div className="afu d3" style={{ display:"flex", gap:12, flexWrap:"wrap", justifyContent:"center" }}>
          <button 
            className="btn bg" 
            style={{ fontSize:15, padding:"14px 32px" }} 
            onClick={() => setScreen("auth")}
          >
            <span>Analyze My Resume — Free</span>
            <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12 5 19 12 12 19"/>
            </svg>
          </button>
        </div>
      </div>
      
      <FeaturesSection />
    </>
  );

  return (
    <>
      <Cursor/>
      <div className="o1 orb"/>
      <div className="o2 orb"/>
      <div className="o3 orb"/>

      {screen === "landing" && <LandingPage />}

      {screen === "quiz" && (
        <Quiz onComplete={handleQuizComplete} onSkip={handleSkipQuiz}/>
      )}

      {screen === "auth" && (
        <AuthModal
          mode={profile ? "save" : "required"}
          onAuth={handleAuth}
          onSkip={() => { 
            setUser({ name:"Guest", avatar:"G", authenticated:false }); 
            setScreen("app"); 
          }}
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
          {/* Mobile menu overlay */}
          <div 
            className={`mobile-menu-overlay ${mobileMenuOpen ? 'show' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          />
          <Sidebar 
            currentPage={currentPage} 
            setCurrentPage={setCurrentPage} 
            user={user}
            mobileMenuOpen={mobileMenuOpen}
            setMobileMenuOpen={setMobileMenuOpen}
          />
          {pages[currentPage]}
        </div>
      )}
    </>
  );
};

export default App;
