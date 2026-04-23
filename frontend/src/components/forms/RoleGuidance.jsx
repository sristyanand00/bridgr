import React, { useState } from 'react';
import { Button, Icon } from '../ui';

const RoleGuidance = ({ onSelect }) => {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});

  const questions = [
    { 
      id: "enjoy", 
      q: "What do you enjoy most?", 
      opts: ["Building & coding systems", "Finding patterns in data", "Understanding users & strategy", "Optimizing infrastructure & scale"] 
    },
    { 
      id: "strength", 
      q: "What's your natural strength?", 
      opts: ["Algorithmic thinking", "Statistical reasoning", "Communication & storytelling", "Systems architecture"] 
    },
    { 
      id: "work", 
      q: "What kind of work excites you?", 
      opts: ["Shipping product features", "Running experiments & models", "Talking to users & making decisions", "Making systems faster & reliable"] 
    },
  ];

  const roleMapping = {
    "Building & coding systems-Algorithmic thinking-Shipping product features": "Software Engineer",
    "Finding patterns in data-Statistical reasoning-Running experiments & models": "Data Scientist",
    "Understanding users & strategy-Communication & storytelling-Talking to users & making decisions": "Product Manager",
    "Optimizing infrastructure & scale-Systems architecture-Making systems faster & reliable": "DevOps / Cloud Engineer",
  };

  const suggestRole = () => {
    const key = `${answers.enjoy}-${answers.strength}-${answers.work}`;
    const suggested = roleMapping[key] || "Data Scientist";
    onSelect(suggested);
  };

  const currentQuestion = questions[step];
  const selectedAnswer = answers[currentQuestion.id];

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center", 
      padding: 24, 
      position: "relative", 
      zIndex: 1 
    }}>
      <div style={{ maxWidth: 480, width: "100%" }}>
        <Button 
          variant="secondary" 
          size="small" 
          style={{ marginBottom: 24 }} 
          onClick={() => onSelect(null)}
        >
          ← Back
        </Button>
        
        <div className="tag tv" style={{ marginBottom: 16, display: "inline-flex" }}>
          <Icon name="sparkle" s={12} c="var(--p3)" /> Role Finder
        </div>
        
        <h2 style={{ 
          fontFamily: "'Fraunces',serif", 
          fontWeight: 300, 
          fontSize: 28, 
          letterSpacing: "-.02em", 
          marginBottom: 8, 
          color: "var(--t1)" 
        }}>
          Let's find the right role for you
        </h2>
        
        <p style={{ 
          fontSize: 14, 
          color: "var(--t3)", 
          marginBottom: 28, 
          lineHeight: 1.6 
        }}>
          3 quick questions — no right answer, just your honest first instinct.
        </p>

        <div className="step-bar" style={{ marginBottom: 24 }}>
          {questions.map((_, index) => (
            <div 
              key={index} 
              className={`step-seg ${
                index < step ? "done" : 
                index === step ? "active" : ""
              }`} 
            />
          ))}
        </div>

        <div className="afu" key={step}>
          <p style={{ 
            fontSize: 16, 
            fontWeight: 500, 
            color: "var(--t1)", 
            marginBottom: 16 
          }}>
            {currentQuestion.q}
          </p>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {currentQuestion.opts.map(option => (
              <button 
                key={option} 
                className={`q-opt ${selectedAnswer === option ? "sel" : ""}`} 
                onClick={() => setAnswers(prev => ({ ...prev, [currentQuestion.id]: option }))}
              >
                <div className={`q-dot ${selectedAnswer === option ? "filled" : ""}`}>
                  {selectedAnswer === option && <Icon name="check" s={9} c="white" />}
                </div>
                {option}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 24 }}>
          {step < questions.length - 1 ? (
            <Button 
              onClick={() => setStep(prev => prev + 1)} 
              disabled={!selectedAnswer}
            >
              Next
            </Button>
          ) : (
            <Button 
              onClick={suggestRole} 
              disabled={!selectedAnswer}
            >
              Find my role →
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoleGuidance;
