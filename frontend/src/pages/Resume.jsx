import React, { useState } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon, Input } from '../components/ui';
import { useAnalysis } from '../App';
import { readiness } from '../config/api';

const samplePosting = `Paste 3-10 real job descriptions here.

Separate postings with a blank line or a line containing ---.

Example:
We are hiring a Backend Engineer with Python, FastAPI, PostgreSQL, Docker, REST APIs, testing, and AWS experience.`;

const Ring = ({ score, size = 120, label, description }) => {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  const getColor = (score) => {
    if (score >= 60) return '#10b981';
    if (score >= 25) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={getColor(score)}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: 24, fontWeight: 'bold', color: 'var(--t1)' }}>
            {score}%
          </div>
        </div>
      </div>
      <div style={{ textAlign: 'center', maxWidth: 140 }}>
        <div style={{ fontSize: 12, color: 'var(--t3)', marginBottom: 4 }}>{label}</div>
        <div style={{ fontSize: 11, color: 'var(--t3)', lineHeight: 1.4 }}>{description}</div>
      </div>
    </div>
  );
};

const getSkillCategory = (skill) => {
  const categories = {
    'python': 'Core engineering',
    'java': 'Core engineering',
    'javascript': 'Core engineering',
    'typescript': 'Core engineering',
    'algorithms': 'Core engineering',
    'data_structures': 'Core engineering',
    'sql': 'Data and storage',
    'postgresql': 'Data and storage',
    'mysql': 'Data and storage',
    'mongodb': 'Data and storage',
    'redis': 'Data and storage',
    'docker': 'Infra and delivery',
    'kubernetes': 'Infra and delivery',
    'aws': 'Infra and delivery',
    'gcp': 'Infra and delivery',
    'azure': 'Infra and delivery',
    'react': 'Frontend',
    'vue': 'Frontend',
    'angular': 'Frontend',
    'html': 'Frontend',
    'css': 'Frontend',
    'fastapi': 'Backend frameworks',
    'django': 'Backend frameworks',
    'flask': 'Backend frameworks',
    'express': 'Backend frameworks',
    'spring': 'Backend frameworks',
    'git': 'Development tools',
    'testing': 'Development tools',
    'ci_cd': 'Development tools',
    'agile': 'Process and collaboration',
    'scrum': 'Process and collaboration',
    'communication': 'Process and collaboration'
  };
  return categories[skill.toLowerCase()] || 'Other skills';
};

const RequirementRow = ({ item, matched = false }) => (
  <div style={{
    padding: '12px 14px',
    borderRadius: 'var(--rm)',
    border: '1px solid var(--gb)',
    background: matched ? 'rgba(16,185,129,.045)' : 'rgba(255,255,255,.03)',
    marginBottom: 9,
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 7 }}>
      <strong style={{ fontSize: 13.5, color: 'var(--t1)' }}>{item.skill}</strong>
      <Chip name={`${item.appears_in} posting${item.appears_in === 1 ? '' : 's'}`} level="v" style={{ fontSize: 10 }} />
      <Chip name={`Level ${item.user_level}/${item.required_level}`} level={matched ? 'ok' : 'learn'} style={{ fontSize: 10 }} />
      {!matched && <Chip name={`-${item.points_lost} pts`} level="bad" style={{ fontSize: 10 }} />}
    </div>
    <div style={{ fontSize: 12, color: 'var(--t3)', lineHeight: 1.45 }}>
      {item.evidence}
    </div>
  </div>
);

const groupSkillsByCategory = (requirements) => {
  const grouped = {};
  requirements.forEach(req => {
    const category = getSkillCategory(req.skill);
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(req);
  });
  return grouped;
};

const ComponentsTable = ({ components }) => {
  if (!components || components.length === 0) return null;
  const thStyle = { fontSize: 11, color: 'var(--t3)', fontWeight: 600, textAlign: 'left', padding: '0 10px 8px 0', whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '0.05em' };
  const tdStyle = (extra) => ({ fontSize: 12.5, color: 'var(--t2)', padding: '7px 10px 7px 0', borderTop: '1px solid var(--gb)', ...extra });
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={thStyle}>Skill</th>
            <th style={{ ...thStyle, textAlign: 'center' }}>Your Level</th>
            <th style={{ ...thStyle, textAlign: 'center' }}>Required</th>
            <th style={{ ...thStyle, textAlign: 'center' }}>Recency</th>
            <th style={{ ...thStyle, textAlign: 'center' }}>Pts Lost</th>
            <th style={thStyle}>Reason</th>
          </tr>
        </thead>
        <tbody>
          {components.map(c => (
            <tr key={c.skill}>
              <td style={tdStyle({ fontWeight: 600, color: 'var(--t1)' })}>{c.skill}</td>
              <td style={tdStyle({ textAlign: 'center' })}>{c.user_level}</td>
              <td style={tdStyle({ textAlign: 'center' })}>{c.required_level}</td>
              <td style={tdStyle({ textAlign: 'center' })}>
                {c.recency_mult != null ? `${Math.round(c.recency_mult * 100)}%` : '—'}
              </td>
              <td style={tdStyle({ textAlign: 'center', color: c.points_lost > 0 ? 'var(--error)' : 'var(--g)' })}>
                {c.points_lost > 0 ? `-${c.points_lost.toFixed(2)}` : '✓'}
              </td>
              <td style={tdStyle({ color: 'var(--t3)', fontSize: 12 })}>{c.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const Resume = ({ profile, mobileMenuOpen, setMobileMenuOpen, setCurrentPage, onBack }) => {
  const { analysisData, setAnalysisData } = useAnalysis();
  const [targetRole, setTargetRole] = useState(analysisData?.target_role || '');
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobDescriptions, setJobDescriptions] = useState('');
  const [weeklyHours, setWeeklyHours] = useState(8);
  const [stage, setStage] = useState(analysisData && typeof analysisData.screen_score === 'number' ? 'report' : 'input');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState({});

  const report = analysisData && typeof analysisData.screen_score === 'number' ? analysisData : null;

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10MB.');
      return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported.');
      return;
    }
    setSelectedFile(file);
    setError('');
  };

  const generateReport = async () => {
    if (!selectedFile) {
      setError('Upload a PDF resume first.');
      return;
    }
    if (!targetRole.trim()) {
      setError('Enter the target role you want to test.');
      return;
    }
    if (!jobDescriptions.trim()) {
      setError('Paste at least one real job description.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('resume', selectedFile);
      formData.append('target_role', targetRole.trim());
      formData.append('job_descriptions', jobDescriptions.trim());
      formData.append('weekly_hours', String(weeklyHours || 8));

      const data = await readiness(formData);
      setAnalysisData(data);
      setStage('report');
    } catch (err) {
      setError(err.message || 'Could not generate readiness report.');
    } finally {
      setLoading(false);
    }
  };

  const toggleTask = (index) => {
    setCompleted(prev => ({ ...prev, [index]: !prev[index] }));
  };

  if (stage === 'report' && report) {
    const doneCount = Object.values(completed).filter(Boolean).length;
    const sprintTotal = report.sprint_tasks?.length || 1;
    const progress = Math.round((doneCount / sprintTotal) * 100);

    return (
      <div className="main">
        <Topbar
          title="Readiness Report"
          sub={`${report.target_role} - ${(() => {
            const minScore = Math.min(report.screen_score, report.interview_score, report.job_score);
            if (minScore < 25) return 'early';
            if (minScore < 60) return 'in progress';
            return 'strong match';
          })()}`}
          onBack={onBack}
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
          right={<Button size="small" variant="secondary" onClick={() => setStage('input')}>New Report</Button>}
        />

        <div className="page">
          {/* Severity-aware banner */}
          {(() => {
            const minScore = Math.min(report.screen_score, report.interview_score, report.job_score);
            const getBannerConfig = (minScore) => {
              if (minScore < 25) return {
                severity: 'early',
                bg: 'rgba(239,68,68,0.1)',
                border: 'rgba(239,68,68,0.2)',
                text: `None of the ${report.requirement_gaps?.length || 0} requirements from your posting show up in your resume yet. That's expected this early — the plan below tells you where to start.`
              };
              if (minScore < 60) return {
                severity: 'in progress',
                bg: 'rgba(245,158,11,0.1)',
                border: 'rgba(245,158,11,0.2)', 
                text: `You're building evidence but have significant gaps remaining. Focus on the highest-frequency requirements first.`
              };
              return {
                severity: 'strong match',
                bg: 'rgba(16,185,129,0.1)',
                border: 'rgba(16,185,129,0.2)',
                text: `Strong alignment with job requirements. Focus on polish and edge cases to maximize your advantage.`
              };
            };
            const bannerConfig = getBannerConfig(minScore);
            return (
              <Card style={{
                padding: 24,
                marginBottom: 16,
                background: bannerConfig.bg,
                borderColor: bannerConfig.border
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <Chip name={bannerConfig.severity} level={minScore >= 60 ? 'ok' : minScore >= 25 ? 'learn' : 'bad'} />
                  <span title={`Lowest score determines overall readiness verdict`} style={{ cursor: 'help', color: 'var(--t3)' }}>
                    ℹ️
                  </span>
                </div>
                <p style={{ color: 'var(--t1)', fontSize: 15, lineHeight: 1.6, margin: 0 }}>
                  {bannerConfig.text}
                </p>
              </Card>
            );
          })()}

          {report.data_mode && report.data_mode !== 'full' && (
            <Card style={{
              padding: '10px 16px',
              marginBottom: 16,
              borderColor: report.data_mode === 'sample' ? 'rgba(251,191,36,.35)' : 'rgba(244,63,94,.35)',
              background: report.data_mode === 'sample' ? 'rgba(251,191,36,.07)' : 'rgba(244,63,94,.07)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13 }}>
                <span style={{ fontSize: 15 }}>{report.data_mode === 'sample' ? '⚠️' : '🔴'}</span>
                <span style={{ color: 'var(--t2)' }}>
                  {report.data_mode === 'sample'
                    ? 'Scored using 50-occupation sample dataset. Run scripts/setup_data.py for full O*NET coverage.'
                    : 'FALLBACK MODE — O*NET data not found. Scores are based on hardcoded role profiles only. Run scripts/setup_data.py.'}
                  <span style={{
                    marginLeft: 8,
                    padding: '2px 7px',
                    borderRadius: 5,
                    fontSize: 10,
                    fontWeight: 700,
                    background: report.data_mode === 'sample' ? 'rgba(251,191,36,.2)' : 'rgba(244,63,94,.2)',
                    color: report.data_mode === 'sample' ? '#fbbf24' : '#f43f5e',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}>
                    {report.data_mode}
                  </span>
                </span>
              </div>
            </Card>
          )}

          {/* Score rings */}
          <Card className="gl" style={{ padding: 32, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', flexWrap: 'wrap', gap: 24 }}>
              <Ring 
                score={report.screen_score} 
                label="Screen" 
                description="Will your resume likely pass the first filter?"
              />
              <Ring 
                score={report.interview_score} 
                label="Interview" 
                description="Can you defend the claims for 45 minutes?"
              />
              <Ring 
                score={report.job_score} 
                label="Job" 
                description="Could you operate in the role after onboarding?"
              />
            </div>
          </Card>

          {/* Skills coverage by category */}
          {report.requirement_gaps && report.requirement_gaps.length > 0 && (
            <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 16 }}>
                Coverage by skill area
              </div>
              {(() => {
                const allSkills = [...(report.requirement_gaps || []), ...(report.matched_requirements || [])];
                const categoryGroups = groupSkillsByCategory(allSkills);
                const categoryStats = Object.entries(categoryGroups)
                  .map(([category, skills]) => {
                    const total = skills.length;
                    const matched = skills.filter(s => report.matched_requirements?.some(m => m.skill === s.skill)).length;
                    const coverage = total > 0 ? (matched / total) * 100 : 0;
                    return { category, matched, total, coverage };
                  })
                  .sort((a, b) => a.coverage - b.coverage);

                return categoryStats.map(({ category, matched, total, coverage }) => (
                  <div key={category} style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <span style={{ fontSize: 13, color: 'var(--t1)', fontWeight: 500 }}>{category}</span>
                      <span style={{ fontSize: 12, color: 'var(--t3)' }}>{matched} of {total} found</span>
                    </div>
                    <ProgressBar value={coverage} />
                  </div>
                ));
              })()}
            </Card>
          )}

          {/* Priority skill chips */}
          {report.requirement_gaps && report.requirement_gaps.length > 0 && (
            <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 14 }}>
                Skills to prioritize
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
                {report.requirement_gaps
                  .slice()
                  .sort((a, b) => b.appears_in - a.appears_in)
                  .map(item => {
                    const isHighPriority = item.appears_in >= 2;
                    return (
                      <div key={item.skill} style={{
                        padding: '8px 12px',
                        borderRadius: 'var(--rm)',
                        border: `1px solid var(--gb)`,
                        background: isHighPriority ? 'rgba(239,68,68,0.1)' : 'rgba(255,255,255,0.03)',
                        color: isHighPriority ? '#ef4444' : 'var(--t2)',
                        fontSize: 12,
                        fontWeight: isHighPriority ? 600 : 400,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6
                      }}>
                        {item.skill}
                        <span style={{ 
                          fontSize: 10, 
                          opacity: 0.7,
                          background: 'rgba(0,0,0,0.2)',
                          padding: '2px 6px',
                          borderRadius: 10
                        }}>
                          {item.appears_in}×
                        </span>
                      </div>
                    );
                  })}
              </div>
              
              {/* Collapsible detailed breakdown */}
              <details>
                <summary style={{ 
                  cursor: 'pointer', 
                  color: 'var(--t3)', 
                  fontSize: 13,
                  userSelect: 'none',
                  marginBottom: 12
                }}>
                  See full breakdown
                </summary>
                <ComponentsTable components={report.components} />
              </details>
            </Card>
          )}

          <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 5 }}>
                  Your next 14 days
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--t3)' }}>
                  Complete these tasks, then re-score with stronger evidence.
                </div>
                {(() => {
                  const totalGaps = report.requirement_gaps?.length || 0;
                  const sprintGaps = report.sprint_tasks?.length || 0;
                  const remainingSprints = totalGaps > sprintGaps ? Math.ceil((totalGaps - sprintGaps) / Math.max(sprintGaps, 1)) : 0;
                  if (remainingSprints > 0) {
                    return (
                      <div style={{ fontSize: 12, color: 'var(--t3)', marginTop: 4 }}>
                        This sprint covers {sprintGaps} of your {totalGaps} gaps. At this pace you'll need about {remainingSprints} more sprint{remainingSprints === 1 ? '' : 's'} like this to close the rest.
                      </div>
                    );
                  }
                  return null;
                })()}
              </div>
              <Chip name={`${progress}% sprint complete`} level={progress === 100 ? 'ok' : 'v'} />
            </div>

            {report.sprint_tasks?.map((task, index) => (
              <div key={task.title} style={{
                display: 'flex',
                gap: 12,
                padding: '13px 0',
                borderBottom: index < report.sprint_tasks.length - 1 ? '1px solid var(--gb)' : 'none',
              }}>
                <button
                  onClick={() => toggleTask(index)}
                  style={{
                    width: 24,
                    height: 24,
                    borderRadius: 7,
                    border: '1px solid var(--gb)',
                    background: completed[index] ? 'var(--g)' : 'rgba(255,255,255,.04)',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    flexShrink: 0,
                  }}
                >
                  {completed[index] ? <Icon name="check" s={13} c="white" /> : null}
                </button>
                <div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', marginBottom: 5 }}>
                    <Chip name={task.day_range} level="v" style={{ fontSize: 10 }} />
                    <strong style={{ color: 'var(--t1)', fontSize: 13.5 }}>{task.title}</strong>
                  </div>
                  <div style={{ color: 'var(--t2)', fontSize: 12.5, lineHeight: 1.5 }}>{task.outcome}</div>
                </div>
              </div>
            ))}
          </Card>

          {/* Matched requirements */}
          {report.matched_requirements?.length > 0 && (
            <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 14 }}>
                Evidence already strong enough
              </div>
              {report.matched_requirements.slice(0, 8).map(item => (
                <RequirementRow key={item.skill} item={item} matched />
              ))}
            </Card>
          )}

          {/* Resume bullets and skip for now in side-by-side layout */}

          <div className="b2">
            <Card className="gl" style={{ padding: 24 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 12 }}>
                Resume bullets to earn, not fake
              </div>
              {(report.resume_bullets || []).map((bullet, index) => (
                <div key={index} style={{ fontSize: 13, color: 'var(--t2)', lineHeight: 1.55, marginBottom: 10 }}>
                  {bullet}
                </div>
              ))}
            </Card>

            <Card className="gl" style={{ padding: 24 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 12 }}>
                Do not learn these now
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {(report.skip_for_now || []).map(skill => (
                  <Chip key={skill} name={skill} level="n" />
                ))}
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--t3)', marginTop: 14, lineHeight: 1.55 }}>
                These appeared less often than your top gaps. The product should save your effort, not give you an infinite syllabus.
              </div>
            </Card>
          </div>

          <div style={{ marginTop: 24, padding: '10px 4px', borderTop: '1px solid var(--gb)', display: 'flex', justifyContent: 'flex-end' }}>
            <span style={{ fontSize: 11, color: 'var(--t4)' }}>
              scoring {report.scoring_version}
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main">
      <Topbar
        title="Create Readiness Report"
        sub="Resume evidence + real job descriptions"
        onBack={onBack}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      <div className="page" style={{ maxWidth: 860, margin: '0 auto' }}>
        <Card className="gl" style={{ padding: 28, marginBottom: 16 }}>
          <div style={{ fontSize: 14, fontWeight: 650, color: 'var(--t1)', marginBottom: 18 }}>
            1. Upload resume and choose target
          </div>

          <div className="b2" style={{ gap: 16 }}>
            <div>
              <div style={{ fontSize: 12, color: 'var(--t3)', marginBottom: 7 }}>Target role</div>
              <Input
                value={targetRole}
                onChange={event => setTargetRole(event.target.value)}
                placeholder="Backend Engineer, Data Analyst, SDET..."
              />
            </div>
            <div>
              <div style={{ fontSize: 12, color: 'var(--t3)', marginBottom: 7 }}>Hours/week for sprint</div>
              <Input
                type="number"
                min={3}
                max={30}
                value={weeklyHours}
                onChange={event => setWeeklyHours(parseInt(event.target.value, 10))}
              />
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <input id="resume-file" type="file" accept=".pdf" onChange={handleFileSelect} style={{ display: 'none' }} />
            <label htmlFor="resume-file" style={{
              display: 'block',
              border: '1px dashed var(--gb)',
              borderRadius: 'var(--rl)',
              padding: 22,
              cursor: 'pointer',
              background: 'rgba(255,255,255,.025)',
            }}>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <Icon name="upload" s={22} c="var(--p3)" />
                <div>
                  <div style={{ color: 'var(--t1)', fontWeight: 600, fontSize: 14 }}>
                    {selectedFile ? selectedFile.name : 'Choose a PDF resume'}
                  </div>
                  <div style={{ color: 'var(--t3)', fontSize: 12 }}>
                    We extract evidence, not a vanity resume score.
                  </div>
                </div>
              </div>
            </label>
          </div>
        </Card>

        <Card className="gl" style={{ padding: 28, marginBottom: 16 }}>
          <div style={{ fontSize: 14, fontWeight: 650, color: 'var(--t1)', marginBottom: 8 }}>
            2. Paste real job descriptions
          </div>
          <div style={{ fontSize: 12.5, color: 'var(--t3)', marginBottom: 12 }}>
            Use jobs you would actually apply to. The more specific the postings, the more honest the report.
          </div>
          <textarea
            value={jobDescriptions}
            onChange={event => setJobDescriptions(event.target.value)}
            placeholder={samplePosting}
            style={{
              width: '100%',
              minHeight: 230,
              resize: 'vertical',
              border: '1px solid var(--gb)',
              borderRadius: 'var(--rm)',
              background: 'rgba(255,255,255,.045)',
              color: 'var(--t1)',
              padding: 14,
              outline: 'none',
              fontFamily: "'Geist', sans-serif",
              fontSize: 13,
              lineHeight: 1.55,
            }}
          />
        </Card>

        {error && (
          <Card style={{ padding: 14, marginBottom: 16, borderColor: 'rgba(244,63,94,.3)', background: 'rgba(244,63,94,.08)' }}>
            <div style={{ color: 'var(--error)', fontSize: 13 }}>{error}</div>
          </Card>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <Button variant="secondary" onClick={() => setCurrentPage('dashboard')}>Cancel</Button>
          <Button onClick={generateReport} disabled={loading}>
            <Icon name="tgt" s={16} c="white" />
            {loading ? 'Generating report...' : 'Generate Readiness Report'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Resume;
