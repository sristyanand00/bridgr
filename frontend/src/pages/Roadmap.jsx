import React from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon } from '../components/ui';

const Roadmap = ({ profile }) => {
  const hoursMap = { 
    "Less than 3 hours": 3, 
    "3–7 hours": 5, 
    "7–15 hours": 10, 
    "15+ hours": 18 
  };
  const hours = hoursMap[profile?.hours] || 10;
  const baseWeeks = 14;
  const adjustedWeeks = Math.round(baseWeeks * (10 / hours));

  const phases = [
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

  const progressMetrics = [
    { label: "Overall Progress", value: 28, bar: true },
    { label: "Weeks Remaining", value: `${Math.round(adjustedWeeks * 0.72)} weeks`, bar: false },
    { label: "Skills Completed", value: "3 of 14", bar: false }
  ];

  return (
    <div className="main">
      <Topbar 
        title="Learning Roadmap" 
        sub={`Adjusted for ${profile?.hours || "7–15 hours"}/week`}
        right={
          <>
            <Chip name="AI Generated" className="tv" style={{ fontSize:10 }} />
            <Button size="small" style={{ marginLeft:8 }}>
              Edit Goals
            </Button>
          </>
        }
      />
      
      <div className="page">
        {/* Timeline adjustment callout */}
        <div style={{ 
          background:"rgba(139,92,246,.07)", 
          border:"1px solid rgba(139,92,246,.18)", 
          borderRadius:"var(--rm)", 
          padding:"13px 18px", 
          marginBottom:16, 
          display:"flex", 
          alignItems:"center", 
          gap:10 
        }}>
          <Icon name="clock" s={17} c="var(--p3)"/>
          <div>
            <span style={{ fontSize:13.5, color:"var(--t1)", fontWeight:600 }}>
              Timeline: {adjustedWeeks} weeks total
            </span>
            <span style={{ fontSize:13, color:"var(--t3)", marginLeft:8 }}>
              at {profile?.hours || "7–15 hours"}/week · Standard 10h/week plan is {baseWeeks} weeks
              {hours < 10 ? ` — adjusted longer for your schedule` : hours > 10 ? ` — you'll finish faster` : ``}
            </span>
          </div>
        </div>

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
