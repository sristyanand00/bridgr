import React, { useState } from 'react';
import { Button, Icon, Input } from '../ui';
import { QUIZ_QUESTIONS } from '../../constants/quiz';

const QuizOption = ({ option, isSelected, onClick }) => (
  <button 
    className={`q-opt ${isSelected ? "sel" : ""}`} 
    onClick={() => onClick(option)}
  >
    <div className={`q-dot ${isSelected ? "filled" : ""}`}>
      {isSelected && <Icon name="check" s={9} c="white" />}
    </div>
    {option}
  </button>
);

const Quiz = ({ onComplete }) => {
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [textValue, setTextValue] = useState("");
  const [animationKey, setAnimationKey] = useState(0);

  const currentQuestion = QUIZ_QUESTIONS[questionIndex];
  const selectedAnswer = answers[currentQuestion.id];
  const totalQuestions = QUIZ_QUESTIONS.length;

  const selectOption = (option) => {
    setAnswers(prev => ({ ...prev, [currentQuestion.id]: option }));
  };

  const handleNext = () => {
    const finalAnswers = { ...answers };
    if (currentQuestion.freeText) {
      finalAnswers[currentQuestion.id] = textValue;
    }
    
    if (questionIndex < totalQuestions - 1) {
      setQuestionIndex(prev => prev + 1);
      setAnimationKey(prev => prev + 1);
    } else {
      onComplete(finalAnswers);
    }
  };

  const skipQuestion = () => {
    if (questionIndex < totalQuestions - 1) {
      setQuestionIndex(prev => prev + 1);
      setAnimationKey(prev => prev + 1);
    } else {
      onComplete(answers);
    }
  };

  const canProceed = currentQuestion.freeText ? true : !!selectedAnswer;

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center", 
      padding: "24px", 
      position: "relative", 
      zIndex: 1 
    }}>
      <div style={{ width: "100%", maxWidth: 520 }}>
        {/* Logo */}
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: 10, 
          marginBottom: 48, 
          justifyContent: "center" 
        }}>
          <div style={{ 
            width: 32, 
            height: 32, 
            borderRadius: 9, 
            background: "linear-gradient(135deg,var(--p2),var(--i))", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center", 
            boxShadow: "0 0 24px rgba(139,92,246,.5)" 
          }}>
            <Icon name="brain" s={16} c="white" />
          </div>
          <span style={{ 
            fontFamily: "'Fraunces',serif", 
            fontWeight: 300, 
            fontSize: 18, 
            letterSpacing: "-.02em" 
          }}>
            Bridgr
          </span>
        </div>

        {/* Step bar */}
        <div className="step-bar">
          {QUIZ_QUESTIONS.map((_, index) => (
            <div 
              key={index} 
              className={`step-seg ${
                index < questionIndex ? "done" : 
                index === questionIndex ? "active" : ""
              }`} 
            />
          ))}
        </div>

        {/* Question */}
        <div key={animationKey} className="afu">
          <div style={{ marginBottom: 6 }}>
            <span style={{ 
              fontSize: 11.5, 
              color: "var(--t3)", 
              fontWeight: 500 
            }}>
              {questionIndex + 1} of {totalQuestions}
              {currentQuestion.optional ? " · Optional" : ""}
            </span>
          </div>
          <h2 style={{ 
            fontFamily: "'Fraunces',serif", 
            fontWeight: 300, 
            fontSize: "clamp(22px,4vw,30px)", 
            letterSpacing: "-.02em", 
            marginBottom: 8, 
            color: "var(--t1)", 
            lineHeight: 1.2 
          }}>
            {currentQuestion.q}
          </h2>
          <p style={{ 
            fontSize: 14, 
            color: "var(--t3)", 
            marginBottom: 28, 
            lineHeight: 1.55 
          }}>
            {currentQuestion.sub}
          </p>

          {currentQuestion.freeText ? (
            <Input 
              value={textValue} 
              onChange={e => setTextValue(e.target.value)}
              placeholder={currentQuestion.placeholder} 
              style={{ marginBottom: 20 }} 
            />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {currentQuestion.opts.map(option => (
                <QuizOption
                  key={option}
                  option={option}
                  isSelected={selectedAnswer === option}
                  onClick={selectOption}
                />
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          marginTop: 28 
        }}>
          {currentQuestion.optional ? (
            <Button variant="secondary" size="small" onClick={skipQuestion}>
              Skip for now
            </Button>
          ) : (
            <div />
          )}
          <Button 
            onClick={handleNext} 
            disabled={!canProceed}
            icon="arr"
            iconPosition="right"
          >
            {questionIndex < totalQuestions - 1 ? "Continue" : "Let's go"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Quiz;
