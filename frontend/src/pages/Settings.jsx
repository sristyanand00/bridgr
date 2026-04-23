import React, { useState } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Icon, Input, Chip } from '../components/ui';

const Settings = ({ profile }) => {
  const [notifications, setNotifications] = useState({ 
    daily: true, 
    weekly: true, 
    tips: false, 
    checkin: true 
  });

  const notificationSettings = [
    { 
      key: "daily", 
      label: "Daily action reminders", 
      description: "Study nudge at 9am" 
    },
    { 
      key: "checkin", 
      label: "Check-in reminder", 
      description: "Re-analyze reminder every 2 weeks" 
    },
    { 
      key: "weekly", 
      label: "Weekly progress report", 
      description: "Career progress every Monday" 
    },
    { 
      key: "tips", 
      label: "Market tips & insights", 
      description: "New hiring trends and skill alerts" 
    },
  ];

  const toggleNotification = (key) => {
    setNotifications(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const hourOptions = ["< 3h", "3–7h", "7–15h", "15h+"];
  const currentHours = profile?.hours || "7–15 hours";

  return (
    <div className="main">
      <Topbar title="Settings"/>
      <div className="page" style={{ maxWidth:620, margin:"0 auto" }}>
        {/* Profile Section */}
        <Card className="gl" style={{ padding:24, marginBottom:12 }}>
          <div style={{ fontSize:14, fontWeight:600, marginBottom:18, color:"var(--t1)" }}>
            Profile
          </div>
          
          <div style={{ 
            display:"flex", 
            alignItems:"center", 
            gap:16, 
            marginBottom:20 
          }}>
            <div style={{ 
              width:56, 
              height:56, 
              borderRadius:"50%", 
              background:"linear-gradient(135deg,var(--p2),var(--i))", 
              display:"flex", 
              alignItems:"center", 
              justifyContent:"center", 
              fontSize:20, 
              fontWeight:700, 
              color:"white", 
              boxShadow:"0 0 20px rgba(139,92,246,.35)" 
            }}>
              A
            </div>
            <div>
              <div style={{ 
                fontWeight:600, 
                fontSize:16, 
                color:"var(--t1)", 
                lineHeight:1.2 
              }}>
                {profile?.name || "Ananya Sharma"}
              </div>
              <div style={{ color:"var(--t3)", fontSize:13 }}>
                {profile?.email || "ananya@gmail.com"}
              </div>
              <div style={{ 
                fontSize:12, 
                color:"var(--g)", 
                marginTop:3 
              }}>
                Signed in with Google
              </div>
            </div>
            <Button size="small" style={{ marginLeft:"auto" }}>
              Edit
            </Button>
          </div>

          <div className="b2" style={{ gap:10 }}>
            {[
              ["Current Role", profile?.currentRole || "CS Student"],
              ["Target Role", "Data Scientist"],
              ["City", profile?.city || "Bengaluru"],
              ["Timeline", profile?.timeline || "3–6 months"]
            ].map(([label, value]) => (
              <div key={label}>
                <div style={{ fontSize:12, color:"var(--t3)", marginBottom:6 }}>
                  {label}
                </div>
                <Input defaultValue={value} />
              </div>
            ))}
          </div>

          <div style={{ marginTop:12 }}>
            <div style={{ fontSize:12, color:"var(--t3)", marginBottom:6 }}>
              Hours/week commitment
            </div>
            <div style={{ display:"flex", gap:8 }}>
              {hourOptions.map((hours, index) => (
                <Chip
                  key={hours}
                  name={hours}
                  className={currentHours.includes(
                    ["3", "3–", "7–", "15+"][index]
                  ) ? "sel" : ""}
                  style={{ fontSize:12 }}
                />
              ))}
            </div>
          </div>
        </Card>

        {/* Notifications Section */}
        <Card className="gl" style={{ padding:24, marginBottom:12 }}>
          <div style={{ fontSize:14, fontWeight:600, marginBottom:18, color:"var(--t1)" }}>
            Notifications
          </div>
          
          {notificationSettings.map((setting, index) => (
            <div 
              key={setting.key}
              style={{ 
                display:"flex", 
                justifyContent:"space-between", 
                alignItems:"center", 
                padding:"12px 0", 
                borderBottom:index < notificationSettings.length - 1 ? 
                  "1px solid var(--gb)" : "none" 
              }}
            >
              <div>
                <div style={{ 
                  fontSize:13.5, 
                  fontWeight:500, 
                  color:"var(--t1)" 
                }}>
                  {setting.label}
                </div>
                <div style={{ fontSize:12, color:"var(--t3)" }}>
                  {setting.description}
                </div>
              </div>
              
              <div 
                onClick={() => toggleNotification(setting.key)}
                style={{ 
                  width:44, 
                  height:24, 
                  borderRadius:12, 
                  background:notifications[setting.key] ? 
                    "var(--p)" : 
                    "rgba(255,255,255,.08)", 
                  position:"relative", 
                  cursor:"none", 
                  transition:"background .25s", 
                  boxShadow:notifications[setting.key] ? 
                    "0 0 12px rgba(139,92,246,.4)" : "none", 
                  flexShrink:0 
                }}
              >
                <div style={{ 
                  width:18, 
                  height:18, 
                  borderRadius:"50%", 
                  background:"white", 
                  position:"absolute", 
                  top:3, 
                  left:notifications[setting.key] ? 23 : 3, 
                  transition:"left .25s var(--spring)" 
                }}/>
              </div>
            </div>
          ))}
        </Card>

        {/* Action Buttons */}
        <div style={{ 
          display:"flex", 
          justifyContent:"space-between", 
          alignItems:"center" 
        }}>
          <div style={{ display:"flex", gap:10 }}>
            <Button size="small" variant="secondary">
              Export Data
            </Button>
            <Button 
              size="small" 
              variant="secondary"
              style={{ 
                color:"var(--r)", 
                borderColor:"rgba(244,63,94,.2)" 
              }}
            >
              Delete Account
            </Button>
          </div>
          <Button>
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
