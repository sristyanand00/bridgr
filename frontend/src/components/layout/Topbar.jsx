import React from 'react';
import { Icon } from '../ui';

const Topbar = ({ title, sub, right }) => (
  <div className="topbar">
    <div>
      <div style={{ 
        fontFamily:"'Fraunces',serif", 
        fontWeight:300, 
        fontSize:17, 
        letterSpacing:"-.02em", 
        color:"var(--t1)" 
      }}>
        {title}
      </div>
      {sub && (
        <div style={{ fontSize:11.5, color:"var(--t3)", marginTop:1 }}>
          {sub}
        </div>
      )}
    </div>
    <div style={{ display:"flex", alignItems:"center", gap:10 }}>
      {right}
      <button className="btn bgl bsm" style={{ padding:"8px" }}>
        <Icon name="bell" s={16}/>
      </button>
    </div>
  </div>
);

export default Topbar;
