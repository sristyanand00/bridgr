import React from 'react';
import { Icon } from '../ui';

const Topbar = ({ title, sub, right, mobileMenuOpen, setMobileMenuOpen }) => (
  <div className="topbar">
    <div style={{ display:"flex", alignItems:"center", gap:10 }}>
      {/* Hamburger menu for mobile */}
      <button 
        className="btn bgl bsm mobile-menu-btn" 
        style={{ padding:"8px", display:"none" }}
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
      >
        <Icon name="menu" s={16}/>
      </button>
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
