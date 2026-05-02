import React from 'react';

const Chip = ({ name, level = "n", className = "", style = {} }) => {
  const levelStyles = {
    ok:   { bg:"rgba(16,185,129,.1)",  c:"#6ee7b7", b:"rgba(16,185,129,.2)" },
    bad:  { bg:"rgba(244,63,94,.1)",   c:"#fda4af", b:"rgba(244,63,94,.2)" },
    learn:{ bg:"rgba(245,158,11,.1)",  c:"#fcd34d", b:"rgba(245,158,11,.2)" },
    v:    { bg:"rgba(139,92,246,.12)", c:"#c4b5fd", b:"rgba(139,92,246,.25)" },
    n:    { bg:"rgba(255,255,255,.04)",c:"var(--t2)",b:"var(--gb)" },
  };

  const defaultStyle = levelStyles[level] || levelStyles.n;

  return (
    <span 
      className={className}
      style={{ 
        display:"inline-flex", 
        alignItems:"center", 
        padding:"4px 11px", 
        borderRadius:100, 
        fontSize:12, 
        fontWeight:500, 
        background:defaultStyle.bg, 
        color:defaultStyle.c, 
        border:`1px solid ${defaultStyle.b}`,
        ...style 
      }}
    >
      {name}
    </span>
  );
};

export default Chip;
