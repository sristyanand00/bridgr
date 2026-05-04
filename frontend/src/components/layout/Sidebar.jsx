import React from 'react';
import { Button, Icon, Chip } from '../ui';
import { NAVIGATION_ITEMS, BOTTOM_NAV_ITEMS } from '../../constants/navigation';

const Sidebar = ({ currentPage, setCurrentPage, user, mobileMenuOpen, setMobileMenuOpen, onSignOut, onSignIn }) => {
  return (
    <div className={`sidebar ${mobileMenuOpen ? 'open' : ''}`}>
      <div style={{ padding:"4px 12px 24px", display:"flex", alignItems:"center", gap:10 }}>
        <img 
          src="/bridgr-logo.svg" 
          alt="Bridgr logo" 
          style={{ width:30, height:30, objectFit:"contain", borderRadius:6 }}
        />
        <span style={{ fontFamily:"'Fraunces',serif", fontWeight:300, fontSize:17, letterSpacing:"-.02em", color:"var(--t1)" }}>
          Bridgr
        </span>
      </div>

      <div className="lbl" style={{ padding:"0 12px 8px" }}>Platform</div>
      {NAVIGATION_ITEMS.map(item => (
        <div 
          key={item.id} 
          className={`ni ${currentPage === item.id ? "active" : ""}`} 
          onClick={() => setCurrentPage(item.id)}
        >
          <span className="ni-icon"><Icon name={item.i} s={16} /></span>
          {item.l}
        </div>
      ))}

      <div style={{ flex:1 }} />
      <div className="dv" style={{ margin:"12px 0" }} />
      {BOTTOM_NAV_ITEMS.map(item => (
        <div 
          key={item.id} 
          className={`ni ${currentPage === item.id ? "active" : ""}`} 
          onClick={() => setCurrentPage(item.id)} 
          style={item.accent ? { color:"var(--p3)" } : {}}
        >
          <Icon name={item.i} s={16}/>
          {item.l}
          {item.accent && <Chip name="PRO" style={{ marginLeft:"auto", fontSize:10, padding:"2px 6px" }} />}
        </div>
      ))}

      {/* User Card */}
      <div style={{ margin:"12px 0 0", padding:"10px 12px", borderRadius:"var(--rs)", background:"var(--gl)", border:"1px solid var(--gb)" }}>
        {/* User info row */}
        <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:10 }}>
          <div style={{ 
            width:28, height:28, borderRadius:"50%", 
            background: user?.authenticated 
              ? "linear-gradient(135deg,var(--p2),var(--i))" 
              : "rgba(255,255,255,0.08)",
            display:"flex", alignItems:"center", justifyContent:"center", 
            fontSize:12, fontWeight:600, color:"white", flexShrink:0 
          }}>
            {user?.authenticated 
              ? (user?.avatar || "U") 
              : <Icon name="user" s={14} c="var(--t3)" />
            }
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontSize:12.5, fontWeight:600, color:"var(--t1)", lineHeight:1.2, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
              {user?.authenticated ? (user?.name || "User") : "Guest"}
            </div>
            <div style={{ fontSize:11, color:"var(--t3)" }}>
              {user?.authenticated ? (user?.email || "Free Plan") : "Not signed in"}
            </div>
          </div>
          {user?.authenticated && (
            <Icon name="shield" s={13} c="var(--p3)" />
          )}
        </div>

        {/* Sign in / Sign out button */}
        {user?.authenticated ? (
          <button
            onClick={onSignOut}
            style={{
              width:"100%", display:"flex", alignItems:"center", justifyContent:"center", gap:6,
              padding:"6px 10px", background:"rgba(239,68,68,0.08)", border:"1px solid rgba(239,68,68,0.15)",
              borderRadius:"var(--rm)", color:"rgba(239,68,68,0.7)", fontSize:12,
              cursor:"pointer", fontFamily:"'Geist',sans-serif", transition:"all 0.2s",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = "rgba(239,68,68,0.15)"; e.currentTarget.style.color = "rgba(239,68,68,1)"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "rgba(239,68,68,0.08)"; e.currentTarget.style.color = "rgba(239,68,68,0.7)"; }}
          >
            <Icon name="logout" s={12} c="currentColor" />
            Sign out
          </button>
        ) : (
          <button
            onClick={onSignIn}
            style={{
              width:"100%", display:"flex", alignItems:"center", justifyContent:"center", gap:6,
              padding:"6px 10px",
              background:"linear-gradient(135deg,rgba(139,92,246,.15),rgba(99,102,241,.15))",
              border:"1px solid rgba(139,92,246,.25)", borderRadius:"var(--rm)",
              color:"var(--p3)", fontSize:12, cursor:"pointer",
              fontFamily:"'Geist',sans-serif", transition:"all 0.2s",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = "linear-gradient(135deg,rgba(139,92,246,.25),rgba(99,102,241,.25))"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "linear-gradient(135deg,rgba(139,92,246,.15),rgba(99,102,241,.15))"; }}
          >
            <Icon name="user" s={12} c="currentColor" />
            Sign in to save progress
          </button>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
