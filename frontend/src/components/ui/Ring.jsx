import React, { useState, useEffect } from 'react';

const Ring = ({ score, size = 100, color = "#8b5cf6", label = "" }) => {
  const [displayed, setDisplayed] = useState(0);
  
  useEffect(() => {
    const timer = setTimeout(() => setDisplayed(score), 80);
    return () => clearTimeout(timer);
  }, [score]);
  
  const radius = size / 2 - 9;
  const circumference = 2 * Math.PI * radius;
  const dash = circumference * displayed / 100;
  
  return (
    <div style={{ 
      position: "relative", 
      width: size, 
      height: size, 
      display: "inline-flex", 
      alignItems: "center", 
      justifyContent: "center" 
    }}>
      <svg 
        width={size} 
        height={size} 
        style={{ 
          position: "absolute", 
          transform: "rotate(-90deg)" 
        }}
      >
        <circle 
          cx={size/2} 
          cy={size/2} 
          r={radius} 
          fill="none" 
          stroke="rgba(255,255,255,.06)" 
          strokeWidth="7"
        />
        <circle 
          cx={size/2} 
          cy={size/2} 
          r={radius} 
          fill="none" 
          stroke={color} 
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circumference}`}
          style={{ 
            filter:`drop-shadow(0 0 8px ${color}90)`, 
            transition: "stroke-dasharray 1.1s cubic-bezier(.4,0,.2,1)" 
          }}
        />
      </svg>
      <div style={{ textAlign: "center", zIndex: 1 }}>
        <div style={{ 
          fontSize: size * .22, 
          fontWeight: 600, 
          color: "#f0f0fc", 
          lineHeight: 1, 
          fontFamily: "'Fraunces',serif" 
        }}>
          {displayed}
        </div>
        {label && (
          <div style={{ 
            fontSize: size * .10, 
            color: "var(--t3)", 
            marginTop: 3 
          }}>
            {label}
          </div>
        )}
      </div>
    </div>
  );
};

export default Ring;
