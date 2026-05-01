import React, { useState } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon } from '../components/ui';

const Roadmap = ({ profile, analysisData }) => {
  const [currentCareer, setCurrentCareer] = useState(profile?.currentRole || "Software Engineer");
  const [targetCareer, setTargetCareer] = useState("");
  const [assessmentComplete, setAssessmentComplete] = useState(!!analysisData);
  const [feasibilityScore, setFeasibilityScore] = useState(analysisData?.score || 0);
  const [roadmapLoading, setRoadmapLoading] = useState(false);
  const [generatedPhases, setGeneratedPhases] = useState(null);
  const [error, setError] = useState("");

  const careerOptions = [
    "Data Scientist", "Product Manager", "UX Designer", "DevOps Engineer",
    "Machine Learning Engineer", "Full Stack Developer", "Backend Engineer",
    "Frontend Developer", "Mobile Developer", "Cloud Architect"
  ];

  const hoursMap = { 
    "Less than 3 hours": 3, 
    "3–7 hours": 5, 
    "7–15 hours": 10, 
    "15+ hours": 18 
  };
  const hours = hoursMap[profile?.hours] || 10;
  const baseWeeks = 14;
  const adjustedWeeks = Math.round(baseWeeks * (10 / hours));

  const fallbackPhases = [
      { 
        label: "Phase 1 — Foundation", 
        weeks: `Weeks 1–${Math.round(adjustedWeeks * 0.28)}`, 
        done: true, 
        skills: ["SQL Fundamentals", "Window Functions", "Database Design"], 
        milestone: "Mode Analytics Tutorial + 20 LeetCode SQL problems", 
        resources: [
          { name: "Mode Analytics", url: "mode.com", free: true }, 
          { name: "LeetCode SQL", url: "leetcode.com", free: true }
        ]
      },
      { 
        label: "Phase 2 — Core Skills", 
        weeks: `Weeks ${Math.round(adjustedWeeks * 0.28)}–${Math.round(adjustedWeeks * 0.6)}`, 
        active: true, 
        skills: ["Feature Engineering", "scikit-learn Pipelines", "Model Evaluation"], 
        milestone: "2 end-to-end Kaggle projects with full feature pipelines", 
        resources: [
          { name: "Kaggle Learn", url: "kaggle.com", free: true }, 
          { name: "Hands-On ML (Géron)", url: "oreilly.com", free: false }
        ]
      },
      { 
        label: "Phase 3 — Production", 
        weeks: `Weeks ${Math.round(adjustedWeeks * 0.6)}–${Math.round(adjustedWeeks * 0.85)}`, 
        skills: ["Docker Basics", "FastAPI for ML", "Model Deployment"], 
        milestone: "Deploy a live model API to Railway or Render", 
        resources: [
          { name: "MLOps Zoomcamp", url: "github.com", free: true }, 
          { name: "FastAPI docs", url: "fastapi.tiangolo.com", free: true }
        ]
      },
      { 
        label: "Phase 4 — Apply", 
        weeks: `Weeks ${Math.round(adjustedWeeks * 0.85)}–${adjustedWeeks}`, 
        skills: ["System Design for ML", "Behavioral Prep", "Portfolio Polish"], 
        milestone: "5 targeted applications/week + mock interview weekly", 
        resources: [
          { name: "Designing ML Systems", url: "oreilly.com", free: false }
        ]
      },
    ];

  const phases = React.useMemo(() => {
    return generatedPhases || fallbackPhases;
  }, [generatedPhases, fallbackPhases]);

  const calculateFeasibility = async () => {
    if (!targetCareer) {
      setError("Please select a target career");
      return;
    }
    
    setRoadmapLoading(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/roadmap`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_role: targetCareer,
          match_score: analysisData?.match_score || 0,
          readiness_level: analysisData?.readiness_level || "Foundation Stage",
          roadmap_inputs: analysisData?.learning_roadmap_inputs || {},
          matched_skills: analysisData?.matched_skills || [],
          missing_required: analysisData?.missing_required || []
        })
      });
      
      const roadmapData = await response.json();
      setGeneratedPhases(roadmapData.phases);
      setFeasibilityScore(analysisData?.match_score || 65);
      setAssessmentComplete(true);
      
    } catch (error) {
      console.error('Failed to generate roadmap:', error);
      setError("Failed to generate roadmap. Please try again.");
      // Fallback to client-side generation
      setFeasibilityScore(65);
      setAssessmentComplete(true);
    } finally {
      setRoadmapLoading(false);
    }
  };

  // Initialize with analysis data if available
  React.useEffect(() => {
    if (analysisData && analysisData.target_role) {
      setTargetCareer(analysisData.target_role);
      setAssessmentComplete(true);
      setFeasibilityScore(analysisData.score);
    }
  }, [analysisData]);

  const progressMetrics = assessmentComplete ? [
    { label: "Career Change Feasibility", value: feasibilityScore, bar: true },
    { label: "Estimated Timeline", value: `${Math.round(adjustedWeeks * (100 / feasibilityScore))} weeks`, bar: false },
    { label: "Skills to Bridge", value: `${Math.max(3, Math.round(15 - (feasibilityScore / 10)))} skills`, bar: false }
  ] : [
    { label: "Overall Progress", value: 28, bar: true },
    { label: "Weeks Remaining", value: `${Math.round(adjustedWeeks * 0.72)} weeks`, bar: false },
    { label: "Skills Completed", value: "3 of 14", bar: false }
  ];

  return (
    <div className="main">
      <Topbar 
        title="Your Career Transition Roadmap" 
        sub={assessmentComplete ? `Roadmap to becoming a ${targetCareer}` : "Plan your move to a new career"}
        right={
          <>
            <Chip name="AI Powered" className="tv" style={{ fontSize:10 }} />
            <Button size="small" style={{ marginLeft:8 }} onClick={() => setAssessmentComplete(false)}>
              Start New Roadmap
            </Button>
          </>
        }
      />
      
      <div className="page">
        {/* Career Transition Journey */}
        {!assessmentComplete ? (
          <Card className="gl" style={{ padding:30, marginBottom:16 }}>
            <div style={{ 
              fontSize:24, 
              fontWeight:600, 
              marginBottom:16, 
              color:"var(--t1)",
              fontFamily:"'Fraunces', serif",
              textAlign: "center"
            }}>
              � Ready for Your Next Chapter?
            </div>
            
            <div style={{ 
              fontSize:16, 
              color:"var(--t2)", 
              marginBottom:32, 
              textAlign: "center",
              lineHeight: 1.6
            }}>
              Every career change begins with a single step. Let's create your personalized roadmap 
              to transform your professional journey and unlock new opportunities.
            </div>
            
            <div style={{ marginBottom:24 }}>
              <div style={{ fontSize:14, color:"var(--t2)", marginBottom:8 }}>
                Where are you now?
              </div>
              <select 
                value={currentCareer}
                onChange={(e) => setCurrentCareer(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid var(--gb)",
                  borderRadius: "8px",
                  color: "var(--t1)",
                  fontSize: "14px"
                }}
              >
                <option value="Software Engineer">Software Engineer</option>
                <option value="Product Manager">Product Manager</option>
                <option value="Data Scientist">Data Scientist</option>
                <option value="UX Designer">UX Designer</option>
              </select>
            </div>

            <div style={{ marginBottom:32 }}>
              <div style={{ fontSize:14, color:"var(--t2)", marginBottom:8 }}>
                Where do you want to be?
              </div>
              <select 
                value={targetCareer}
                onChange={(e) => setTargetCareer(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid var(--gb)",
                  borderRadius: "8px",
                  color: "var(--t1)",
                  fontSize: "14px"
                }}
              >
                <option value="">Choose your dream career</option>
                {careerOptions.map(career => (
                  <option key={career} value={career}>{career}</option>
                ))}
              </select>
            </div>

            <Button 
              size="medium" 
              onClick={calculateFeasibility}
              disabled={!targetCareer}
              style={{ 
                background: targetCareer ? "linear-gradient(135deg, #8b5cf6, #3b82f6)" : "var(--t4)",
                border: "none",
                fontSize: 16,
                padding: "16px 32px",
                width: "100%"
              }}
            >
              <Icon name="route" s={16} c="white"/>
              Generate My Career Roadmap
            </Button>
          </Card>
        ) : (
          /* Personalized Roadmap */
          <Card className="gl" style={{ padding:30, marginBottom:16 }}>
            <div style={{ 
              fontSize:24, 
              fontWeight:600, 
              marginBottom:20, 
              color:"var(--t1)",
              fontFamily:"'Fraunces', serif",
              textAlign: "center"
            }}>
              🎯 Your Journey to {targetCareer}
            </div>
            
            <div style={{ 
              background: "linear-gradient(135deg, rgba(139,92,246,.1), rgba(59,130,246,.1))",
              border: "1px solid rgba(139,92,246,.2)",
              borderRadius: "12px",
              padding: "20px",
              marginBottom:24,
              textAlign: "center"
            }}>
              <div style={{ 
                fontSize:18, 
                fontWeight:600, 
                marginBottom:8,
                color: "var(--t1)"
              }}>
                Your Career Transition is {feasibilityScore}% Achievable
              </div>
              <div style={{ fontSize:14, color:"var(--t2)" }}>
                {feasibilityScore > 70 ? "🎉 You're perfectly positioned for this transition!" :
                 feasibilityScore > 50 ? "💪 With dedication, this transition is very achievable!" :
                 "🔥 This will be challenging, but your determination will make it possible!"}
              </div>
            </div>

            <div style={{ 
              fontSize:16, 
              color:"var(--t1)", 
              marginBottom:20,
              fontWeight: 600
            }}>
              📍 Your Transition Timeline
            </div>
            
            <div style={{ 
              background: "rgba(255,255,255,0.02)",
              border: "1px solid var(--gb)",
              borderRadius: "8px",
              padding: "16px",
              marginBottom:24
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom:8 }}>
                <span style={{ color: "var(--t2)" }}>From:</span>
                <span style={{ color: "var(--t1)", fontWeight: 600 }}>{currentCareer}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom:8 }}>
                <span style={{ color: "var(--t2)" }}>To:</span>
                <span style={{ color: "var(--t1)", fontWeight: 600 }}>{targetCareer}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom:8 }}>
                <span style={{ color: "var(--t2)" }}>Duration:</span>
                <span style={{ color: "var(--t1)", fontWeight: 600 }}>{Math.round(adjustedWeeks * (100 / feasibilityScore))} weeks</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--t2)" }}>Focus Areas:</span>
                <span style={{ color: "var(--t1)", fontWeight: 600 }}>{Math.max(3, Math.round(15 - (feasibilityScore / 10)))} key skills</span>
              </div>
            </div>

            <div style={{ 
              fontSize:16, 
              color:"var(--t1)", 
              marginBottom:16,
              fontWeight: 600
            }}>
              🗺️ Your Personalized Roadmap
            </div>
            
            <div style={{ fontSize:14, color:"var(--t2)", marginBottom:16, lineHeight: 1.6 }}>
              Based on your background and goals, I've created a step-by-step plan to guide your transition. 
              Each phase builds upon the previous one, ensuring you develop the right skills at the right time.
            </div>
          </Card>
        )}

        {/* Progress Metrics */}
        <div className="b3" style={{ marginBottom:16 }}>
          {progressMetrics.map(metric => (
            <Card key={metric.label}>
              <div style={{ fontSize:12, color:"var(--t3)", marginBottom:10 }}>
                {metric.label}
              </div>
              {metric.bar ? (
                <>
                  <div style={{ 
                    fontFamily:"'Fraunces',serif", 
                    fontSize:30, 
                    fontWeight:300, 
                    marginBottom:10 
                  }}>
                    {metric.value}%
                  </div>
                  <ProgressBar value={metric.value} />
                </>
              ) : (
                <div style={{ 
                  fontFamily:"'Fraunces',serif", 
                  fontSize:28, 
                  fontWeight:300 
                }}>
                  {metric.value}
                </div>
              )}
            </Card>
          ))}
        </div>

        {/* Timeline Phases */}
        <Card className="gl" style={{ padding:30 }}>
          <div style={{ 
            fontSize:15, 
            fontWeight:600, 
            marginBottom:28, 
            color:"var(--t1)" 
          }}>
            30/60/90 Day Plan — Data Scientist
          </div>
          
          {phases.map((phase, index) => (
            <div 
              key={phase.label} 
              style={{ 
                position:"relative", 
                paddingLeft:30, 
                marginBottom:index < phases.length - 1 ? 32 : 0 
              }}
            >
              {index < phases.length - 1 && <div className="tl-line"/>}
              
              <div style={{ 
                position:"absolute", 
                left:0, 
                top:4, 
                width:22, 
                height:22, 
                borderRadius:"50%", 
                border:`2px solid ${phase.done ? "var(--g)" : phase.active ? "var(--p)" : "var(--t4)"}`, 
                background:phase.done ? "var(--g)" : phase.active ? "rgba(139,92,246,.15)" : "transparent", 
                display:"flex", 
                alignItems:"center", 
                justifyContent:"center", 
                boxShadow:phase.active ? "0 0 14px rgba(139,92,246,.4)" : "none" 
              }}>
                {phase.done && <Icon name="check" s={10} c="white"/>}
                {phase.active && (
                  <div style={{ 
                    width:6, 
                    height:6, 
                    borderRadius:"50%", 
                    background:"var(--p3)" 
                  }}/>
                )}
              </div>
              
              <div style={{ 
                background:phase.active ? "rgba(139,92,246,.05)" : "transparent", 
                borderRadius:"var(--rl)", 
                padding:phase.active ? "18px" : "0 0 0 4px", 
                border:phase.active ? "1px solid rgba(139,92,246,.18)" : "none" 
              }}>
                <div style={{ 
                  display:"flex", 
                  justifyContent:"space-between", 
                  marginBottom:10 
                }}>
                  <div>
                    <div style={{ 
                      fontWeight:600, 
                      fontSize:14, 
                      color:"var(--t1)", 
                      marginBottom:3 
                    }}>
                      {phase.label}
                    </div>
                    <div style={{ fontSize:12, color:"var(--t3)" }}>
                      {phase.weeks}
                    </div>
                  </div>
                  {phase.done && <Chip name="Completed" level="ok"/>}
                  {phase.active && <Chip name="In Progress" className="tv"/>}
                </div>
                
                <div style={{ 
                  display:"flex", 
                  flexWrap:"wrap", 
                  gap:6, 
                  marginBottom:10 
                }}>
                  {phase.skills.map(skill => (
                    <Chip 
                      key={skill} 
                      name={skill} 
                      level={phase.done ? "ok" : phase.active ? "learn" : "n"}
                    />
                  ))}
                </div>
                
                <div style={{ 
                  fontSize:13, 
                  color:"var(--t2)", 
                  marginBottom:12 
                }}>
                  <strong style={{ color:"var(--t1)" }}>Milestone:</strong> {phase.milestone}
                </div>
                
                {/* Resources */}
                <div style={{ display:"flex", gap:7, flexWrap:"wrap" }}>
                  {phase.resources.map(resource => (
                    <div 
                      key={resource.name}
                      className="res-link" 
                      style={{ fontSize:12 }}
                    >
                      <Icon name="link" s={13} c="var(--p3)"/>
                      <span style={{ color:"var(--t1)" }}>{resource.name}</span>
                      {resource.free && (
                        <Chip name="Free" level="ok" style={{ fontSize:10, padding:"1px 6px" }} />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
};

export default Roadmap;
