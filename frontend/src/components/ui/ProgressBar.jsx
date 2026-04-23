import React from 'react';

const ProgressBar = ({ value, color }) => (
  <div className="pt">
    <div 
      className="pf" 
      style={{ 
        width: `${value}%`, 
        background: color || "linear-gradient(90deg,var(--p),var(--f))" 
      }} 
    />
  </div>
);

export default ProgressBar;
