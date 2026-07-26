import React, { useState } from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon, Input } from '../components/ui';
import { useAnalysis } from '../App';
import { readiness } from '../config/api';

const samplePosting = `Paste 3-10 real job descriptions here.

Separate postings with a blank line or a line containing ---.

Example:
We are hiring a Backend Engineer with Python, FastAPI, PostgreSQL, Docker, REST APIs, testing, and AWS experience.`;

const ScoreCard = ({ label, value, description }) => (
  <Card className="gl" style={{ padding: 20 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
      <span style={{ fontSize: 12, color: 'var(--t3)' }}>{label}</span>
      <strong style={{ color: 'var(--t1)' }}>{value}%</strong>
    </div>
    <div className="serif" style={{ fontSize: 34, color: 'var(--t1)', marginBottom: 10 }}>
      {value}
    </div>
    <ProgressBar value={value} />
    <div style={{ fontSize: 12, color: 'var(--t3)', marginTop: 10, lineHeight: 1.45 }}>
      {description}
    </div>
  </Card>
);

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
  const [stage, setStage] = useState(analysisData?.screen_score ? 'report' : 'input');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState({});

  const report = analysisData?.screen_score ? analysisData : null;

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
          sub={`${report.target_role} - ${report.verdict}`}
          onBack={onBack}
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
          right={<Button size="small" variant="secondary" onClick={() => setStage('input')}>New Report</Button>}
        />

        <div className="page">
          <Card className="gl" style={{ padding: 28, marginBottom: 16 }}>
            <Chip name={report.verdict} level={Math.min(report.screen_score, report.interview_score, report.job_score) >= 55 ? 'ok' : 'learn'} style={{ marginBottom: 16 }} />
            <h1 className="serif" style={{ fontSize: 34, color: 'var(--t1)', margin: '0 0 8px' }}>
              You are being measured against real postings, not a generic role template.
            </h1>
            <p style={{ color: 'var(--t2)', fontSize: 14, lineHeight: 1.6, maxWidth: 760, margin: 0 }}>
              Every gap below comes from a requirement found in the jobs you pasted and is compared with evidence extracted from your resume.
            </p>
          </Card>

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

          <div className="b3" style={{ marginBottom: 16 }}>
            <ScoreCard label="Screen" value={report.screen_score} description="Will your resume likely pass the first filter?" />
            <ScoreCard label="Interview" value={report.interview_score} description="Can you defend the claims for 45 minutes?" />
            <ScoreCard label="Job" value={report.job_score} description="Could you operate in the role after onboarding?" />
          </div>

          <div className="b2" style={{ marginBottom: 16 }}>
            <Card className="gl" style={{ padding: 24 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 14 }}>
                Highest-ROI gaps
              </div>
              {(report.requirement_gaps || []).slice(0, 8).map(item => (
                <RequirementRow key={item.skill} item={item} />
              ))}
            </Card>

            <Card className="gl" style={{ padding: 24 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 14 }}>
                Evidence already strong enough
              </div>
              {report.matched_requirements?.length ? (
                report.matched_requirements.slice(0, 8).map(item => (
                  <RequirementRow key={item.skill} item={item} matched />
                ))
              ) : (
                <div style={{ color: 'var(--t3)', fontSize: 13 }}>
                  No requirement is fully supported yet. Start with the sprint below.
                </div>
              )}
            </Card>
          </div>

          <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'center', marginBottom: 18, flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 5 }}>
                  Your next 14 days
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--t3)' }}>
                  Complete these tasks, then re-score with stronger evidence.
                </div>
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

          {report.components?.length > 0 && (
            <Card className="gl" style={{ padding: 24, marginBottom: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 14 }}>
                Per-requirement scoring breakdown
              </div>
              <ComponentsTable components={report.components} />
            </Card>
          )}

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
