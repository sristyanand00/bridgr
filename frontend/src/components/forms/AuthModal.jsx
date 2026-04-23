import React from 'react';
import { Button, Icon, Input } from '../ui';

const AuthModal = ({ mode = "save", onAuth, onSkip }) => {
  return (
    <div style={{ 
      position: "fixed", 
      inset: 0, 
      background: "rgba(0,0,5,.8)", 
      backdropFilter: "blur(12px)", 
      zIndex: 300, 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center", 
      padding: 24, 
      animation: "fadeIn .3s both" 
    }}>
      <div className="auth-card afu">
        {/* Logo */}
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: 10, 
          marginBottom: 28, 
          justifyContent: "center" 
        }}>
          <div style={{ 
            width: 36, 
            height: 36, 
            borderRadius: 10, 
            background: "linear-gradient(135deg,var(--p2),var(--i))", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center", 
            boxShadow: "0 0 24px rgba(139,92,246,.45)" 
          }}>
            <Icon name="brain" s={18} c="white" />
          </div>
          <span style={{ 
            fontFamily: "'Fraunces',serif", 
            fontWeight: 300, 
            fontSize: 20, 
            letterSpacing: "-.02em" 
          }}>
            Bridgr
          </span>
        </div>

        {mode === "save" ? (
          <>
            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <div style={{ fontSize: 13, color: "var(--t3)", marginBottom: 8 }}>
                Your analysis is ready
              </div>
              <h2 style={{ 
                fontFamily: "'Fraunces',serif", 
                fontWeight: 300, 
                fontSize: 24, 
                letterSpacing: "-.02em", 
                color: "var(--t1)", 
                marginBottom: 10 
              }}>
                Save your results &amp; track progress
              </h2>
              <p style={{ 
                fontSize: 13.5, 
                color: "var(--t3)", 
                lineHeight: 1.6 
              }}>
                Sign in to save this analysis, track your score over time, and pick up exactly where you left off.
              </p>
            </div>

            <div style={{ 
              background: "rgba(139,92,246,.08)", 
              border: "1px solid rgba(139,92,246,.2)", 
              borderRadius: "var(--rm)", 
              padding: "12px 16px", 
              marginBottom: 24, 
              display: "flex", 
              gap: 10, 
              alignItems: "center" 
            }}>
              <Icon name="sparkle" s={16} c="var(--p3)" />
              <div style={{ fontSize: 13, color: "var(--t2)", lineHeight: 1.5 }}>
                Your quiz answers flow directly into your AI coach — every chat response will be personalized to <em style={{ fontStyle: "italic", color: "var(--t1)" }}>your</em> situation.
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <h2 style={{ 
                fontFamily: "'Fraunces',serif", 
                fontWeight: 300, 
                fontSize: 26, 
                letterSpacing: "-.02em", 
                color: "var(--t1)", 
                marginBottom: 10 
              }}>
                Create your account
              </h2>
              <p style={{ 
                fontSize: 13.5, 
                color: "var(--t3)", 
                lineHeight: 1.6 
              }}>
                Your results will auto-save. Track your career readiness score over time.
              </p>
            </div>
          </>
        )}

        {/* Google OAuth button */}
        <button 
          className="google-btn" 
          onClick={() => onAuth({ name: "Ananya Sharma", email: "ananya@gmail.com", avatar: "A" })}
        >
          {/* Google G logo */}
          <svg width="18" height="18" viewBox="0 0 18 18">
            <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
            <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
            <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
            <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
          </svg>
          Continue with Google
        </button>

        {/* Email divider */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "16px 0" }}>
          <div className="dv" style={{ flex: 1 }} />
          <span style={{ fontSize: 12, color: "var(--t3)" }}>or</span>
          <div className="dv" style={{ flex: 1 }} />
        </div>

        <Input placeholder="Email address" style={{ marginBottom: 10 }} />
        <Button variant="secondary" style={{ width: "100%", justifyContent: "center" }}>
          Continue with email
        </Button>

        {mode === "save" && onSkip && (
          <button 
            onClick={onSkip} 
            style={{ 
              width: "100%", 
              marginTop: 14, 
              background: "none", 
              border: "none", 
              color: "var(--t3)", 
              fontSize: 13, 
              cursor: "none", 
              padding: "8px", 
              fontFamily: "'Geist',sans-serif" 
            }}
          >
            View results without saving →
          </button>
        )}

        <p style={{ 
          fontSize: 11.5, 
          color: "var(--t4)", 
          textAlign: "center", 
          marginTop: 20, 
          lineHeight: 1.5 
        }}>
          By continuing you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
};

export default AuthModal;
