import React, { useState, useEffect } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, Counter, Ring, ProgressBar, Icon } from '../components/ui';
import { auth } from '../config/firebase';

const Dashboard = ({ setCurrentPage, profile, analysisData, mobileMenuOpen, setMobileMenuOpen }) => {
  const city = profile?.city || "Bengaluru";

  const features = [
    {
      icon: "📄",
      title: "Resume Analysis",
      description: "AI-powered resume scoring and skill gap analysis",
      action: "Analyze Resume",
      page: "resume",
      color: "#8b5cf6"
    },
    {
      icon: "🤖",
      title: "AI Career Coach",
      description: "Personalized career guidance and advice",
      action: "Chat Now",
      page: "chat",
      color: "#3b82f6"
    },
    {
      icon: "📊",
      title: "Market Insights",
      description: "Real-time job market data and salary trends",
      action: "Explore",
      page: "market",
      color: "#10b981"
    },
    {
      icon: "�",
      title: "Career Change Feasibility",
      description: "Assess career change viability & generate personalized roadmap",
      action: "Explore Now",
      page: "roadmap",
      color: "#f59e0b"
    },
    {
      icon: "🎯",
      title: "Mock Interviews",
      description: "Practice with AI feedback and coaching",
      action: "Practice",
      page: "interview",
      color: "#ef4444"
    },
    {
      icon: "📈",
      title: "Progress Tracking",
      description: "Monitor your career growth journey",
      action: "Track Progress",
      page: "dashboard",
      color: "#6366f1"
    }
  ];

  
  return (
    <div className="main">
      <Topbar 
        title="Dashboard" 
        sub={`Good morning, ${(profile?.name || "Ananya").split(" ")[0]}`}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />
      
      <div className="page">
        {/* PROMINENT RESUME UPLOAD CARD */}
        <Card className="gl afu d1" style={{ 
          marginBottom:24, 
          padding:32, 
          background:"linear-gradient(135deg, rgba(139,92,246,.1), rgba(59,130,246,.1))",
          border:"1px solid rgba(139,92,246,.2)"
        }}>
          <div style={{ 
            display:"flex", 
            alignItems:"center", 
            justifyContent:"space-between", 
            gap:24 
          }}>
            <div style={{ flex:1 }}>
              <div style={{ 
                fontSize:32, 
                fontWeight:600, 
                color:"var(--t1)", 
                marginBottom:12,
                fontFamily:"'Fraunces', serif"
              }}>
                📄 Start Your Career Transition
              </div>
              <div style={{ 
                fontSize:16, 
                color:"var(--t2)", 
                marginBottom:20,
                lineHeight:1.5
              }}>
                Upload your resume and select your target role. Our AI will analyze your skills, 
                identify gaps, and generate a personalized roadmap to help you successfully transition to your dream career.
              </div>
              <Button 
                size="medium" 
                onClick={() => setCurrentPage("resume")}
                style={{ 
                  background:"linear-gradient(135deg, #8b5cf6, #3b82f6)",
                  border:"none",
                  fontSize:16,
                  padding:"14px 28px"
                }}
              >
                <Icon name="upload" s={16} c="white"/>
                Upload Resume & Get Roadmap
              </Button>
            </div>
            <div style={{ 
              fontSize:80, 
              opacity:0.3,
              display:"flex",
              alignItems:"center",
              justifyContent:"center"
            }}>
              📄
            </div>
          </div>
        </Card>

        
        {/* FEATURES GRID */}
        <div style={{ marginBottom:24 }}>
          <div style={{ 
            fontSize:20, 
            fontWeight:600, 
            color:"var(--t1)", 
            marginBottom:16,
            fontFamily:"'Fraunces', serif"
          }}>
            Explore All Features
          </div>
          <div style={{ 
            display:"grid", 
            gridTemplateColumns:"repeat(auto-fit, minmax(300px, 1fr))", 
            gap:16 
          }}>
            {features.map((feature, index) => (
              <Card 
                key={index} 
                className="gl afu d2"
                style={{ 
                  padding:20, 
                  cursor:"pointer",
                  transition:"all 0.3s ease",
                  border:`1px solid ${feature.color}20`
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.background = `${feature.color}08`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.background = "rgba(255,255,255,0.02)";
                }}
                onClick={() => setCurrentPage(feature.page)}
              >
                <div style={{ 
                  display:"flex", 
                  alignItems:"center", 
                  gap:12, 
                  marginBottom:12 
                }}>
                  <div style={{ 
                    fontSize:32, 
                    width:48, 
                    height:48, 
                    display:"flex", 
                    alignItems:"center", 
                    justifyContent:"center",
                    background:`${feature.color}15`,
                    borderRadius:12
                  }}>
                    {feature.icon}
                  </div>
                  <div style={{ flex:1 }}>
                    <div style={{ 
                      fontSize:16, 
                      fontWeight:600, 
                      color:"var(--t1)",
                      marginBottom:2
                    }}>
                      {feature.title}
                    </div>
                    <div style={{ 
                      fontSize:12, 
                      color:"var(--t3)" 
                    }}>
                      {feature.description}
                    </div>
                  </div>
                </div>
                <Button 
                  size="small" 
                  style={{ 
                    background:`${feature.color}`,
                    border:"none",
                    fontSize:13
                  }}
                >
                  {feature.action}
                </Button>
              </Card>
            ))}
          </div>
        </div>

        {/* QUICK STATS */}
        <div className="b4 afu d3" style={{ marginBottom:14 }}>
          <Card className="gl" style={{ padding:20 }}>
            <div style={{ fontSize:14, fontWeight:600, marginBottom:16, color:"var(--t1)" }}>
              Quick Stats
            </div>
            <div style={{ display:"flex", justifyContent:"space-around", textAlign:"center" }}>
              <div>
                <div style={{ 
                  fontFamily:"'Fraunces',serif", 
                  fontSize:28, 
                  fontWeight:300, 
                  color:"var(--t1)" 
                }}>
                  {analysisData?.match_score || "--"}
                </div>
                <div style={{ fontSize:12, color:"var(--t3)" }}>Resume Score</div>
              </div>
              <div>
                <div style={{ 
                  fontFamily:"'Fraunces',serif", 
                  fontSize:28, 
                  fontWeight:300, 
                  color:"var(--t1)" 
                }}>
                  {analysisData?.matched_skills?.length || 0}
                </div>
                <div style={{ fontSize:12, color:"var(--t3)" }}>Skills Matched</div>
              </div>
              <div>
                <div style={{ 
                  fontFamily:"'Fraunces',serif", 
                  fontSize:28, 
                  fontWeight:300, 
                  color:"var(--t1)" 
                }}>
                  {profile?.daysActive || 1}
                </div>
                <div style={{ fontSize:12, color:"var(--t3)" }}>Days Active</div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
