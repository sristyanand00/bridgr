import React from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon } from '../components/ui';
import { SKILLS_DATA, USER_GAPS } from '../constants/skills';

const Market = ({ profile, analysisData }) => {
  const city = profile?.city || "Bengaluru";
  
  // Intersection: user's gaps that are also high-demand
  const personalROI = SKILLS_DATA
    .filter(skill => USER_GAPS.includes(skill.n))
    .sort((a, b) => b.d - a.d);

  const companies = [
    { name: "Flipkart", openings: 124, role: "Data Scientist" },
    { name: "Razorpay", openings: 87, role: "ML Engineer" },
    { name: "Zomato", openings: 63, role: "Data Analyst" },
    { name: "CRED", openings: 41, role: "Data Scientist" },
    { name: "PhonePe", openings: 78, role: "ML Engineer" },
  ];

  const marketMetrics = [
    { 
      label: `Active DS Jobs in ${city}`, 
      value: "4,280", 
      delta: "+12% this week", 
      icon: "trend", 
      color: "var(--g)" 
    },
    { 
      label: `Median Salary (DS, ${city})`, 
      value: "₹14.5L", 
      delta: "+6% YoY", 
      icon: "award", 
      color: "var(--p3)" 
    },
    { 
      label: "Hottest Skill", 
      value: "LLMOps", 
      delta: "+210% demand YoY", 
      icon: "zap", 
      color: "var(--a)" 
    }
  ];

  return (
    <div className="main">
      <Topbar 
        title="Market Pulse" 
        sub={`${city} hiring intelligence · Updated 2h ago`}
        right={
          <select className="inp" style={{ width:"auto", fontSize:13, padding:"6px 12px" }}>
            <option>India — All Cities</option>
            <option selected>{city}</option>
            <option>Mumbai</option>
            <option>Delhi / NCR</option>
          </select>
        }
      />
      
      <div className="page">
        {/* Market Metrics */}
        <div className="b3" style={{ marginBottom:14 }}>
          {marketMetrics.map(metric => (
            <Card key={metric.label}>
              <div style={{ 
                display:"flex", 
                justifyContent:"space-between", 
                marginBottom:14 
              }}>
                <span style={{ fontSize:12, color:"var(--t3)" }}>
                  {metric.label}
                </span>
                <Icon name={metric.icon} s={16} c={metric.color}/>
              </div>
              <div style={{ 
                fontFamily:"'Fraunces',serif", 
                fontSize:30, 
                fontWeight:300, 
                marginBottom:6, 
                color:"var(--t1)" 
              }}>
                {metric.value}
              </div>
              <div style={{ fontSize:12, color:"var(--g)" }}>
                {metric.delta}
              </div>
            </Card>
          ))}
        </div>

        {/* Personal ROI Section */}
        <Card 
          className="gl" 
          style={{ 
            padding:24, 
            marginBottom:14, 
            borderColor:"rgba(139,92,246,.25)" 
          }}
        >
          <div style={{ 
            display:"flex", 
            alignItems:"center", 
            gap:8, 
            marginBottom:16 
          }}>
            <Icon name="sparkle" s={18} c="var(--p3)"/>
            <div>
              <div style={{ 
                fontSize:14, 
                fontWeight:600, 
                color:"var(--t1)" 
              }}>
                Your Personal ROI Map
              </div>
              <div style={{ fontSize:12, color:"var(--t3)" }}>
                Your gaps that are also trending in {city} right now — highest-leverage skills
              </div>
            </div>
          </div>
          
          {personalROI.map((skill, index) => (
            <div key={skill.n} className="insight-row">
              <div style={{ 
                width:28, 
                height:28, 
                borderRadius:8, 
                background:"rgba(139,92,246,.15)", 
                display:"flex", 
                alignItems:"center", 
                justifyContent:"center", 
                flexShrink:0, 
                fontFamily:"'Fraunces',serif", 
                fontWeight:300, 
                fontSize:15, 
                color:"var(--p3)" 
              }}>
                {index + 1}
              </div>
              <div style={{ flex:1 }}>
                <div style={{ 
                  display:"flex", 
                  alignItems:"center", 
                  gap:8, 
                  marginBottom:4 
                }}>
                  <span style={{ 
                    fontSize:14, 
                    fontWeight:600, 
                    color:"var(--t1)" 
                  }}>
                    {skill.n}
                  </span>
                  <Chip 
                    name={`Your Gap #${index + 1}`} 
                    level="bad" 
                    style={{ fontSize:10, padding:"2px 6px" }} 
                  />
                  <Chip 
                    name={`${skill.d}% market demand`} 
                    className="tv" 
                    style={{ fontSize:10, padding:"2px 6px" }} 
                  />
                  <Chip 
                    name={`↑ ${skill.g}% growth`} 
                    level="ok" 
                    style={{ fontSize:10, padding:"2px 6px" }} 
                  />
                </div>
                <div style={{ fontSize:12.5, color:"var(--t2)" }}>
                  {skill.n} is your #{index + 1} skill gap <strong style={{ color:"var(--t1)" }}>AND</strong> appears in {skill.d}% of {city} DS job postings. Closing this gap has the highest return on your study hours.
                </div>
              </div>
              <ProgressBar value={skill.d} />
            </div>
          ))}
        </Card>

        <div className="b2">
          {/* Full Skill Demand */}
          <Card className="gl" style={{ padding:24 }}>
            <div style={{ 
              fontSize:14, 
              fontWeight:600, 
              marginBottom:18, 
              color:"var(--t1)" 
            }}>
              Full Skill Demand — {city}
            </div>
            {SKILLS_DATA.slice(0, 8).map(skill => (
              <div key={skill.n} style={{ marginBottom:13 }}>
                <div style={{ 
                  display:"flex", 
                  justifyContent:"space-between", 
                  fontSize:13, 
                  marginBottom:5 
                }}>
                  <div style={{ display:"flex", alignItems:"center", gap:7 }}>
                    <span style={{ 
                      color:USER_GAPS.includes(skill.n) ? "var(--t1)" : "var(--t2)" 
                    }}>
                      {skill.n}
                    </span>
                    {USER_GAPS.includes(skill.n) && (
                      <span style={{ 
                        fontSize:10, 
                        color:"var(--p3)", 
                        background:"rgba(139,92,246,.12)", 
                        padding:"1px 6px", 
                        borderRadius:100 
                      }}>
                        Your gap
                      </span>
                    )}
                  </div>
                  <span style={{ display:"flex", gap:12 }}>
                    <span style={{ color:"var(--t3)" }}>{skill.d}%</span>
                    <span style={{ 
                      color:skill.g > 0 ? "var(--g)" : "var(--r)", 
                      fontWeight:600 
                    }}>
                      {skill.g > 0 ? "↑" : "↓"}{Math.abs(skill.g)}%
                    </span>
                  </span>
                </div>
                <ProgressBar 
                  value={skill.d} 
                  color={USER_GAPS.includes(skill.n) ? "#8b5cf6" : undefined}
                />
              </div>
            ))}
          </Card>

          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            {/* Emerging Skills Heatmap */}
            <Card className="gl" style={{ padding:22 }}>
              <div style={{ 
                fontSize:13.5, 
                fontWeight:600, 
                marginBottom:14, 
                color:"var(--t1)" 
              }}>
                Emerging Skills Heatmap
              </div>
              <div style={{ 
                display:"grid", 
                gridTemplateColumns:"repeat(4,1fr)", 
                gap:6 
              }}>
                {SKILLS_DATA.map(skill => {
                  const intensity = Math.min(1, Math.abs(skill.g) / 220);
                  const isWarm = skill.g > 50;
                  return (
                    <div 
                      key={skill.n}
                      className="hmc" 
                      style={{ 
                        background:isWarm ? 
                          `rgba(245,158,11,${0.08 + intensity * 0.6})` : 
                          `rgba(139,92,246,${0.08 + intensity * 0.4})`, 
                        padding:"9px 5px", 
                        textAlign:"center", 
                        border:USER_GAPS.includes(skill.n) ? 
                          "1px solid rgba(244,63,94,.3)" : "none" 
                      }}
                    >
                      <div style={{ 
                        fontSize:9.5, 
                        fontWeight:600, 
                        color:"var(--t1)", 
                        marginBottom:2, 
                        lineHeight:1.3 
                      }}>
                        {skill.n}
                      </div>
                      <div style={{ 
                        fontSize:9.5, 
                        color:isWarm ? "#fcd34d" : "var(--p3)", 
                        fontWeight:600 
                      }}>
                        {skill.g > 0 ? "+" : ""}{skill.g}%
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Top Companies */}
            <Card className="gl" style={{ padding:22 }}>
              <div style={{ 
                fontSize:13.5, 
                fontWeight:600, 
                marginBottom:14, 
                color:"var(--t1)" 
              }}>
                Top Companies in {city}
              </div>
              {companies.map((company, index) => (
                <div 
                  key={company.name}
                  style={{ 
                    display:"flex", 
                    alignItems:"center", 
                    gap:10, 
                    padding:"9px 0", 
                    borderBottom:index < companies.length - 1 ? "1px solid var(--gb)" : "none" 
                  }}
                >
                  <div style={{ 
                    width:30, 
                    height:30, 
                    borderRadius:8, 
                    background:"rgba(139,92,246,.1)", 
                    display:"flex", 
                    alignItems:"center", 
                    justifyContent:"center", 
                    fontWeight:600, 
                    fontSize:12, 
                    color:"var(--p3)", 
                    flexShrink:0 
                  }}>
                    {company.name[0]}
                  </div>
                  <div style={{ flex:1 }}>
                    <div style={{ 
                      fontSize:13, 
                      fontWeight:600, 
                      color:"var(--t1)" 
                    }}>
                      {company.name}
                    </div>
                    <div style={{ fontSize:11.5, color:"var(--t3)" }}>
                      {company.role}
                    </div>
                  </div>
                  <Chip 
                    name={`${company.openings} open`} 
                    className="tv" 
                    style={{ fontSize:11 }} 
                  />
                </div>
              ))}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Market;
