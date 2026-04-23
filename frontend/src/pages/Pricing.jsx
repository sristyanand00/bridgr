import React from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Icon } from '../components/ui';

const Pricing = () => {
  const plans = [
    {
      name: "Free",
      price: "₹0",
      period: "/mo",
      description: "Get started, no card needed.",
      features: [
        "1 resume analysis/month",
        "Basic skill gap view", 
        "3 AI chat messages/day",
        "Market Pulse (limited)",
        "Community access"
      ],
      cta: "Current Plan",
      featured: false,
      disabled: true
    },
    {
      name: "Pro",
      price: "₹499",
      period: "/mo",
      description: "Everything to land your next role.",
      features: [
        "Unlimited resume analyses",
        "Full gap analysis + roadmap",
        "Unlimited AI coaching",
        "Mock interviews (10/mo)",
        "Real-time Market Pulse",
        "Resume improvement AI",
        "Progress tracking"
      ],
      cta: "Upgrade to Pro",
      featured: true,
      badge: "Most Popular",
      disabled: false
    },
    {
      name: "Turbo",
      price: "₹1,199",
      period: "/mo",
      description: "For serious career transitions.",
      features: [
        "Everything in Pro",
        "Unlimited mock interviews",
        "1:1 mentor session/month",
        "LinkedIn profile review",
        "Referral network access",
        "Interview guarantee*"
      ],
      cta: "Get Turbo",
      featured: false,
      disabled: false
    },
  ];

  return (
    <div className="main">
      <Topbar title="Upgrade Plan"/>
      <div className="page" style={{ maxWidth:840, margin:"0 auto" }}>
        <div style={{ textAlign:"center", marginBottom:48 }}>
          <h1 className="serif" style={{ fontSize:44, marginBottom:12, color:"var(--t1)" }}>
            Invest in your career
          </h1>
          <p style={{ color:"var(--t2)", fontSize:16 }}>
            One offer letter pays for 3 years of Pro. Most users see results in 30 days.
          </p>
        </div>

        <div className="b3" style={{ alignItems:"start" }}>
          {plans.map(plan => (
            <Card 
              key={plan.name}
              className={`pc ${plan.featured ? "feat" : ""}`}
            >
              {plan.badge && (
                <div style={{ 
                  position:"absolute", 
                  top:-11, 
                  left:"50%", 
                  transform:"translateX(-50%)", 
                  background:"linear-gradient(135deg,var(--p2),var(--i))", 
                  color:"white", 
                  fontSize:11, 
                  fontWeight:700, 
                  padding:"3px 14px", 
                  borderRadius:100, 
                  whiteSpace:"nowrap" 
                }}>
                  {plan.badge}
                </div>
              )}
              
              <div style={{ fontSize:13, fontWeight:600, color:"var(--t3)", marginBottom:8 }}>
                {plan.name}
              </div>
              
              <div style={{ display:"flex", alignItems:"baseline", gap:4 }}>
                <span style={{ 
                  fontFamily:"'Fraunces',serif", 
                  fontSize:42, 
                  fontWeight:300, 
                  color:"var(--t1)" 
                }}>
                  {plan.price}
                </span>
                <span style={{ fontSize:13.5, color:"var(--t3)" }}>
                  {plan.period}
                </span>
              </div>
              
              <p style={{ fontSize:13, color:"var(--t3)", margin:"8px 0 18px" }}>
                {plan.description}
              </p>
              
              <div className="dv" style={{ marginBottom:18 }}/>
              
              <div style={{ marginBottom:22 }}>
                {plan.features.map(feature => (
                  <div key={feature} style={{ 
                    display:"flex", 
                    gap:9, 
                    alignItems:"flex-start", 
                    marginBottom:9 
                  }}>
                    <div style={{ 
                      width:15, 
                      height:15, 
                      borderRadius:"50%", 
                      background:plan.featured ? 
                        "rgba(139,92,246,.15)" : 
                        "rgba(255,255,255,.06)", 
                      display:"flex", 
                      alignItems:"center", 
                      justifyContent:"center", 
                      flexShrink:0, 
                      marginTop:2 
                    }}>
                      <Icon 
                        name="check" 
                        s={8} 
                        c={plan.featured ? "var(--p3)" : "var(--g)"} 
                      />
                    </div>
                    <span style={{ fontSize:13, color:"var(--t2)" }}>
                      {feature}
                    </span>
                  </div>
                ))}
              </div>
              
              <Button 
                className={plan.featured ? "" : "bgl"}
                style={{ 
                  width:"100%", 
                  justifyContent:"center", 
                  fontSize:14, 
                  padding:13, 
                  opacity:plan.disabled ? 0.6 : 1 
                }}
                disabled={plan.disabled}
              >
                {plan.featured ? plan.cta : plan.cta}
              </Button>
            </Card>
          ))}
        </div>

        <p style={{ 
          textAlign:"center", 
          fontSize:12, 
          color:"var(--t3)", 
          marginTop:20 
        }}>
          *Interview guarantee: 3 interview invitations within 60 days or full refund.
        </p>
      </div>
    </div>
  );
};

export default Pricing;
