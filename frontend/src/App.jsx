import React, { useState } from 'react';
import './styles/index.css';

// Import components
import { Sidebar, Topbar, Cursor } from './components/layout';
import { Quiz, AuthModal, RoleGuidance } from './components/forms';
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

  const handleQuizComplete = (answers) => {
    setProfile(answers);
    // Show Google auth before running analysis — but non-blocking
    setScreen("auth");
  };

  const handleAuth = (userData) => {
    setUser({ ...userData, authenticated: true });
    setProfile(prev => ({ ...prev, ...userData, authenticated: true }));
    setShowAuth(false);
    setScreen("app");
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
    />,
    resume: <Resume 
      profile={{...profile, ...user}} 
      onSaveGate={() => setShowAuth(true)} 
      analysisData={analysisData} 
      setAnalysisData={setAnalysisData}
    />,
    chat: <Chat 
      profile={{...profile, ...user}} 
      analysisData={analysisData}
    />,
    roadmap: <Roadmap 
      profile={{...profile, ...user}}
    />,
    market: <Market 
      profile={{...profile, ...user}} 
      analysisData={analysisData}
    />,
    interview: <Interview />,
    pricing: <Pricing />,
    settings: <Settings 
      profile={{...profile, ...user}}
    />,
  };

  const LandingPage = () => (
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
            <div style={{ 
              width:24, 
              height:24, 
              borderRadius:"50%", 
              background:"linear-gradient(135deg,var(--p2),var(--i))", 
              display:"flex", 
              alignItems:"center", 
              justifyContent:"center",
              position:"relative"
            }}>
              <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <div style={{ 
              width:20, 
              height:2, 
              background:"repeating-linear-gradient(90deg, var(--p3) 0, var(--p3) 2px, transparent 2px, transparent 4px)",
              borderRadius:1 
            }}/>
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
          <button className="btn bgl bsm" style={{ border:"none", color:"var(--t3)" }}>
            Features
          </button>
          <button className="btn bgl bsm" style={{ border:"none", color:"var(--t3)" }}>
            Pricing
          </button>
          <button className="btn bgl bsm" onClick={() => setScreen("auth")}>
            Sign in
          </button>
          <button className="btn bg bsm" onClick={() => setScreen("quiz")}>
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
          onClick={() => setScreen("quiz")}
        >
          <span>Analyze My Resume — Free</span>
          <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </button>
        <button className="btn bgl" style={{ fontSize:15, padding:"14px 24px" }}>
          Watch demo ↗
        </button>
      </div>
      
      <div className="afu d4" style={{ fontSize:12.5, color:"var(--t3)", marginTop:18 }}>
        No credit card · 60 seconds · Free forever plan
      </div>
    </div>
  );

  return (
    <>
      <Cursor/>
      <div className="o1 orb"/>
      <div className="o2 orb"/>
      <div className="o3 orb"/>

      {screen === "landing" && <LandingPage />}

      {screen === "quiz" && (
        <Quiz onComplete={handleQuizComplete}/>
      )}

      {screen === "auth" && (
        <AuthModal
          mode="required"
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
          <Sidebar 
            currentPage={currentPage} 
            setCurrentPage={setCurrentPage} 
            user={user}
          />
          {pages[currentPage]}
        </div>
      )}
    </>
  );
};

export default App;
