import React, { useState, useEffect } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Ring, Icon, Input } from '../components/ui';
import { useTimer } from '../hooks';

const Interview = () => {
  const [stage, setStage] = useState("setup");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const { seconds, isRunning, start, stop, reset, formattedTime } = useTimer(120);

  const questions = [
    {
      question: "Explain the bias-variance tradeoff and how you'd handle it in practice.",
      type: "ML Theory",
      difficulty: "Medium"
    },
    {
      question: "Write a SQL query to find the top 3 customers by revenue for each city.",
      type: "SQL",
      difficulty: "Hard"
    },
    {
      question: "How would you detect data leakage in a machine learning pipeline?",
      type: "ML Theory",
      difficulty: "Hard"
    },
  ];

  const feedback = [
    {
      area: "Technical Accuracy",
      score: 74,
      comment: "Good understanding of bias-variance, but missed regularization techniques like Ridge/Lasso.",
      weakness: "regularization techniques",
      resource: {
        name: "Hands-On ML — Chapter 4: Regularization", 
        url: "oreilly.com", 
        tag: "Free preview"
      },
    },
    {
      area: "Communication",
      score: 88,
      comment: "Clear structure. Used concrete examples effectively.",
      weakness: null,
    },
    {
      area: "SQL Depth",
      score: 55,
      comment: "Struggled with window functions in the ranking query. The ROW_NUMBER() PARTITION BY pattern is key.",
      weakness: "SQL window functions",
      resource: {
        name: "Mode Analytics — Window Functions Tutorial", 
        url: "mode.com/sql-tutorial/sql-window-functions", 
        tag: "Free"
      },
    },
  ];

  useEffect(() => {
    if (stage === "live" && seconds <= 0) {
      stop();
    }
  }, [seconds, stage, stop]);

  const handleStartSession = () => {
    setStage("live");
    reset();
    start();
  };

  const handleNextQuestion = () => {
    if (questionIndex < questions.length - 1) {
      setQuestionIndex(prev => prev + 1);
      reset();
      setAnswer("");
    } else {
      setStage("results");
      stop();
    }
  };

  const handlePreviousQuestion = () => {
    if (questionIndex > 0) {
      setQuestionIndex(prev => prev - 1);
      reset();
      setAnswer("");
    }
  };

  const handleSubmitSession = () => {
    setStage("results");
    stop();
  };

  const handleNewSession = () => {
    setStage("setup");
    setQuestionIndex(0);
    setAnswer("");
    reset();
  };

  if (stage === "setup") {
    const sessionTypes = [
      { type: "Technical", icon: "brain", description: "SQL + ML Theory", active: true },
      { type: "Behavioral", icon: "award", description: "STAR Questions" },
      { type: "System Design", icon: "trend", description: "Architecture" },
      { type: "Full Round", icon: "zap", description: "Mixed 45min" },
    ];

    const difficulties = ["Easy", "Medium", "Hard", "FAANG"];

    return (
      <div className="main">
        <Topbar title="Mock Interview Simulator"/>
        <div className="page" style={{ maxWidth:580, margin:"0 auto" }}>
          <div style={{ textAlign:"center", marginBottom:36 }}>
            <h1 className="serif" style={{ fontSize:36, marginBottom:10, color:"var(--t1)" }}>
              Targeted mock interviews
            </h1>
            <p style={{ color:"var(--t2)", fontSize:15 }}>
              Questions focus on your weak areas — SQL and Feature Engineering
            </p>
          </div>

          <Card className="gl" style={{ padding:22, marginBottom:12 }}>
            <div className="lbl" style={{ marginBottom:14 }}>Session Type</div>
            <div className="b2" style={{ gap:10 }}>
              {sessionTypes.map(session => (
                <button
                  key={session.type}
                  style={{ 
                    display:"flex", 
                    flexDirection:"column", 
                    alignItems:"center", 
                    gap:8, 
                    padding:16, 
                    background:session.active ? 
                      "rgba(139,92,246,.1)" : 
                      "rgba(255,255,255,.03)", 
                    border:session.active ? 
                      "1px solid rgba(139,92,246,.4)" : 
                      "var(--gb)", 
                    borderRadius:"var(--rl)", 
                    cursor:"none", 
                    fontSize:12.5, 
                    color:session.active ? "var(--p3)" : "var(--t2)", 
                    fontFamily:"'Geist',sans-serif", 
                    fontWeight:500 
                  }}
                >
                  <Icon 
                    name={session.icon} 
                    s={19} 
                    c={session.active ? "var(--p3)" : "var(--t3)"} 
                  />
                  <span style={{ fontWeight:600 }}>{session.type}</span>
                  <span style={{ fontSize:11, color:"var(--t3)" }}>
                    {session.description}
                  </span>
                </button>
              ))}
            </div>
          </Card>

          <Card className="gl" style={{ padding:18, marginBottom:22 }}>
            <div className="lbl" style={{ marginBottom:12 }}>Difficulty</div>
            <div style={{ display:"flex", gap:8 }}>
              {difficulties.map((difficulty, index) => (
                <button
                  key={difficulty}
                  className="btn bgl bsm"
                  style={{ 
                    flex:1, 
                    fontSize:12, 
                    borderColor:index === 1 ? "rgba(139,92,246,.5)" : "var(--gb)", 
                    color:index === 1 ? "var(--p3)" : "var(--t3)" 
                  }}
                >
                  {difficulty}
                </button>
              ))}
            </div>
          </Card>

          <Button 
            style={{ width:"100%", justifyContent:"center", fontSize:15, padding:14 }} 
            onClick={handleStartSession}
          >
            <Icon name="mic" s={17} c="white"/>
            Start Interview Session
          </Button>
        </div>
      </div>
    );
  }

  if (stage === "live") {
    const currentQuestion = questions[questionIndex];
    
    return (
      <div className="main">
        <div style={{ 
          padding:"12px 28px", 
          borderBottom:"1px solid var(--gb)", 
          display:"flex", 
          alignItems:"center", 
          justifyContent:"space-between", 
          background:"rgba(0,0,5,.55)", 
          backdropFilter:"blur(20px)" 
        }}>
          <div style={{ display:"flex", gap:8 }}>
            <span style={{ fontSize:13, color:"var(--t3)" }}>
              Q{questionIndex + 1}/{questions.length}
            </span>
            <Chip name={currentQuestion.type} level="v"/>
            <Chip 
              name={currentQuestion.difficulty} 
              level={currentQuestion.difficulty === "Hard" ? "bad" : "learn"}
            />
          </div>
          <div style={{ display:"flex", alignItems:"center", gap:14 }}>
            <div style={{ 
              fontFamily:"'Fraunces',serif", 
              fontSize:28, 
              color:seconds < 30 ? "var(--r)" : "var(--t1)" 
            }}>
              {formattedTime}
            </div>
            <Button 
              size="small" 
              onClick={() => setStage("results")}
            >
              End Session
            </Button>
          </div>
        </div>

        <div className="page" style={{ maxWidth:680, margin:"0 auto" }}>
          <Card 
            className="gl" 
            style={{ 
              padding:28, 
              marginBottom:18, 
              borderColor:"rgba(139,92,246,.2)" 
            }}
          >
            <div className="lbl" style={{ marginBottom:12 }}>
              Question {questionIndex + 1}
            </div>
            <p style={{ 
              fontSize:18, 
              lineHeight:1.65, 
              fontWeight:500, 
              color:"var(--t1)" 
            }}>
              {currentQuestion.question}
            </p>
          </Card>

          <Input
            rows={9}
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            placeholder="Type your answer here…"
            style={{ 
              resize:"none", 
              marginBottom:16, 
              lineHeight:1.75,
              fontFamily: "'Geist', sans-serif"
            }}
          />

          <div style={{ display:"flex", justifyContent:"flex-end", gap:10 }}>
            {questionIndex > 0 && (
              <Button variant="secondary" onClick={handlePreviousQuestion}>
                ← Previous
              </Button>
            )}
            {questionIndex < questions.length - 1 ? (
              <Button onClick={handleNextQuestion}>
                Next →
              </Button>
            ) : (
              <Button onClick={handleSubmitSession}>
                Submit & Get Feedback →
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main">
      <Topbar 
        title="Interview Results" 
        right={<Button size="small" onClick={handleNewSession}>New Session</Button>}
      />
      <div className="page" style={{ maxWidth:680, margin:"0 auto" }}>
        <div style={{ 
          display:"flex", 
          alignItems:"center", 
          gap:24, 
          padding:"24px 0 32px", 
          flexWrap:"wrap" 
        }}>
          <Ring score={72} size={96}/>
          <div>
            <div className="serif" style={{ fontSize:26, color:"var(--t1)", marginBottom:6 }}>
              Good performance
            </div>
            <p style={{ color:"var(--t2)", fontSize:14 }}>
              Strong communication. SQL depth needs work — resources below.
            </p>
          </div>
        </div>

        {feedback.map((item, index) => (
          <Card 
            key={item.area}
            className="gl" 
            style={{ padding:20, marginBottom:12 }}
          >
            <div style={{ 
              display:"flex", 
              justifyContent:"space-between", 
              marginBottom:10 
            }}>
              <div style={{ fontWeight:600, fontSize:14, color:"var(--t1)" }}>
                {item.area}
              </div>
              <div style={{ 
                fontFamily:"'Fraunces',serif", 
                fontSize:26, 
                color:item.score >= 80 ? "var(--g)" : item.score >= 65 ? "var(--a)" : "var(--r)" 
              }}>
                {item.score}
              </div>
            </div>
            <ProgressBar 
              value={item.score} 
              color={
                item.score >= 80 ? "#10b981" : 
                item.score >= 65 ? "#f59e0b" : 
                "#f43f5e"
              }
            />
            <p style={{ 
              fontSize:13, 
              color:"var(--t2)", 
              marginTop:10, 
              lineHeight:1.65 
            }}>
              {item.comment}
            </p>

            {/* Resource link */}
            {item.resource && (
              <div style={{ 
                marginTop:12, 
                padding:"10px 14px", 
                background:"rgba(139,92,246,.07)", 
                border:"1px solid rgba(139,92,246,.18)", 
                borderRadius:"var(--rm)", 
                display:"flex", 
                alignItems:"center", 
                gap:10 
              }}>
                <Icon name="book" s={15} c="var(--p3)"/>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:12, color:"var(--t3)", marginBottom:2 }}>
                    You struggled with {item.weakness} — fix it here:
                  </div>
                  <div style={{ 
                    fontSize:13, 
                    fontWeight:600, 
                    color:"var(--p3)" 
                  }}>
                    {item.resource.name}
                  </div>
                </div>
                <Chip 
                  name={item.resource.tag} 
                  level="ok" 
                  style={{ fontSize:10 }} 
                />
                <Button size="small" style={{ fontSize:12 }}>
                  Open →
                </Button>
              </div>
            )}
          </Card>
        ))}

        <Card 
          className="gl" 
          style={{ 
            padding:20, 
            borderColor:"rgba(139,92,246,.2)" 
          }}
        >
          <div style={{ 
            fontWeight:600, 
            fontSize:14, 
            marginBottom:10, 
            color:"var(--t1)" 
          }}>
            AI Coaching Tip
          </div>
          <p style={{ 
            fontSize:13.5, 
            color:"var(--t2)", 
            lineHeight:1.7 
          }}>
            Your biggest opportunity is SQL window functions — this pattern appears in <strong style={{ color:"var(--t1)" }}>every</strong> DS technical interview. Spend 2 sessions on Mode Analytics' window function tutorial before your next mock.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default Interview;
