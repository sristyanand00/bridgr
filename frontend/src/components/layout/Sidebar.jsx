import React from 'react';
import { Button, Icon, Chip } from '../ui';
import { NAVIGATION_ITEMS, BOTTOM_NAV_ITEMS } from '../../constants/navigation';

const Sidebar = ({ currentPage, setCurrentPage, user }) => {
  return (
    <div className="sidebar">
      <div style={{ padding:"4px 12px 24px", display:"flex", alignItems:"center", gap:10 }}>
        <div style={{ 
          width:30, 
          height:30, 
          borderRadius:9, 
          background:"linear-gradient(135deg,var(--p2),var(--i))", 
          display:"flex", 
          alignItems:"center", 
          justifyContent:"center", 
          boxShadow:"0 0 20px rgba(139,92,246,.4)" 
        }}>
          <Icon name="brain" s={15} c="white" />
        </div>
        <span style={{ 
          fontFamily:"'Fraunces',serif", 
          fontWeight:300, 
          fontSize:17, 
          letterSpacing:"-.02em", 
          color:"var(--t1)" 
        }}>
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
          <span className="ni-icon">
            <Icon name={item.i} s={16} />
          </span>
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

      <div style={{ margin:"12px 0 0", padding:"10px 12px", borderRadius:"var(--rs)", background:"var(--gl)", border:"1px solid var(--gb)", display:"flex", alignItems:"center", gap:10 }}>
        <div style={{ 
          width:28, 
          height:28, 
          borderRadius:"50%", 
          background:"linear-gradient(135deg,var(--p2),var(--i))", 
          display:"flex", 
          alignItems:"center", 
          justifyContent:"center", 
          fontSize:12, 
          fontWeight:600, 
          color:"white", 
          flexShrink:0 
        }}>
          {user?.avatar || "A"}
        </div>
        <div>
          <div style={{ fontSize:12.5, fontWeight:600, color:"var(--t1)", lineHeight:1.2 }}>
            {user?.name || "Ananya S."}
          </div>
          <div style={{ fontSize:11, color:"var(--t3)" }}>
            Free Plan
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
