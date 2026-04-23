import React, { useState, useEffect, useRef } from 'react';
import { Topbar } from '../components/layout';
import { Button, Icon, Input, Chip } from '../components/ui';

const Chat = ({ profile, analysisData }) => {
  const city = profile?.city || "Bengaluru";
  const timeline = profile?.timeline || "3–6 months";
  const blocker = profile?.blocker || "I don't know what skills I'm missing";
  const hours = profile?.hours || "7–15 hours";

  const openingMsg = `Hi! Based on your profile I know you're ${profile?.stage || "a student"} in ${city} with a ${timeline} timeline, committing ${hours}/week. Your biggest focus right now: "${blocker}". You're at 72% readiness for Data Scientist — your Python and ML foundations are strong. The #1 gap is SQL — it appears in 89% of ${city} DS postings. Want a focused plan to close that gap this month?`;

  const [messages, setMessages] = useState([{ role: "ai", text: openingMsg }]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef();

  const contextualReplies = {
    apply: timeline === "Interview in the next month"
      ? `With your interview this month, I'd start applying immediately to 3–5 roles in parallel — don't wait until you feel "ready." Focus applications on companies in ${city} that list Python as the primary requirement, where SQL is listed as "nice to have" rather than required. Your 72% match is enough to get interviews at mid-stage startups.` 
      : `At 72%, you're close. Give it another 4 weeks on SQL, then apply actively. Mid-stage startups in ${city} are the right target — they value raw ability over credential stacking.`,
    learn: `Given you have ${hours}/week, here's your week: Mon/Wed/Fri — 45min SQL on Mode Analytics. Tue/Thu — 1 LeetCode SQL problem. Weekend — 1 small feature engineering project in Python. This pace closes your top gap in 3 weeks.`,
    gap: `Your SQL gap is the one that pays back most immediately — 89% of ${city} DS postings require it. After SQL, Feature Engineering unlocks most of the remaining job postings. Your Python background means you can move through both faster than a newcomer.`,
  };

  const defaultReply = `Based on what I know about your situation — ${timeline} timeline, ${hours}/week in ${city} — here's my honest take: focus on SQL for 3 weeks, then start applying. Your transferable skills from ${profile?.currentRole || "your background"} are being undersold. Let's work on that framing next.`;

  const sendMessage = (text) => {
    const messageText = text || inputValue;
    if (!messageText.trim()) return;
    
    setMessages(prev => [...prev, { role: "user", text: messageText }]);
    setInputValue("");
    setIsTyping(true);
    
    setTimeout(() => {
      setIsTyping(false);
      const lowerText = messageText.toLowerCase();
      const reply = lowerText.includes("apply") ? contextualReplies.apply
        : lowerText.includes("learn") || lowerText.includes("study") ? contextualReplies.learn
        : lowerText.includes("gap") || lowerText.includes("missing") ? contextualReplies.gap
        : defaultReply;
      setMessages(prev => [...prev, { role: "ai", text: reply }]);
    }, 1900);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const promptSuggestions = [
    "What should I focus on this week?",
    "Am I ready to apply now?",
    "How do I explain my gap?",
    `Best companies in ${city} for me?`,
  ];

  return (
    <div className="main" style={{ display:"flex", flexDirection:"column", height:"100vh" }}>
      <Topbar 
        title="Career Coach AI" 
        sub={`Personalized for your ${city} · ${timeline} context`}
        right={
          <div style={{ 
            display:"flex", 
            alignItems:"center", 
            gap:6, 
            padding:"5px 12px", 
            background:"rgba(16,185,129,.08)", 
            borderRadius:100, 
            border:"1px solid rgba(16,185,129,.2)" 
          }}>
            <div style={{ 
              width:6, 
              height:6, 
              borderRadius:"50%", 
              background:"var(--g)", 
              animation:"pulse 2s infinite" 
            }}/>
            <span style={{ fontSize:12, color:"#6ee7b7", fontWeight:500 }}>
              Connected to your profile
            </span>
          </div>
        }
      />
      
      <div style={{ flex:1, overflowY:"auto", padding:"24px 28px" }}>
        <div style={{ maxWidth:680, margin:"0 auto" }}>
          {messages.map((message, index) => (
            <div 
              key={index} 
              style={{ 
                marginBottom:20, 
                display:"flex", 
                flexDirection:"column", 
                alignItems:message.role === "user" ? "flex-end" : "flex-start", 
                animation:"fadeUp .3s both" 
              }}
            >
              {message.role === "ai" && (
                <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
                  <div style={{ 
                    width:26, 
                    height:26, 
                    borderRadius:8, 
                    background:"linear-gradient(135deg,var(--p2),var(--i))", 
                    display:"flex", 
                    alignItems:"center", 
                    justifyContent:"center" 
                  }}>
                    <Icon name="brain" s={13} c="white"/>
                  </div>
                  <span style={{ fontSize:12, fontWeight:600, color:"var(--t3)" }}>
                    Bridgr AI
                  </span>
                </div>
              )}
              <div className={message.role === "user" ? "cu" : "cai"}>
                {message.text}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div style={{ display:"flex", alignItems:"flex-start", gap:8, marginBottom:20 }}>
              <div style={{ 
                width:26, 
                height:26, 
                borderRadius:8, 
                background:"linear-gradient(135deg,var(--p2),var(--i))", 
                display:"flex", 
                alignItems:"center", 
                justifyContent:"center" 
              }}>
                <Icon name="brain" s={13} c="white"/>
              </div>
              <div className="cai" style={{ display:"flex", gap:5, alignItems:"center" }}>
                {[0, 0.2, 0.4].map(delay => (
                  <div 
                    key={delay} 
                    style={{ 
                      width:6, 
                      height:6, 
                      borderRadius:"50%", 
                      background:"var(--t3)", 
                      animation:`blk 1.2s ${delay}s infinite` 
                    }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef}/>
        </div>
      </div>
      
      <div style={{ padding:"0 28px 12px" }}>
        <div style={{ maxWidth:680, margin:"0 auto", display:"flex", gap:7, flexWrap:"wrap" }}>
          {promptSuggestions.map(prompt => (
            <Chip 
              key={prompt}
              name={prompt}
              className="tv"
              style={{ cursor:"none", fontSize:12.5, padding:"6px 12px" }}
              onClick={() => sendMessage(prompt)}
            />
          ))}
        </div>
      </div>
      
      <div style={{ 
        padding:"12px 28px 24px", 
        borderTop:"1px solid var(--gb)", 
        background:"rgba(0,0,5,.5)", 
        backdropFilter:"blur(20px)" 
      }}>
        <div style={{ maxWidth:680, margin:"0 auto", display:"flex", gap:10 }}>
          <Button variant="secondary" style={{ padding:"11px" }}>
            <Icon name="mic" s={17}/>
          </Button>
          <Input 
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendMessage()}
            placeholder="Ask anything about your career…"
            style={{ flex:1 }}
          />
          <Button style={{ padding:"11px 16px" }} onClick={() => sendMessage()}>
            <Icon name="send" s={16} c="white"/>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
