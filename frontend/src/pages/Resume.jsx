import React, { useState } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon, Input } from '../components/ui';
import { useAnalysis } from '../App';
import { auth } from '../config/firebase';

const formatSalary = (num) => {
  if (typeof num !== 'number') return num;
  if (num >= 10000000) return `₹${(num / 10000000).toFixed(1)}Cr`;
  if (num >= 100000)   return `₹${(num / 100000).toFixed(1)}L`;
  if (num >= 1000)     return `₹${(num / 1000).toFixed(1)}K`;
  return `₹${num.toLocaleString('en-IN')}`;
};

const Resume = ({ profile, onSaveGate, mobileMenuOpen, setMobileMenuOpen, setCurrentPage, onBack }) => {
  const {
    analysisData, setAnalysisData,
    setRoadmapDays, setAutoGenerate,   // ← from context
  } = useAnalysis();

  const [stage, setStage]               = useState("upload");
  const [targetRole, setTargetRole]     = useState(analysisData?.target_role || "");
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError]               = useState("");

  // ── NEW: days input state (shown on results page) ─────────────────────────
  const [daysInput, setDaysInput] = useState(90);

  const steps = [
    "Extracting text from PDF…",
    "Detecting resume sections…",
    "Running NER skill extraction…",
    "Matching to job descriptions…",
    "Generating gap analysis…",
  ];

  // ── upload handler ─────────────────────────────────────────────────────────
  const handleFileUpload = async () => {
    if (!selectedFile) { setError("Please select a file first"); return; }
    if (!targetRole.trim()) { setError("Please enter your target job role"); return; }

    setStage("analyzing");
    setError("");

    try {
      const formData = new FormData();
      formData.append('resume', selectedFile);
      formData.append('target_role', targetRole.trim());

      // Get ID token if user is logged in
      let headers = {};
      if (auth.currentUser) {
        const token = await auth.currentUser.getIdToken();
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/analyze`, {
        method: 'POST',
        headers: headers,
        body: formData,
      });

      if (!response.ok) {
        let msg = "Analysis failed. Please try again.";
        try {
          const errBody = await response.json();
          msg = errBody?.detail || errBody?.message || msg;
        } catch (_) {}
        throw new Error(msg);
      }

      const result = await response.json();
      setAnalysisData(result);
      setStage("results");

      if (!profile?.authenticated) {
        onSaveGate?.();
      }
    } catch (err) {
      setError(err.message || "Failed to analyze resume. Please try again.");
      setStage("upload");
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) { setError("File too large. Maximum size is 10MB."); return; }
    if (!file.name.toLowerCase().endsWith('.pdf')) { setError("Only PDF files are supported."); return; }
    setSelectedFile(file);
    setError("");
  };

  // ── NEW: navigate to roadmap with auto-generate trigger ───────────────────
  const handleGenerateRoadmap = () => {
    const days = parseInt(daysInput, 10);
    if (!days || days < 7) { setError("Please enter at least 7 days."); return; }
    setRoadmapDays(days);    // pass days via context
    setAutoGenerate(true);   // trigger flag — Roadmap useEffect will fire API
    setCurrentPage("roadmap");
  };

  // ── upload stage ───────────────────────────────────────────────────────────
  if (stage === "upload") {
    return (
      <div className="main">
        <Topbar title="Resume Analysis" onBack={onBack} mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />
        <div className="page" style={{ maxWidth: 580, margin: "0 auto" }}>

          <div style={{ textAlign: "center", marginBottom: 36 }}>
            <h1 className="serif" style={{ fontSize: 36, marginBottom: 10, color: "var(--t1)" }}>
              Upload your resume
            </h1>
            <p style={{ color: "var(--t2)", fontSize: 15 }}>
              Get instant AI analysis, skill gap mapping, and salary insights
            </p>
          </div>

          <Card className="gl" style={{ padding: 40, marginBottom: 20, textAlign: "center" }}>
            <div style={{
              width: 80, height: 80, borderRadius: 20,
              background: "linear-gradient(135deg,var(--p2),var(--i))",
              display: "flex", alignItems: "center", justifyContent: "center",
              margin: "0 auto 20px", boxShadow: "0 0 30px rgba(139,92,246,.4)",
            }}>
              <Icon name="upload" s={32} c="white" />
            </div>

            <h3 style={{ fontFamily: "'Fraunces',serif", fontSize: 22, marginBottom: 8, color: "var(--t1)" }}>
              Drop your resume here
            </h3>
            <p style={{ fontSize: 13, color: "var(--t3)", marginBottom: 24 }}>
              PDF only • Max 10MB • We'll extract skills automatically
            </p>

            {/* Target Role Input */}
            <div style={{ marginBottom: 24, textAlign: "left" }}>
              <label style={{ display: "block", fontSize: 14, fontWeight: 600, color: "var(--t1)", marginBottom: 8 }}>
                Target Job Role *
              </label>
              <Input
                type="text"
                placeholder="e.g. Data Scientist, Software Engineer, Product Manager"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                style={{ width: "100%" }}
              />
              <div style={{ fontSize: 11, color: "var(--t3)", marginTop: 4 }}>
                Be specific — "Senior Data Scientist" is better than "tech job"
              </div>
            </div>

            {/* File picker */}
            <div style={{ marginBottom: 24 }}>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                style={{ display: "none" }}
                id="resume-upload"
              />
              <label htmlFor="resume-upload" style={{ cursor: "pointer" }}>
                <div style={{
                  border: "2px dashed var(--gb)", borderRadius: "var(--rm)", padding: "20px",
                  textAlign: "center", background: "rgba(139,92,246,.02)", transition: "all 0.2s",
                }}>
                  <Icon name="upload" s={24} c="var(--p3)" style={{ marginBottom: 8 }} />
                  <div style={{ fontSize: 14, color: "var(--t1)", marginBottom: 4 }}>
                    {selectedFile ? selectedFile.name : "Choose a PDF file"}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--t3)" }}>or drag and drop</div>
                </div>
              </label>
            </div>

            {/* Error */}
            {error && (
              <div style={{
                background: "rgba(239,68,68,.1)", border: "1px solid rgba(239,68,68,.2)",
                borderRadius: "var(--rm)", padding: 12, marginBottom: 20, fontSize: 13, color: "var(--error)",
              }}>
                {error}
              </div>
            )}

            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <Button onClick={handleFileUpload} disabled={!selectedFile || !targetRole.trim()}>
                <Icon name="upload" s={14} c="white" />
                Analyze Resume
              </Button>
            </div>
          </Card>

          {/* Show last analysis if exists */}
          {analysisData && (
            <div style={{ marginTop: 24 }}>
              <Card>
                <div style={{ padding: 24 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                    <h3 style={{ margin: 0, fontSize: 16, color: "var(--t1)" }}>Last Analysis</h3>
                    <Button 
                      size="small" 
                      variant="secondary"
                      onClick={() => setStage("results")}
                    >
                      View Results
                    </Button>
                  </div>
                  <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, color: "var(--t2)", marginBottom: 4 }}>Target Role</div>
                      <div style={{ fontSize: 16, fontWeight: 500, color: "var(--t1)" }}>{analysisData.target_role}</div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, color: "var(--t2)", marginBottom: 4 }}>Match Score</div>
                      <div style={{ fontSize: 16, fontWeight: 500, color: "var(--t1)" }}>{analysisData.match_score}%</div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, color: "var(--t2)", marginBottom: 4 }}>Readiness</div>
                      <div style={{ fontSize: 16, fontWeight: 500, color: "var(--t1)" }}>{analysisData.readiness_level}</div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ── analyzing stage ────────────────────────────────────────────────────────
  if (stage === "analyzing") {
    return (
      <div className="main">
        <Topbar title="Resume Analysis" onBack={onBack} mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />
        <div className="page" style={{ maxWidth: 580, margin: "0 auto", textAlign: "center", paddingTop: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 20 }}>⚡</div>
          <h2 className="serif" style={{ fontSize: 28, marginBottom: 12, color: "var(--t1)" }}>
            Analyzing your resume…
          </h2>
          <p style={{ color: "var(--t2)", fontSize: 15, marginBottom: 32 }}>
            Running NLP extraction and gap analysis. This takes 10–30 seconds.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, textAlign: "left" }}>
            {steps.map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, color: "var(--t3)", fontSize: 13 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--p3)", flexShrink: 0 }} />
                {s}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── results stage ──────────────────────────────────────────────────────────
  const {
    matched_skills       = [],
    missing_required     = [],
    salary_band_estimate = {},
    match_score          = 0,
    readiness_level      = "Unknown",
    transferable_skills  = [],
    feasibility          = {},
    target_role: analyzedRole,
  } = analysisData || {};

  const displayRole = analyzedRole || targetRole || "your target role";

  return (
    <div className="main">
      <Topbar
        title="Resume Analysis"
        sub={`${displayRole} • ${profile?.city || "Bengaluru"}`}
        right={<Button size="small">Export PDF</Button>}
        onBack={onBack}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      <div className="page">
        {/* Score Overview */}
        <Card className="gl" style={{ padding: 30, marginBottom: 14, textAlign: "center" }}>
          <div style={{ fontSize: 14, color: "var(--t3)", marginBottom: 8 }}>Resume Match Score</div>
          <div className="serif" style={{ fontSize: 64, color: "var(--t1)", marginBottom: 12 }}>
            {match_score}%
          </div>
          <div style={{ fontSize: 13, color: "var(--t2)", maxWidth: 400, margin: "0 auto" }}>
            Your resume matches <strong>{matched_skills.length}</strong> key skills for{" "}
            {displayRole} roles in {profile?.city || "Bengaluru"}
          </div>

          {feasibility?.score != null && (
            <div style={{ marginTop: 12, padding: "10px 16px", background: "rgba(139,92,246,.08)", borderRadius: "var(--rm)", display: "inline-block" }}>
              <div style={{ fontSize: 12, color: "var(--t3)", marginBottom: 2 }}>AI Feasibility Score</div>
              <div style={{ fontSize: 22, color: "var(--t1)", fontFamily: "'Fraunces',serif" }}>
                {feasibility.score}%
              </div>
              {feasibility.reasoning && (
                <div style={{ fontSize: 12, color: "var(--t2)", marginTop: 4, maxWidth: 340 }}>
                  {feasibility.reasoning}
                </div>
              )}
              {feasibility.weeks_to_ready && (
                <div style={{ fontSize: 11, color: "var(--t3)", marginTop: 4 }}>
                  Estimated time to ready: ~{feasibility.weeks_to_ready} weeks
                </div>
              )}
            </div>
          )}

          {/* ── NEW: Days input + Generate Roadmap button ── */}
          <div style={{
            marginTop: 28,
            padding: "20px 24px",
            background: "rgba(139,92,246,.06)",
            border: "1px solid rgba(139,92,246,.18)",
            borderRadius: "var(--rl)",
            display: "inline-block",
            textAlign: "left",
            minWidth: 300,
          }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--t1)", marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
              <span>⏱</span> How many days to achieve your goal?
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
              <input
                type="number"
                min={7}
                max={365}
                value={daysInput}
                onChange={(e) => setDaysInput(e.target.value)}
                style={{
                  width: 80,
                  padding: "10px 12px",
                  background: "rgba(255,255,255,.07)",
                  border: "1px solid var(--gb)",
                  borderRadius: "var(--rm)",
                  color: "var(--t1)",
                  fontSize: 16,
                  fontFamily: "'Fraunces',serif",
                  textAlign: "center",
                  outline: "none",
                }}
              />
              <span style={{ fontSize: 13, color: "var(--t3)" }}>days</span>
            </div>
            {error && (
              <div style={{ fontSize: 12, color: "var(--error)", marginBottom: 10 }}>{error}</div>
            )}
            <Button
              onClick={handleGenerateRoadmap}
              style={{
                background: "linear-gradient(135deg, #8b5cf6, #3b82f6)",
                border: "none",
                fontSize: 14,
                padding: "12px 24px",
                width: "100%",
                justifyContent: "center",
              }}
            >
              <Icon name="route" s={15} c="white" />
              Generate My Career Roadmap →
            </Button>
          </div>
        </Card>

        <div className="b2" style={{ marginBottom: 14 }}>
          {/* Matched Skills */}
          <Card className="gl" style={{ padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 14 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: "var(--t1)" }}>Matched Skills</div>
              <Chip name={`${matched_skills.length} found`} level="ok" />
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
              {matched_skills.map(skill => <Chip key={skill} name={skill} level="ok" />)}
            </div>

            {transferable_skills.length > 0 && (
              <div style={{
                marginTop: 16, padding: "12px 14px",
                background: "rgba(16,185,129,.05)", borderRadius: "var(--rm)",
                border: "1px solid rgba(16,185,129,.15)",
              }}>
                <div style={{ fontSize: 12, color: "var(--g)", fontWeight: 600, marginBottom: 6 }}>
                  Transferable skills detected
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {transferable_skills.slice(0, 5).map(t => (
                    <Chip key={t.user_skill} name={`${t.user_skill} → ${t.maps_to_job_skill}`} level="ok" />
                  ))}
                </div>
                <div style={{ fontSize: 12, color: "var(--t3)", marginTop: 8 }}>
                  These give you more credit than they appear on paper.
                </div>
              </div>
            )}
          </Card>

          {/* Gap Analysis */}
          <Card className="gl" style={{ padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 14 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: "var(--t1)" }}>Gap Analysis</div>
              <Chip name={`${missing_required.length} gaps`} level="bad" />
            </div>
            {missing_required.map(gap => (
              <div key={gap.name} style={{
                marginBottom: 10, padding: "10px 14px",
                background: "rgba(255,255,255,.03)", borderRadius: "var(--rm)", border: "1px solid var(--gb)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 4 }}>
                  <span style={{ fontSize: 13, fontWeight: 500, color: "var(--t1)" }}>{gap.name}</span>
                  <Chip
                    name={gap.priority || "High"}
                    level={gap.priority === "Critical" ? "bad" : "learn"}
                    style={{ fontSize: 10, padding: "2px 6px" }}
                  />
                  {gap.estimated_weeks && (
                    <span style={{ fontSize: 11, color: "var(--t3)" }}>~{gap.estimated_weeks}w</span>
                  )}
                </div>
                <div style={{ fontSize: 11.5, color: "var(--t3)", marginBottom: 6 }}>
                  {gap.reason || `Required for ${displayRole}`}
                </div>
                <ProgressBar
                  v={
                    gap.market_demand != null
                      ? Math.round(gap.market_demand * 100)
                      : gap.priority_score != null
                        ? Math.round(gap.priority_score * 100)
                        : 50
                  }
                  color={gap.priority === "Critical" ? "#f43f5e" : "#f59e0b"}
                />
                {gap.learning_resources?.length > 0 && (
                  <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {gap.learning_resources.slice(0, 2).map(r => {
                      const [name, url] = typeof r === "string" ? r.split("|") : [r.name, r.url];
                      return (
                        <a
                          key={name}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: 11, color: "var(--p3)", textDecoration: "underline" }}
                        >
                          {name}
                        </a>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </Card>
        </div>

        {/* Salary band */}
        <Card className="gl" style={{
          padding: 20, marginBottom: 14, display: "flex",
          alignItems: "center", gap: 16, justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Icon name="pin" s={18} c="var(--p3)" />
            <div>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: "var(--t1)" }}>
                {displayRole} Salary in {profile?.city || "Bengaluru"}
              </div>
              <div style={{ fontSize: 12, color: "var(--t3)" }}>Based on current market data</div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 24, textAlign: "center" }}>
            {[
              ["Min",    salary_band_estimate?.min],
              ["Median", salary_band_estimate?.median],
              ["Max",    salary_band_estimate?.max],
            ].map(([label, val]) => (
              <div key={label}>
                <div style={{ fontSize: 11, color: "var(--t3)" }}>{label}</div>
                <div style={{ fontFamily: "'Fraunces',serif", fontSize: 20, color: "var(--t1)" }}>
                  {val ? formatSalary(val) : "—"}
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Re-analyse */}
        <div style={{ textAlign: "center", marginTop: 8 }}>
          <Button variant="secondary" onClick={() => { setStage("upload"); setError(""); }}>
            ↑ Upload a different resume
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Resume;