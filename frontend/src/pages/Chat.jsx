import React, { useState, useEffect, useRef } from 'react';
import { Topbar } from '../components/layout';
import { Button, Icon, Input, Chip } from '../components/ui';
import { auth } from '../config/firebase';

const Chat = ({ profile, analysisData, mobileMenuOpen, setMobileMenuOpen, onBack }) => {
  const [messages, setMessages] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  useEffect(() => {
    const fetchHistory = async () => {
      if (auth.currentUser) {
        setLoadingHistory(true);
        try {
          const token = await auth.currentUser.getIdToken();
          const analysis_id = analysisData?.analysis_id;
          let url = `${process.env.REACT_APP_API_URL}/api/chat/history`;
          if (analysis_id) url += `?analysis_id=${analysis_id}`;
          
          const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) {
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
              setMessages(data.messages.map(m => ({
                role: m.sender === "coach" ? "ai" : "user",
                text: m.message
              })));
            } else {
              setMessages([{ role: "ai", text: generateOpeningMsg() }]);
            }
          } else {
            setMessages([{ role: "ai", text: generateOpeningMsg() }]);
          }
        } catch (err) {
          console.error("Failed to load chat history:", err);
          setMessages([{ role: "ai", text: generateOpeningMsg() }]);
        } finally {
          setLoadingHistory(false);
        }
      } else {
        setMessages([{ role: "ai", text: generateOpeningMsg() }]);
      }
    };
    fetchHistory();
  }, [analysisData?.analysis_id]);

  const city = profile?.city || "Bengaluru";

  const timeline = profile?.timeline || "3–6 months";

  const blocker = profile?.blocker || "I don't know what skills I'm missing";

  const hours = profile?.hours || "7–15 hours";



  // Generate dynamic opening message based on real data

  const generateOpeningMsg = () => {

    const score = analysisData?.score || 0;

    const topGap = analysisData?.gaps?.[0]?.n || "skill gaps";

    const matchedSkills = analysisData?.matched?.length || 0;

    

    return `Hi! Based on your profile I know you're ${profile?.stage || "exploring opportunities"} in ${city} with a ${timeline} timeline, committing ${hours}/week. Your biggest focus right now: "${blocker}". You're at ${score}% readiness — your ${matchedSkills} matched skills are a strong foundation. The #1 gap is ${topGap}. Want a focused plan to close that gap this month?`;

  };



  const [inputValue, setInputValue] = useState("");

  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef();



  const sendMessage = async (text) => {

    const messageText = text || inputValue;

    if (!messageText.trim()) return;

    

    setMessages(prev => [...prev, { role: "user", text: messageText }]);

    setInputValue("");

    setIsTyping(true);

    

    try {

      // Get ID token if user is logged in
      const headers = { 'Content-Type': 'application/json' };
      if (auth.currentUser) {
        const token = await auth.currentUser.getIdToken();
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/chat`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: messageText,
          analysis_id: analysisData?.analysis_id, // Link to DB record

          context: {

            target_role: profile?.currentRole || "Data Scientist",

            match_score: analysisData?.match_score || 0,

            readiness_level: analysisData?.readiness_level || "Unknown",

            user_strengths: analysisData?.matched_skills || [],

            user_gaps: analysisData?.missing_required?.map(g => g.name || g.skill_name) || [],

            top_transferable: analysisData?.transferable_skills?.slice(0, 3)?.map(t => ({

              from: t.user_skill,

              to: t.maps_to_job_skill

            })) || [],

            city: city,

            timeline: timeline,

            hours: hours,

            blocker: blocker

          }

        })

      });



      if (!response.ok) {

        throw new Error('Failed to get AI response');

      }



      // Handle streaming response

      const reader = response.body.getReader();

      const decoder = new TextDecoder();

      let aiResponse = "";



      while (true) {

        const { done, value } = await reader.read();

        if (done) break;

        

        const chunk = decoder.decode(value);

        const lines = chunk.split('\n');

        

        for (const line of lines) {

          if (line.startsWith('data: ')) {

            const data = JSON.parse(line.slice(6));

            if (data.text === '[DONE]') {

              setIsTyping(false);

              return;

            }

            aiResponse += data.text;

            setMessages(prev => {

              const newMessages = [...prev];

              const lastMessage = newMessages[newMessages.length - 1];

              if (lastMessage && lastMessage.role === 'ai' && lastMessage.typing) {

                lastMessage.text = aiResponse;

              } else {

                newMessages.push({ role: "ai", text: aiResponse, typing: true });

              }

              return newMessages;

            });

          }

        }

      }

      

      // Finalize the message

      setMessages(prev => {

        const newMessages = [...prev];

        const lastMessage = newMessages[newMessages.length - 1];

        if (lastMessage && lastMessage.role === 'ai') {

          delete lastMessage.typing;

        }

        return newMessages;

      });

      

    } catch (error) {

      console.error('AI Chat Error:', error);

      // Fallback to a simple response if API fails

      setIsTyping(false);

      setMessages(prev => [...prev, { 

        role: "ai", 

        text: `I'm having trouble connecting right now. Based on your profile in ${city}, I'd recommend focusing on your top skill gap first. Would you like me to help you create a learning plan?` 

      }]);

    }

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

        onBack={onBack}

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

        mobileMenuOpen={mobileMenuOpen}

        setMobileMenuOpen={setMobileMenuOpen}

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

