import React, { useState, useEffect } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, Icon } from '../components/ui';
import { auth } from '../config/firebase';

const History = ({ profile, mobileMenuOpen, setMobileMenuOpen, setCurrentPage, onBack }) => {
  const [history, setHistory] = useState({ analyses: [], roadmaps: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      if (profile?.authenticated) {
        setLoading(true);
        setError("");
        try {
          const token = await auth.currentUser.getIdToken();
          const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) {
            const data = await response.json();
            setHistory(data);
          } else {
            throw new Error("Failed to fetch history");
          }
        } catch (err) {
          console.error("Error fetching history:", err);
          setError("Failed to load history. Please try again.");
        } finally {
          setLoading(false);
        }
      }
    };
    fetchHistory();
  }, [profile?.authenticated]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score) => {
    if (score >= 70) return '#10b981';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  if (!profile?.authenticated) {
    return (
      <div className="main">
        <Topbar 
          title="History" 
          onBack={onBack}
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
        />
        <div style={{ 
          padding: '40px 24px', 
          textAlign: 'center',
          color: 'var(--t2)'
        }}>
          <Icon name="lock" s={48} c="var(--t3)" style={{ marginBottom: 16 }} />
          <h3 style={{ marginBottom: 8 }}>Sign in Required</h3>
          <p>Please sign in to view your analysis history.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="main">
      <Topbar 
        title="History" 
        sub="Your past analyses and roadmaps"
        onBack={onBack}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Icon name="loader" s={32} c="var(--p3)" style={{ animation: 'spin 1s linear infinite' }} />
            <p style={{ marginTop: 16, color: 'var(--t2)' }}>Loading history...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Icon name="alert" s={32} c="var(--error)" style={{ marginBottom: 16 }} />
            <p style={{ color: 'var(--error)' }}>{error}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        ) : (
          <>
            {/* Analyses Section */}
            <div style={{ marginBottom: 48 }}>
              <h2 style={{ marginBottom: 24, color: 'var(--t1)' }}>Resume Analyses</h2>
              {history.analyses.length === 0 ? (
                <Card>
                  <div style={{ padding: '40px', textAlign: 'center', color: 'var(--t2)' }}>
                    <Icon name="document" s={48} c="var(--t3)" style={{ marginBottom: 16 }} />
                    <h3>No Analyses Yet</h3>
                    <p>Upload and analyze your resume to see your history here.</p>
                    <Button onClick={() => setCurrentPage('resume')}>
                      Analyze Resume
                    </Button>
                  </div>
                </Card>
              ) : (
                <div style={{ display: 'grid', gap: 16 }}>
                  {history.analyses.map((analysis) => (
                    <Card key={analysis.id}>
                      <div style={{ padding: '24px' }}>
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'flex-start',
                          marginBottom: 16
                        }}>
                          <div>
                            <h3 style={{ margin: '0 0 8px 0', color: 'var(--t1)' }}>
                              {analysis.target_role}
                            </h3>
                            <p style={{ margin: 0, fontSize: 12, color: 'var(--t3)' }}>
                              {formatDate(analysis.created_at)}
                            </p>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <div style={{ 
                              fontSize: 24, 
                              fontWeight: 'bold', 
                              color: getScoreColor(analysis.match_score)
                            }}>
                              {analysis.match_score}%
                            </div>
                            <div style={{ fontSize: 12, color: 'var(--t3)' }}>
                              Match Score
                            </div>
                          </div>
                        </div>
                        
                        {analysis.feasibility && (
                          <div style={{ 
                            background: 'rgba(139,92,246,0.1)', 
                            border: '1px solid rgba(139,92,246,0.2)',
                            borderRadius: 'var(--rm)', 
                            padding: '12px',
                            marginBottom: 16
                          }}>
                            <div style={{ fontSize: 14, color: 'var(--t2)', marginBottom: 4 }}>
                              Feasibility Score
                            </div>
                            <div style={{ 
                              fontSize: 18, 
                              fontWeight: 'bold', 
                              color: 'var(--p3)' 
                            }}>
                              {analysis.feasibility.score}%
                            </div>
                            <div style={{ fontSize: 12, color: 'var(--t3)', marginTop: 4 }}>
                              {analysis.feasibility.reasoning?.substring(0, 100)}...
                            </div>
                          </div>
                        )}
                        
                        <div style={{ display: 'flex', gap: 12 }}>
                          <Button 
                            size="small"
                            onClick={() => setCurrentPage('resume')}
                          >
                            <Icon name="refresh" s={12} />
                            New Analysis
                          </Button>
                          <Button 
                            size="small" 
                            variant="secondary"
                            onClick={() => setCurrentPage('roadmap')}
                          >
                            <Icon name="map" s={12} />
                            View Roadmap
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Roadmaps Section */}
            <div>
              <h2 style={{ marginBottom: 24, color: 'var(--t1)' }}>Learning Roadmaps</h2>
              {history.roadmaps.length === 0 ? (
                <Card>
                  <div style={{ padding: '40px', textAlign: 'center', color: 'var(--t2)' }}>
                    <Icon name="map" s={48} c="var(--t3)" style={{ marginBottom: 16 }} />
                    <h3>No Roadmaps Yet</h3>
                    <p>Generate a learning roadmap to see your history here.</p>
                    <Button onClick={() => setCurrentPage('roadmap')}>
                      Generate Roadmap
                    </Button>
                  </div>
                </Card>
              ) : (
                <div style={{ display: 'grid', gap: 16 }}>
                  {history.roadmaps.map((roadmap) => (
                    <Card key={roadmap.id}>
                      <div style={{ padding: '24px' }}>
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'flex-start',
                          marginBottom: 16
                        }}>
                          <div>
                            <h3 style={{ margin: '0 0 8px 0', color: 'var(--t1)' }}>
                              {roadmap.target_role}
                            </h3>
                            <p style={{ margin: 0, fontSize: 12, color: 'var(--t3)' }}>
                              {formatDate(roadmap.created_at)}
                            </p>
                          </div>
                          <Chip size="small" color="var(--p3)">
                            {roadmap.total_days} days
                          </Chip>
                        </div>
                        
                        {roadmap.summary && (
                          <p style={{ 
                            color: 'var(--t2)', 
                            fontSize: 14, 
                            lineHeight: 1.5,
                            marginBottom: 16
                          }}>
                            {roadmap.summary.substring(0, 200)}...
                          </p>
                        )}
                        
                        <div style={{ display: 'flex', gap: 12 }}>
                          <Button 
                            size="small"
                            onClick={() => setCurrentPage('roadmap')}
                          >
                            <Icon name="eye" s={12} />
                            View Details
                          </Button>
                          <Button 
                            size="small" 
                            variant="secondary"
                            onClick={() => setCurrentPage('resume')}
                          >
                            <Icon name="refresh" s={12} />
                            New Roadmap
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default History;
