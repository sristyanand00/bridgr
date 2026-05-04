import React from 'react';
import { Icon } from '../ui';

const Topbar = ({ title, sub, right, onBack, mobileMenuOpen, setMobileMenuOpen }) => (
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

      {/* Back button — shown when onBack is provided */}
      {onBack && (
        <button
          onClick={onBack}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            background: "rgba(255,255,255,0.05)",
            border: "1px solid var(--gb)",
            borderRadius: "var(--rm)",
            color: "var(--t2)",
            fontSize: 13,
            padding: "6px 12px",
            cursor: "pointer",
            transition: "all 0.2s",
            fontFamily: "'Geist', sans-serif",
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = "rgba(255,255,255,0.1)";
            e.currentTarget.style.color = "var(--t1)";
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = "rgba(255,255,255,0.05)";
            e.currentTarget.style.color = "var(--t2)";
          }}
        >
          <Icon name="back" s={14}/>
          Back
        </button>
      )}

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
