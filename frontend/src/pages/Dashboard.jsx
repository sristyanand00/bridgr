import React from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, Counter, Ring, ProgressBar, Icon } from '../components/ui';

const Dashboard = ({ setCurrentPage, profile, analysisData }) => {
  const isUrgent = profile?.timeline === "Interview in the next month";
  const city = profile?.city || "Bengaluru";
  const prevScore = 67;
  const currScore = analysisData?.score || 72;

  const metrics = [
    { l:"Career Readiness", v:currScore, sfx:"%", i:"tgt", c:"var(--p)", d:"+8 this week" },
    { l:"Resume Score", v:84, sfx:"/100", i:"file", c:"#8b5cf6", d:"Updated 2d ago" },
    { l:"Skills Matched", v:14, sfx:"/23", i:"check", c:"var(--g)", d:`For Data Scientist` },
    { l:"Study Streak", v:7, sfx:"d", i:"zap", c:"var(--a)", d:"Keep going!" },
  ];

  const readinessBreakdown = [
    ["Technical Skills",78],
    ["Experience Match",65],
    ["Resume Quality",84],
    ["Interview Ready",58]
  ];

  const todayTasks = isUrgent ? [
    { done:true,  t:"2 SQL window function problems", time:"30m", tag:"Critical" },
    { done:false, t:"1 mock behavioral question (recorded)", time:"20m", tag:"Critical" },
    { done:false, t:"Review your top 3 project stories", time:"15m", tag:"High" },
    { done:false, t:"Cold email 2 Bengaluru DS contacts", time:"10m", tag:"High" },
  ] : [
    { done:true,  t:"SQL basics — Module 3", time:"30m", tag:"Learning" },
    { done:false, t:"2 LeetCode medium problems", time:"45m", tag:"DSA" },
    { done:false, t:"Update resume — add recent project", time:"20m", tag:"Resume" },
    { done:false, t:"Mock interview: Behavioral round", time:"30m", tag:"Interview" },
  ];

  return (
    <div className="main">
      <Topbar 
        title="Overview" 
        sub={`Good morning, ${(profile?.name || "Ananya").split(" ")[0]}`}
        right={
          <Button size="small" onClick={() => setCurrentPage("resume")}>
            <Icon name="upload" s={13} c="white"/>
            Upload Resume
          </Button>
        }
      />
      
      <div className="page">
        {/* URGENCY BANNER */}
        {isUrgent && (
          <div className="urgency-bar afu">
            <Icon name="clock" s={18} c="#fda4af"/>
            <div style={{ flex:1 }}>
              <div style={{ fontSize:13.5, fontWeight:600, color:"var(--t1)" }}>
                Interview mode active
              </div>
              <div style={{ fontSize:12.5, color:"var(--t3)" }}>
                You have an interview this month. Today's plan is optimized for speed.
              </div>
            </div>
            <Button size="small" onClick={() => setCurrentPage("interview")}>
              Practice now
            </Button>
          </div>
        )}

        {/* PROGRESS DELTA */}
        <Card className="delta-card afu d1" style={{ marginBottom:14 }}>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
            <div>
              <div style={{ fontSize:12, color:"var(--t3)", marginBottom:4 }}>
                Career Readiness — since last session
              </div>
              <div style={{ display:"flex", alignItems:"baseline", gap:12 }}>
                <span style={{ fontFamily:"'Fraunces',serif", fontSize:42, fontWeight:300, color:"var(--t1)" }}>
                  <Counter to={currScore} suffix="%"/>
                </span>
                <span style={{ fontSize:14, color:"var(--g)", fontWeight:600 }}>
                  ↑ +{currScore - prevScore}pts
                </span>
                <span style={{ fontSize:13, color:"var(--t3)" }}>
                  was {prevScore}%
                </span>
              </div>
            </div>
            <div style={{ display:"flex", gap:16 }}>
              <Ring score={prevScore} size={70} color="rgba(139,92,246,.4)" label="Before"/>
              <Ring score={currScore} size={70} label="Now"/>
            </div>
          </div>
          <div style={{ marginTop:12, fontSize:12.5, color:"var(--t2)" }}>
            <strong style={{ color:"var(--g)" }}>You closed 2 gaps since last session:</strong> NumPy Pipelines, Pandas Data Wrangling
          </div>
        </Card>

        {/* METRICS */}
        <div className="b4 afu d2" style={{ marginBottom:14 }}>
          {metrics.map(metric => (
            <Card key={metric.l}>
              <div style={{ display:"flex", justifyContent:"space-between", marginBottom:14 }}>
                <div style={{ fontSize:12, color:"var(--t3)" }}>{metric.l}</div>
                <div style={{ 
                  width:32, 
                  height:32, 
                  borderRadius:9, 
                  background:`${metric.c}18`, 
                  display:"flex", 
                  alignItems:"center", 
                  justifyContent:"center" 
                }}>
                  <Icon name={metric.i} s={15} c={metric.c}/>
                </div>
              </div>
              <div style={{ 
                fontFamily:"'Fraunces',serif", 
                fontSize:36, 
                fontWeight:300, 
                color:"var(--t1)", 
                lineHeight:1 
              }}>
                <Counter to={metric.v} suffix={metric.sfx}/>
              </div>
              <div style={{ fontSize:12, color:"var(--g)", marginTop:8 }}>
                {metric.d}
              </div>
            </Card>
          ))}
        </div>

        <div className="b2" style={{ marginBottom:14 }}>
          {/* READINESS */}
          <Card className="gl afu d3" style={{ padding:24 }}>
            <div style={{ fontSize:14, fontWeight:600, marginBottom:22, color:"var(--t1)" }}>
              Readiness Breakdown
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:24 }}>
              <Ring score={currScore} size={108}/>
              <div style={{ flex:1 }}>
                {readinessBreakdown.map(([label, value]) => (
                  <div key={label} style={{ marginBottom:13 }}>
                    <div style={{ 
                      display:"flex", 
                      justifyContent:"space-between", 
                      fontSize:12.5, 
                      marginBottom:5 
                    }}>
                      <span style={{ color:"var(--t2)" }}>{label}</span>
                      <span style={{ fontWeight:600, color:"var(--t1)" }}>{value}%</span>
                    </div>
                    <ProgressBar v={value}/>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            {/* Today's plan */}
            <Card className="gl afu d4" style={{ padding:20 }}>
              <div style={{ 
                display:"flex", 
                justifyContent:"space-between", 
                alignItems:"center", 
                marginBottom:14 
              }}>
                <div style={{ fontSize:13.5, fontWeight:600, color:"var(--t1)" }}>
                  {isUrgent ? "⚡ Today — Interview Prep Mode" : "Today's Action Plan"}
                </div>
                <Chip name={city} />
              </div>
              
              {todayTasks.map((task, index) => (
                <div 
                  key={index} 
                  style={{ 
                    display:"flex", 
                    alignItems:"center", 
                    gap:10, 
                    padding:"10px 0", 
                    borderBottom:index < todayTasks.length - 1 ? "1px solid var(--gb)" : "none", 
                    opacity:task.done ? 0.5 : 1 
                  }}
                >
                  <div style={{ 
                    width:18, 
                    height:18, 
                    borderRadius:"50%", 
                    border:`1.5px solid ${task.done ? "var(--g)" : "var(--t4)"}`, 
                    background:task.done ? "var(--g)" : "transparent", 
                    display:"flex", 
                    alignItems:"center", 
                    justifyContent:"center", 
                    flexShrink:0 
                  }}>
                    {task.done && <Icon name="check" s={9} c="white"/>}
                  </div>
                  <span style={{ 
                    flex:1, 
                    fontSize:13, 
                    textDecoration:task.done ? "line-through" : "none", 
                    color:task.done ? "var(--t3)" : "var(--t1)" 
                  }}>
                    {task.t}
                  </span>
                  <span style={{ fontSize:11.5, color:"var(--t3)" }}>
                    {task.time}
                  </span>
                  <Chip 
                    name={task.tag} 
                    level={task.tag === "Critical" ? "bad" : task.tag === "High" ? "learn" : "v"}
                  />
                </div>
              ))}
            </Card>

            {/* Check-in reminder */}
            <div style={{ 
              background:"rgba(99,102,241,.08)", 
              border:"1px solid rgba(99,102,241,.2)", 
              borderRadius:"var(--rm)", 
              padding:"14px 16px", 
              display:"flex", 
              alignItems:"center", 
              gap:10 
            }}>
              <Icon name="refresh" s={16} c="var(--i2)"/>
              <div style={{ flex:1 }}>
                <div style={{ fontSize:13, fontWeight:600, color:"var(--t1)" }}>
                  Set your check-in reminder
                </div>
                <div style={{ fontSize:12, color:"var(--t3)" }}>
                  Re-analyze in 2 weeks to track your score improvement
                </div>
              </div>
              <Button size="small">Remind me</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
