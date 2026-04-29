import React from 'react';

const FeaturesSection = () => {
  const features = [
    {
      icon: "📄",
      title: "Resume Analysis",
      description: "AI-powered resume scoring and skill gap analysis to optimize your career profile"
    },
    {
      icon: "🤖",
      title: "AI Career Coach",
      description: "Personalized AI chat based on your profile to guide your career decisions"
    },
    {
      icon: "📊",
      title: "Market Pulse",
      description: "Real-time job market insights and salary data for informed career planning"
    },
    {
      icon: "🗺️",
      title: "Learning Roadmap",
      description: "Personalized skill development plans to bridge your skill gaps"
    },
    {
      icon: "🎯",
      title: "Mock Interviews",
      description: "Practice interview sessions with AI feedback to boost your confidence"
    },
    {
      icon: "📈",
      title: "Progress Tracking",
      description: "Monitor your career growth and improvement over time"
    }
  ];

  return (
    <div style={{
      padding: "120px 24px",
      maxWidth: "1200px",
      margin: "0 auto",
      position: "relative",
      zIndex: 1
    }}>
      <div style={{
        textAlign: "center",
        marginBottom: "80px"
      }}>
        <h2 style={{
          fontFamily: "'Fraunces', serif",
          fontWeight: 300,
          fontSize: "clamp(36px, 4vw, 56px)",
          lineHeight: 1.1,
          letterSpacing: "-.03em",
          color: "var(--t1)",
          marginBottom: "24px"
        }}>
          Everything you need to advance your career
        </h2>
        <p style={{
          fontSize: "18px",
          color: "var(--t2)",
          maxWidth: "600px",
          margin: "0 auto",
          lineHeight: 1.5,
          fontFamily: "'Fraunces', serif",
          fontWeight: 300
        }}>
          Bridgr combines AI technology with career insights to help you make informed decisions about your professional journey.
        </p>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
        gap: "32px",
        marginBottom: "80px"
      }}>
        {features.map((feature, index) => (
          <div
            key={index}
            style={{
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "16px",
              padding: "32px",
              backdropFilter: "blur(20px)",
              transition: "all 0.3s ease"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-4px)";
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)";
            }}
          >
            <div style={{
              fontSize: "32px",
              marginBottom: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "64px",
              height: "64px",
              background: "linear-gradient(135deg, var(--p2), var(--i))",
              borderRadius: "16px"
            }}>
              {feature.icon}
            </div>
            <h3 style={{
              fontFamily: "'Fraunces', serif",
              fontWeight: 400,
              fontSize: "20px",
              color: "var(--t1)",
              marginBottom: "12px",
              letterSpacing: "-.01em"
            }}>
              {feature.title}
            </h3>
            <p style={{
              fontSize: "14px",
              color: "var(--t2)",
              lineHeight: 1.6,
              margin: 0
            }}>
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      <div style={{
        textAlign: "center",
        padding: "60px 24px",
        background: "rgba(255, 255, 255, 0.02)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        borderRadius: "24px",
        backdropFilter: "blur(20px)"
      }}>
        <h3 style={{
          fontFamily: "'Fraunces', serif",
          fontWeight: 300,
          fontSize: "clamp(28px, 3vw, 40px)",
          color: "var(--t1)",
          marginBottom: "20px",
          letterSpacing: "-.02em"
        }}>
          Ready to transform your career?
        </h3>
        <p style={{
          fontSize: "16px",
          color: "var(--t2)",
          marginBottom: "32px",
          maxWidth: "500px",
          margin: "0 auto 32px",
          lineHeight: 1.5
        }}>
          Join thousands of professionals who are already using Bridgr to accelerate their career growth.
        </p>
        <button
          className="btn bg"
          style={{ fontSize: "16px", padding: "16px 40px" }}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          Get Started Free →
        </button>
      </div>
    </div>
  );
};

export default FeaturesSection;
