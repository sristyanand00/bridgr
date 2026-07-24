import React from 'react';
import { Topbar } from '../components/layout';
import { Button, Card, Chip, ProgressBar, Icon } from '../components/ui';

const Dashboard = ({ setCurrentPage, profile, analysisData, mobileMenuOpen, setMobileMenuOpen }) => {
  const hasReport = Boolean(analysisData?.screen_score || analysisData?.match_score);
  const screenScore = analysisData?.screen_score ?? analysisData?.match_score ?? 0;
  const interviewScore = analysisData?.interview_score ?? 0;
  const jobScore = analysisData?.job_score ?? 0;

  const steps = [
    {
      title: 'Extract evidence',
      body: 'Turn your resume into a claim ledger: skills, source bullets, confidence, and depth.',
    },
    {
      title: 'Compare real jobs',
      body: 'Paste job descriptions you actually want and score against their repeated requirements.',
    },
    {
      title: 'Close the gap',
      body: 'Get a 14-day sprint that raises evidence for the highest-return gaps first.',
    },
  ];

  return (
    <div className="main">
      <Topbar
        title="Readiness Engine"
        sub={`Know if you are actually ready${profile?.name ? `, ${profile.name.split(' ')[0]}` : ''}`}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      <div className="page">
        <Card className="gl afu d1" style={{ padding: 34, marginBottom: 18 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(280px, .8fr)', gap: 24, alignItems: 'center' }}>
            <div>
              <Chip name="Role readiness, not generic advice" level="v" style={{ marginBottom: 16 }} />
              <h1 className="serif" style={{ fontSize: 42, lineHeight: 1.08, margin: '0 0 14px', color: 'var(--t1)' }}>
                Find out if you are ready before 200 applications do.
              </h1>
              <p style={{ color: 'var(--t2)', fontSize: 15.5, lineHeight: 1.65, maxWidth: 680, margin: '0 0 22px' }}>
                Upload your resume, paste real job descriptions, and Bridgr gives a traceable verdict:
                screening readiness, interview readiness, job readiness, exact gaps, and your next 14 days.
              </p>
              <Button onClick={() => setCurrentPage('resume')} style={{ padding: '13px 22px' }}>
                <Icon name="file" s={16} c="white" />
                Get Readiness Report
              </Button>
            </div>

            <Card style={{ padding: 22, background: 'rgba(255,255,255,.035)' }}>
              <div style={{ fontSize: 13, color: 'var(--t3)', marginBottom: 14 }}>
                Current report
              </div>
              {hasReport ? (
                <>
                  {[
                    ['Screen', screenScore],
                    ['Interview', interviewScore],
                    ['Job', jobScore],
                  ].map(([label, score]) => (
                    <div key={label} style={{ marginBottom: 14 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 13 }}>
                        <span style={{ color: 'var(--t2)' }}>{label}</span>
                        <strong style={{ color: 'var(--t1)' }}>{score}%</strong>
                      </div>
                      <ProgressBar value={score} />
                    </div>
                  ))}
                  <Chip name={analysisData?.verdict || 'Report ready'} level="learn" />
                </>
              ) : (
                <div style={{ color: 'var(--t2)', fontSize: 14, lineHeight: 1.55 }}>
                  No readiness report yet. Your first report becomes the baseline for every future re-score.
                </div>
              )}
            </Card>
          </div>
        </Card>

        <div className="b3" style={{ marginBottom: 18 }}>
          {steps.map((step, index) => (
            <Card key={step.title} className="gl" style={{ padding: 22 }}>
              <div style={{ width: 34, height: 34, borderRadius: 9, background: 'rgba(139,92,246,.14)', color: 'var(--p3)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14, fontWeight: 700 }}>
                {index + 1}
              </div>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 8 }}>
                {step.title}
              </div>
              <div style={{ fontSize: 13, color: 'var(--t2)', lineHeight: 1.55 }}>
                {step.body}
              </div>
            </Card>
          ))}
        </div>

        <Card className="gl" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: 15, fontWeight: 650, color: 'var(--t1)', marginBottom: 6 }}>
                MVP scope is intentionally narrow
              </div>
              <div style={{ fontSize: 13, color: 'var(--t2)' }}>
                No chat, fake market pulse, salary guesses, interview module, or long generic roadmap. The report is the product.
              </div>
            </div>
            <Button variant="secondary" onClick={() => setCurrentPage('resume')}>
              Start Report
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
