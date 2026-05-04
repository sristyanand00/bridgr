import React, { useState, useEffect } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon } from '../components/ui';
import { useAnalysis } from '../App';

const Roadmap = ({ profile, mobileMenuOpen, setMobileMenuOpen }) => {
  const {
    analysisData,
    roadmapDays,  setRoadmapDays,
    autoGenerate, setAutoGenerate,
  } = useAnalysis();

  const [targetCareer,    setTargetCareer]    = useState(analysisData?.target_role || "");
  const [roadmapLoading,  setRoadmapLoading]  = useState(false);
  const [generatedPhases, setGeneratedPhases] = useState(null);
  const [totalDays,       setTotalDays]       = useState(roadmapDays || 90);
  const [summary,         setSummary]         = useState("");
  const [error,           setError]           = useState("");

  // ── sync targetCareer if analysisData arrives after mount ─────────────────
  useEffect(() => {
    if (analysisData?.target_role) setTargetCareer(analysisData.target_role);
  }, [analysisData]);

  // ── AUTO-GENERATE: fires immediately when user navigates from Resume ───────
  useEffect(() => {
    if (autoGenerate && analysisData) {
      setAutoGenerate(false);   // clear flag — prevent double-fire
      setTotalDays(roadmapDays);
      generateRoadmap(roadmapDays);
    }
    }, [autoGenerate]);

  // ── generate roadmap ───────────────────────────────────────────────────────
  const generateRoadmap = async (days = totalDays) => {
    const role = analysisData?.target_role || targetCareer;
    if (!role?.trim()) { setError("No target role found — please go back and analyse a resume first."); return; }

    setRoadmapLoading(true);
    setError("");
    setGeneratedPhases(null);

    try {
      const payload = {
        target_role:      role,
        match_score:      analysisData?.match_score      ?? 0,
        readiness_level:  analysisData?.readiness_level  ?? "Foundation Stage",
        roadmap_inputs:   analysisData?.learning_roadmap_inputs ?? {},
        matched_skills:   analysisData?.matched_skills   ?? [],
        missing_required: analysisData?.missing_required ?? [],
        total_days:       parseInt(days, 10) || 90,   // ← NEW field
      };

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/roadmap`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let msg = "Failed to generate roadmap.";
        try { const b = await response.json(); msg = b?.detail || b?.message || msg; } catch (_) {}
        throw new Error(msg);
      }

      const data = await response.json();
      setGeneratedPhases(data.phases || []);
      setTotalDays(data.total_days || days);
      setSummary(data.summary || "");

    } catch (err) {
      console.error("Roadmap error:", err);
      setError(err.message || "Failed to generate roadmap. Please try again.");
    } finally {
      setRoadmapLoading(false);
    }
  };

  const matchScore = analysisData?.match_score ?? 0;
  const gapCount   = analysisData?.missing_required?.length ?? 0;

  const progressMetrics = generatedPhases
    ? [
        { label: "Resume Match Score",  value: matchScore,             bar: true },
        { label: "Total Timeline",      value: `${totalDays} days`,    bar: false },
        { label: "Skills to Bridge",    value: `${gapCount} skills`,   bar: false },
      ]
    : [
        { label: "Resume Match Score",  value: matchScore,             bar: true },
        { label: "Target Timeline",     value: `${roadmapDays} days`,  bar: false },
        { label: "Skills to Bridge",    value: `${gapCount} skills`,   bar: false },
      ];

  // ── render ─────────────────────────────────────────────────────────────────
  return (
    <div className="main">
      <Topbar
        title="Your Career Roadmap"
        sub={targetCareer ? `Roadmap to becoming a ${targetCareer}` : "Plan your move to a new career"}
        right={
          <>
            <Chip name="AI Powered" className="tv" style={{ fontSize: 10 }} />
            <Button size="small" style={{ marginLeft: 8 }} onClick={() => {
              setGeneratedPhases(null);
              setSummary("");
              setError("");
            }}>
              Regenerate
            </Button>
          </>
        }
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      <div className="page">

        {/* ── Loading state ── */}
        {roadmapLoading && (
          <Card className="gl" style={{ padding: 48, textAlign: "center", marginBottom: 16 }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>⚡</div>
            <div className="serif" style={{ fontSize: 24, color: "var(--t1)", marginBottom: 8 }}>
              Building your {totalDays}-day roadmap…
            </div>
            <div style={{ fontSize: 14, color: "var(--t3)" }}>Talking to AI teacher…</div>
          </Card>
        )}

        {/* ── Error ── */}
        {error && !roadmapLoading && (
          <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
            <div style={{ fontSize: 13, color: "var(--error)", marginBottom: 12 }}>{error}</div>
            <Button onClick={() => generateRoadmap()}>Retry</Button>
          </Card>
        )}

        {/* ── Progress metrics ── */}
        {!roadmapLoading && (
          <div className="b3" style={{ marginBottom: 16 }}>
            {progressMetrics.map(metric => (
              <Card key={metric.label}>
                <div style={{ fontSize: 12, color: "var(--t3)", marginBottom: 10 }}>{metric.label}</div>
                {metric.bar ? (
                  <>
                    <div style={{ fontFamily: "'Fraunces',serif", fontSize: 30, fontWeight: 300, marginBottom: 10 }}>
                      {metric.value}%
                    </div>
                    <ProgressBar value={metric.value} />
                  </>
                ) : (
                  <div style={{ fontFamily: "'Fraunces',serif", fontSize: 28, fontWeight: 300 }}>
                    {metric.value}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}

        {/* ── Summary card ── */}
        {!roadmapLoading && summary && generatedPhases?.length > 0 && (
          <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--t1)", marginBottom: 8 }}>📋 Plan Summary</div>
            <p style={{ fontSize: 13.5, color: "var(--t2)", lineHeight: 1.6, margin: 0 }}>{summary}</p>
            <div style={{ marginTop: 12, display: "flex", gap: 16 }}>
              <div>
                <span style={{ fontSize: 11, color: "var(--t3)" }}>Goal </span>
                <span style={{ fontSize: 13, color: "var(--t1)", fontWeight: 600 }}>{targetCareer}</span>
              </div>
              <div>
                <span style={{ fontSize: 11, color: "var(--t3)" }}>Duration </span>
                <span style={{ fontSize: 13, color: "var(--t1)", fontWeight: 600 }}>{totalDays} days</span>
              </div>
            </div>
          </Card>
        )}

        {/* ── Teacher-style phase + topic rendering ── */}
        {!roadmapLoading && generatedPhases?.length > 0 && (
          <Card className="gl" style={{ padding: 30 }}>
            <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 28, color: "var(--t1)" }}>
              {totalDays}-Day Roadmap — {targetCareer}
            </div>

            {generatedPhases.map((phase, index) => (
              <div key={phase.label || index} style={{
                position: "relative",
                paddingLeft: 30,
                marginBottom: index < generatedPhases.length - 1 ? 40 : 0,
              }}>
                {/* Timeline connector */}
                {index < generatedPhases.length - 1 && <div className="tl-line" />}

                {/* Timeline dot */}
                <div style={{
                  position: "absolute", left: 0, top: 4, width: 22, height: 22, borderRadius: "50%",
                  border: `2px solid ${index === 0 ? "var(--p)" : "var(--t4)"}`,
                  background: index === 0 ? "rgba(139,92,246,.15)" : "transparent",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: index === 0 ? "0 0 14px rgba(139,92,246,.4)" : "none",
                }}>
                  {index === 0 && <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--p3)" }} />}
                </div>

                <div style={{
                  background: index === 0 ? "rgba(139,92,246,.05)" : "transparent",
                  borderRadius: "var(--rl)", padding: index === 0 ? "20px" : "0 0 0 4px",
                  border: index === 0 ? "1px solid rgba(139,92,246,.18)" : "none",
                }}>
                  {/* Phase header */}
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <span style={{
                          fontSize: 11, fontWeight: 700, color: "var(--p3)",
                          background: "rgba(139,92,246,.12)", borderRadius: 4,
                          padding: "2px 8px", letterSpacing: "0.05em",
                        }}>
                          {phase.duration || phase.day_range || `Phase ${phase.phase}`}
                        </span>
                        <div style={{ fontWeight: 600, fontSize: 15, color: "var(--t1)" }}>
                          {phase.label}
                        </div>
                      </div>
                      {phase.goal && (
                        <div style={{ fontSize: 12.5, color: "var(--t2)", fontStyle: "italic", marginBottom: 4 }}>
                          Goal: {phase.goal}
                        </div>
                      )}
                    </div>
                    {index === 0 && <Chip name="In Progress" className="tv" />}
                  </div>

                  {/* ── Topics (teacher-style) ── */}
                  {phase.topics?.length > 0 ? (
                    <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 12 }}>
                      {phase.topics.map((topic, ti) => (
                        <div key={ti} style={{
                          background: "rgba(255,255,255,.03)",
                          border: "1px solid var(--gb)",
                          borderRadius: "var(--rm)",
                          padding: "14px 16px",
                        }}>
                          {/* Topic title + day range */}
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                            <div style={{ fontWeight: 600, fontSize: 13, color: "var(--t1)", display: "flex", alignItems: "center", gap: 6 }}>
                              <span>📖</span>
                              <span>Topic {ti + 1}: {topic.title || topic.name}</span>
                            </div>
                            {topic.days && (
                              <span style={{ fontSize: 11, color: "var(--t3)", whiteSpace: "nowrap", marginLeft: 8 }}>
                                {topic.days}
                              </span>
                            )}
                          </div>

                          {/* What to learn */}
                          {topic.subtopics?.length > 0 && (
                            <div style={{ marginBottom: 10 }}>
                              <div style={{ fontSize: 11, color: "var(--t3)", fontWeight: 600, marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                                What to learn
                              </div>
                              {topic.subtopics.map((sub, si) => (
                                <div key={si} style={{ fontSize: 12.5, color: "var(--t2)", marginBottom: 3, display: "flex", gap: 6 }}>
                                  <span style={{ color: "var(--p3)", flexShrink: 0 }}>→</span>
                                  <span>{sub}</span>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Mini project */}
                          {topic.mini_project && (
                            <div style={{
                              marginBottom: 10, padding: "8px 12px",
                              background: "rgba(16,185,129,.06)", border: "1px solid rgba(16,185,129,.15)",
                              borderRadius: "var(--rm)",
                            }}>
                              <div style={{ fontSize: 11, color: "var(--g)", fontWeight: 600, marginBottom: 3 }}>Mini Project</div>
                              <div style={{ fontSize: 12.5, color: "var(--t2)" }}>{topic.mini_project}</div>
                            </div>
                          )}

                          {/* Per-topic resource */}
                          {topic.resource && (
                            <a
                              href={topic.resource.url || "#"}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ display: "inline-flex", alignItems: "center", gap: 5, textDecoration: "none", fontSize: 12 }}
                            >
                              <Icon name="link" s={13} c="var(--p3)" />
                              <span style={{ color: "var(--t1)" }}>{topic.resource.name || "Resource"}</span>
                              {topic.resource.free !== false && (
                                <Chip name="Free" level="ok" style={{ fontSize: 10, padding: "1px 6px" }} />
                              )}
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    /* Fallback: week-by-week when no topics field */
                    phase.weeks?.length > 0 && (
                      <div style={{ marginBottom: 10 }}>
                        {phase.weeks.map((w, wi) => (
                          <div key={wi} style={{
                            fontSize: 12.5, color: "var(--t2)", marginBottom: 6,
                            paddingLeft: 10, borderLeft: "2px solid var(--gb)",
                          }}>
                            <strong style={{ color: "var(--t1)" }}>Week {w.week}:</strong> {w.focus}
                            {w.milestone && <span style={{ color: "var(--t3)" }}> — {w.milestone}</span>}
                          </div>
                        ))}
                      </div>
                    )
                  )}

                  {/* Phase-level milestones */}
                  {phase.milestones?.length > 0 && (
                    <div style={{
                      marginTop: 14, padding: "10px 14px",
                      background: "rgba(139,92,246,.04)", borderRadius: "var(--rm)",
                      border: "1px solid rgba(139,92,246,.12)",
                    }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: "var(--p3)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                        ✅ Milestones by {phase.duration || phase.day_range || `Phase ${phase.phase}`}
                      </div>
                      {phase.milestones.map((m, mi) => (
                        <div key={mi} style={{ fontSize: 12.5, color: "var(--t2)", marginBottom: 3, display: "flex", gap: 6 }}>
                          <span style={{ color: "var(--g)", fontWeight: 700 }}>✓</span>
                          <span>{m}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Phase-level skills chips */}
                  {phase.skills?.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 12 }}>
                      {phase.skills.map(skill => (
                        <Chip key={skill} name={skill} level={index === 0 ? "learn" : "n"} />
                      ))}
                    </div>
                  )}

                  {/* Phase-level resources (fallback when no per-topic resources) */}
                  {!phase.topics?.length && phase.resources?.length > 0 && (
                    <div style={{ display: "flex", gap: 7, flexWrap: "wrap", marginTop: 10 }}>
                      {phase.resources.map((resource, ri) => {
                        const name = resource.name || resource;
                        const url  = resource.url  || "#";
                        const free = resource.free !== false;
                        return (
                          <a
                            key={ri}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="res-link"
                            style={{ fontSize: 12, textDecoration: "none", display: "flex", alignItems: "center", gap: 4 }}
                          >
                            <Icon name="link" s={13} c="var(--p3)" />
                            <span style={{ color: "var(--t1)" }}>{name}</span>
                            {free && <Chip name="Free" level="ok" style={{ fontSize: 10, padding: "1px 6px" }} />}
                          </a>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </Card>
        )}

        {/* ── Empty state after load with no phases ── */}
        {!roadmapLoading && generatedPhases !== null && generatedPhases.length === 0 && (
          <Card className="gl" style={{ padding: 40, textAlign: "center" }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>🤔</div>
            <div style={{ fontSize: 15, color: "var(--t2)" }}>
              No roadmap phases were returned. Please try again.
            </div>
            <Button style={{ marginTop: 16 }} onClick={() => generateRoadmap()}>
              Retry
            </Button>
          </Card>
        )}

      </div>
    </div>
  );
};

export default Roadmap;