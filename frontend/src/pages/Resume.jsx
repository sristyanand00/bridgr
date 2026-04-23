import React, { useState } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon, Input } from '../components/ui';

const Resume = ({ profile, onSaveGate, analysisData, setAnalysisData }) => {
  const [stage, setStage] = useState("upload");
  const [showRoleGuide, setShowRoleGuide] = useState(false);
  const [targetRole, setTargetRole] = useState("");
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState(0);
  const [showSaveGate, setShowSaveGate] = useState(false);

  const steps = [
    "Extracting text from PDF…",
    "Detecting resume sections…",
    "Running NER skill extraction…",
    "Matching to job descriptions…",
    "Generating gap analysis…"
  ];

  // Simulated analysis results
  const mockAnalysis = {
    score: 72,
    matched: ["Python", "Machine Learning", "Data Analysis", "Pandas", "NumPy"],
    gaps: [
      { n: "SQL", p: "Critical", d: 89, reason: "Appears in 89% of DS job postings in your city" },
      { n: "Feature Engineering", p: "High", d: 76, reason: "Key differentiator for senior roles" },
      { n: "Docker", p: "Medium", d: 45, reason: "Increasingly required for production ML" },
      { n: "System Design", p: "Medium", d: 38, reason: "Essential for tech interviews" }
    ],
    salary: { min: "₹8L", median: "₹14.5L", max: "₹22L" }
  };

  const handleFileUpload = () => {
    setStage("analyzing");
    
    // Simulate analysis progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setStage("results");
            setAnalysisData(mockAnalysis);
            if (!profile?.authenticated) {
              setShowSaveGate(true);
            }
          }, 500);
          return 100;
        }
        return prev + 20;
      });
      
      if (progress < 100) {
        setStep(prev => Math.min(prev + 1, steps.length - 1));
      }
    }, 800);
  };

  if (stage === "upload") {
    return (
      <div className="main">
        <Topbar title="Resume Analysis" />
        <div className="page" style={{ maxWidth:580, margin:"0 auto" }}>
          <div style={{ textAlign:"center", marginBottom:36 }}>
            <h1 className="serif" style={{ fontSize:36, marginBottom:10, color:"var(--t1)" }}>
              Upload your resume
            </h1>
            <p style={{ color:"var(--t2)", fontSize:15 }}>
              Get instant AI analysis, skill gap mapping, and salary insights
            </p>
          </div>

          <Card className="gl" style={{ padding:40, marginBottom:20, textAlign:"center" }}>
            <div style={{ 
              width:80, 
              height:80, 
              borderRadius:20, 
              background:"linear-gradient(135deg,var(--p2),var(--i))", 
              display:"flex", 
              alignItems:"center", 
              justifyContent:"center", 
              margin:"0 auto 20px",
              boxShadow:"0 0 30px rgba(139,92,246,.4)"
            }}>
              <Icon name="upload" s={32} c="white"/>
            </div>
            
            <h3 style={{ fontFamily:"'Fraunces',serif", fontSize:22, marginBottom:8, color:"var(--t1)" }}>
              Drop your resume here
            </h3>
            <p style={{ fontSize:13, color:"var(--t3)", marginBottom:24 }}>
              PDF, DOC, DOCX • Max 5MB • We'll extract skills automatically
            </p>
            
            <div style={{ display:"flex", gap:12, justifyContent:"center" }}>
              <Button onClick={handleFileUpload}>
                <Icon name="upload" s={14} c="white"/>
                Choose File
              </Button>
              <Button variant="secondary">
                Browse Templates
              </Button>
            </div>
          </Card>

          <div style={{ 
            background:"rgba(139,92,246,.07)", 
            border:"1px solid rgba(139,92,246,.18)", 
            borderRadius:"var(--rm)", 
            padding:16, 
            display:"flex", 
            alignItems:"center", 
            gap:12 
          }}>
            <Icon name="sparkle" s={18} c="var(--p3)"/>
            <div style={{ fontSize:13, color:"var(--t2)", lineHeight:1.5 }}>
              <strong style={{ color:"var(--t1)" }}>Pro tip:</strong> Upload your most recent resume. Our AI will compare it against 1,000+ real job descriptions in {profile?.city || "Bengaluru"}.
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (stage === "analyzing") {
    return (
      <div className="main">
        <Topbar title="Analyzing Resume" />
        <div className="page" style={{ maxWidth:480, margin:"0 auto" }}>
          <div style={{ textAlign:"center", marginBottom:40 }}>
            <div style={{ 
              width:100, 
              height:100, 
              borderRadius:25, 
              background:"linear-gradient(135deg,var(--p2),var(--i))", 
              display:"flex", 
              alignItems:"center", 
              justifyContent:"center", 
              margin:"0 auto 24px",
              boxShadow:"0 0 40px rgba(139,92,246,.5)",
              animation:"pulse 2s infinite"
            }}>
              <Icon name="brain" s={40} c="white"/>
            </div>
            
            <h2 className="serif" style={{ fontSize:28, marginBottom:12, color:"var(--t1)" }}>
              AI is analyzing your resume
            </h2>
            <p style={{ fontSize:14, color:"var(--t3)", marginBottom:32 }}>
              Comparing against real job descriptions in {profile?.city || "Bengaluru"}
            </p>

            <div style={{ marginBottom:24 }}>
              <div style={{ 
                fontSize:12, 
                color:"var(--t3)", 
                marginBottom:8, 
                textAlign:"center" 
              }}>
                {steps[step]}
              </div>
              <ProgressBar value={progress} />
            </div>

            <div style={{ fontSize:12, color:"var(--t4)" }}>
              This usually takes 15-20 seconds
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { matched, gaps, salary } = analysisData || mockAnalysis;

  return (
    <div className="main">
      <Topbar 
        title="Resume Analysis" 
        sub={`${targetRole || "Data Scientist"} • ${profile?.city || "Bengaluru"}`}
        right={<Button size="small">Export PDF</Button>}
      />
      
      <div className="page">
        {/* Score Overview */}
        <Card className="gl" style={{ padding:30, marginBottom:14, textAlign:"center" }}>
          <div style={{ fontSize:14, color:"var(--t3)", marginBottom:8 }}>
            Resume Match Score
          </div>
          <div className="serif" style={{ fontSize:64, color:"var(--t1)", marginBottom:12 }}>
            {analysisData?.score || 72}%
          </div>
          <div style={{ fontSize:13, color:"var(--t2)", maxWidth:400, margin:"0 auto" }}>
            Your resume matches <strong>{matched.length}</strong> key skills for {targetRole || "Data Scientist"} roles in {profile?.city || "Bengaluru"}
          </div>
        </Card>

        <div className="b2" style={{ marginBottom:14 }}>
          {/* Matched Skills */}
          <Card className="gl" style={{ padding:24 }}>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:14 }}>
              <div style={{ fontSize:14, fontWeight:600, color:"var(--t1)" }}>
                Matched Skills
              </div>
              <Chip name={`${matched.length} found`} level="ok"/>
            </div>
            <div style={{ display:"flex", flexWrap:"wrap", gap:7 }}>
              {matched.map(skill => <Chip key={skill} name={skill} level="ok"/>)}
            </div>
            
            {/* Transferable skills */}
            {profile?.currentRole && (
              <div style={{ 
                marginTop:16, 
                padding:"12px 14px", 
                background:"rgba(16,185,129,.05)", 
                borderRadius:"var(--rm)", 
                border:"1px solid rgba(16,185,129,.15)" 
              }}>
                <div style={{ fontSize:12, color:"var(--g)", fontWeight:600, marginBottom:6 }}>
                  Transferable from your {profile.currentRole} background
                </div>
                <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
                  {["Statistical reasoning","A/B testing","Data interpretation"].map(skill => 
                    <Chip key={skill} name={skill} level="ok"/>
                  )}
                </div>
                <div style={{ fontSize:12, color:"var(--t3)", marginTop:8 }}>
                  These give you more credit than they appear on paper.
                </div>
              </div>
            )}
          </Card>

          {/* Gap Analysis */}
          <Card className="gl" style={{ padding:24 }}>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:14 }}>
              <div style={{ fontSize:14, fontWeight:600, color:"var(--t1)" }}>
                Gap Analysis
              </div>
              <Chip name={`${gaps.length} gaps`} level="bad"/>
            </div>
            {gaps.map(gap => (
              <div key={gap.n} style={{ 
                marginBottom:10, 
                padding:"10px 14px", 
                background:"rgba(255,255,255,.03)", 
                borderRadius:"var(--rm)", 
                border:"1px solid var(--gb)" 
              }}>
                <div style={{ display:"flex", alignItems:"center", gap:7, marginBottom:4 }}>
                  <span style={{ fontSize:13, fontWeight:500, color:"var(--t1)" }}>
                    {gap.n}
                  </span>
                  <Chip 
                    name={gap.p} 
                    level={gap.p === "Critical" ? "bad" : "learn"} 
                    style={{ fontSize:10, padding:"2px 6px" }} 
                  />
                </div>
                <div style={{ fontSize:11.5, color:"var(--t3)", marginBottom:6 }}>
                  {gap.reason}
                </div>
                <ProgressBar 
                  v={gap.d} 
                  color={gap.p === "Critical" ? "#f43f5e" : "#f59e0b"}
                />
              </div>
            ))}
          </Card>
        </div>

        {/* City-specific salary band */}
        <Card className="gl" style={{ 
          padding:20, 
          marginBottom:14, 
          display:"flex", 
          alignItems:"center", 
          gap:16, 
          justifyContent:"space-between" 
        }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <Icon name="pin" s={18} c="var(--p3)"/>
            <div>
              <div style={{ fontSize:13.5, fontWeight:600, color:"var(--t1)" }}>
                Data Scientist Salary in {profile?.city || "Bengaluru"}
              </div>
              <div style={{ fontSize:12, color:"var(--t3)" }}>
                Based on current market data for your city
              </div>
            </div>
          </div>
          <div style={{ display:"flex", gap:24, textAlign:"center" }}>
            {[["Min", salary.min],["Median", salary.median],["Max", salary.max]].map(([label, value]) => (
              <div key={label}>
                <div style={{ fontSize:11, color:"var(--t3)" }}>{label}</div>
                <div style={{ fontFamily:"'Fraunces',serif", fontSize:20, color:"var(--t1)" }}>
                  {value}
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Check-in reminder */}
        <div style={{ 
          background:"rgba(99,102,241,.07)", 
          border:"1px solid rgba(99,102,241,.2)", 
          borderRadius:"var(--rm)", 
          padding:"14px 18px", 
          display:"flex", 
          alignItems:"center", 
          gap:12 
        }}>
          <Icon name="refresh" s={18} c="var(--i2)"/>
          <div style={{ flex:1 }}>
            <div style={{ fontSize:13.5, fontWeight:600, color:"var(--t1)" }}>
              Come back in 2 weeks
            </div>
            <div style={{ fontSize:12.5, color:"var(--t3)" }}>
              Re-upload your resume to track your score improvement. We'll remind you.
            </div>
          </div>
          <Button size="small">Set reminder</Button>
        </div>
      </div>
    </div>
  );
};

export default Resume;
