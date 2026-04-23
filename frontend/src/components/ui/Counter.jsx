import React, { useState, useEffect, useRef } from 'react';

const Counter = ({ to, suffix = "" }) => {
  const [value, setValue] = useState(0);
  const hasRun = useRef(false);
  
  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;
    
    let start = 0;
    const step = to / (1400 / 16);
    const timer = setInterval(() => {
      start = Math.min(start + step, to);
      setValue(Math.round(start));
      if (start >= to) clearInterval(timer);
    }, 16);
    
    return () => clearInterval(timer);
  }, [to]);
  
  return <>{value}{suffix}</>;
};

export default Counter;
