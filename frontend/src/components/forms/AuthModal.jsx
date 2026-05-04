import React, { useState } from 'react';
import { Button, Icon, Input } from '../ui';
import { 
  auth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  GoogleAuthProvider, 
  signInWithPopup 
} from '../../config/firebase';

const AuthModal = ({ mode = "save", onAuth, onSkip, onBack }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(mode === "required");
  const [error, setError] = useState("");

  const handleEmailAuth = async () => {
    if (!email.trim() || !password.trim() || (isSignUp && !name.trim())) {
      setError("Please fill in all fields");
      return;
    }

    setIsLoading(true);
    setError("");
    
    try {
      let userCredential;
      
      if (isSignUp) {
        userCredential = await createUserWithEmailAndPassword(auth, email.trim(), password);
        // Update profile with display name
        await userCredential.user.updateProfile({ displayName: name.trim() });
      } else {
        userCredential = await signInWithEmailAndPassword(auth, email.trim(), password);
      }
      
      const user = userCredential.user;
      const userData = {
        uid: user.uid,
        name: user.displayName || name.trim(),
        email: user.email,
        avatar: (user.displayName || name).charAt(0).toUpperCase(),
        authenticated: true
      };
      
      onAuth(userData);
    } catch (error) {
      let errorMessage = "Authentication failed";
      
      switch (error.code) {
        case 'auth/user-not-found':
          errorMessage = "No account found with this email";
          break;
        case 'auth/wrong-password':
          errorMessage = "Incorrect password";
          break;
        case 'auth/email-already-in-use':
          errorMessage = "Email already registered";
          break;
        case 'auth/weak-password':
          errorMessage = "Password should be at least 6 characters";
          break;
        case 'auth/invalid-email':
          errorMessage = "Invalid email address";
          break;
        default:
          errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      const user = userCredential.user;
      
      const userData = {
        uid: user.uid,
        name: user.displayName,
        email: user.email,
        avatar: user.displayName.charAt(0).toUpperCase(),
        authenticated: true
      };
      
      onAuth(userData);
    } catch (error) {
      setError("Google sign-in failed: " + error.message);
    } finally {
      setIsLoading(false);
    }
  };

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
        {/* Back to landing */}
        {onBack && (
          <button
            onClick={onBack}
            style={{
              display: "flex", alignItems: "center", gap: 6,
              background: "none", border: "none",
              color: "var(--t3)", fontSize: 12.5,
              cursor: "pointer", marginBottom: 16, padding: 0,
              fontFamily: "'Geist', sans-serif",
              transition: "color 0.2s",
            }}
            onMouseEnter={e => e.currentTarget.style.color = "var(--t2)"}
            onMouseLeave={e => e.currentTarget.style.color = "var(--t3)"}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            Back to home
          </button>
        )}
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

        {/* Error Display */}
        {error && (
          <div style={{
            background:"rgba(239,68,68,.1)",
            border:"1px solid rgba(239,68,68,.2)",
            borderRadius:"var(--rm)",
            padding:12,
            marginBottom:16,
            fontSize:13,
            color:"var(--error)"
          }}>
            {error}
          </div>
        )}

        {/* Name Input (only for sign up) */}
        {isSignUp && (
          <Input 
            placeholder="Your name" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ marginBottom: 10 }} 
          />
        )}
        
        {/* Email Input */}
        <Input 
          placeholder="Email address" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ marginBottom: 10 }} 
        />
        
        {/* Password Input */}
        <Input 
          type="password"
          placeholder="Password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ marginBottom: 16 }} 
        />

        {/* Google Sign-in Button */}
        <button 
          className="google-btn" 
          onClick={handleGoogleAuth}
          disabled={isLoading}
          style={{ marginBottom: 16 }}
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
        
        {/* Email Auth Button */}
        <Button 
          onClick={handleEmailAuth}
          disabled={isLoading || !email.trim() || !password.trim() || (isSignUp && !name.trim())}
          style={{ 
            width: "100%", 
            justifyContent: "center",
            background: isLoading ? "var(--g)" : "linear-gradient(135deg,var(--p2),var(--i))"
          }}
        >
          {isLoading ? (
            <>
              <div style={{ 
                width: 16, 
                height: 16, 
                border: "2px solid white", 
                borderTop: "2px solid transparent", 
                borderRadius: "50%", 
                animation: "spin 1s linear infinite",
                marginRight: 8
              }} />
              {isSignUp ? "Creating account..." : "Signing in..."}
            </>
          ) : (
            isSignUp ? "Create account" : "Sign in"
          )}
        </Button>

        {/* Toggle Sign In/Sign Up */}
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <button 
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError("");
            }}
            style={{ 
              background: "none", 
              border: "none", 
              color: "var(--p3)", 
              fontSize: 13, 
              cursor: "pointer",
              textDecoration: "underline"
            }}
          >
            {isSignUp ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
          </button>
        </div>

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
              cursor: "pointer", 
              padding: "8px", 
              fontFamily: "'Geist',sans-serif",
              transition: "color 0.2s"
            }}
            onMouseEnter={e => e.currentTarget.style.color = "var(--t2)"}
            onMouseLeave={e => e.currentTarget.style.color = "var(--t3)"}
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
