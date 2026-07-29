# Rater Instructions — Pairwise Readiness Study

**Purpose:** Compare pairs of candidates to determine which is MORE ready for their target role.

**What you'll see:** Two candidates side-by-side, each with:
- A target role (e.g., "Senior Backend Engineer")
- 6-8 resume bullets summarizing their experience

**Your task:** For each pair, answer: **"Which candidate is MORE ready for their target role?"**

---

## How to Rate

Run the rating tool:
```bash
cd evals/human_study
python rate.py --rater <your_name>
```

For each pair you'll see Candidate A and Candidate B displayed side-by-side.

### Choices:
- **A** — Candidate A is more ready
- **B** — Candidate B is more ready
- **tie** — Both are roughly equally ready (use sparingly — most pairs have a clear winner)
- **skip** — This pair is too difficult to judge (ambiguous bullets, missing key context)

### What "ready" means:
A candidate is MORE ready if they demonstrate:
1. **Direct experience** with the listed job requirements
2. **Sufficient depth** (not just exposure — owned or applied the skills professionally)
3. **Recent usage** (skills used within the last 2-3 years)
4. **Scale or impact** (large user base, team leadership, complex systems)

---

## Rating Guidelines

### DO:
- ✓ Compare candidates **relative to their target role** — a candidate applying for "Senior ML Engineer" needs deeper ML experience than one applying for "Junior Data Analyst"
- ✓ Look for **verbs**: "Led", "built", "architected", "owned" signal deeper experience than "assisted", "helped", "familiar with"
- ✓ Look for **scope markers**: team size, user counts, data volume, SLA numbers (e.g., "serving 2M users", "99.9% uptime", "5-person team")
- ✓ Look for **tenure**: "18 months", "3 years" beats "4-month internship"
- ✓ Prefer **professional** experience over personal projects, bootcamp projects, or university coursework
- ✓ Judge based ONLY on the resume bullets shown — ignore what you'd expect from the role title

### DON'T:
- ✗ Don't judge whether either candidate is "good enough" — just pick who's **more ready** between the two
- ✗ Don't factor in things not in the bullets (age, gender, school name are not shown for this reason)
- ✗ Don't overthink it — your first instinct is usually correct
- ✗ Don't use **tie** as "I'm not sure" — if genuinely unsure, choose **skip** instead

---

## Worked Examples

### Example 1: Clear Winner

**Pair 007**  
**Role**: Backend Software Engineer

| Candidate A | Candidate B |
|-------------|-------------|
| • Led backend API development using Python FastAPI for 28 months | • Skills: Python, SQL, Docker, Kubernetes |
| • Served 500K monthly active users | • Familiar with RESTful APIs |
| • Architected microservices on AWS EKS | • Personal project: built a Flask API |

**Answer: A** — Candidate A has leadership verbs, scope markers (500K users), long tenure (28 months), and professional context. Candidate B lists skills but lacks depth: "familiar with" and "personal project" signal level 1-2 evidence.

---

### Example 2: Close Call (Borderline)

**Pair 012**  
**Role**: Data Analyst

| Candidate A | Candidate B |
|-------------|-------------|
| • Data Analyst (18 months) — built SQL reports | • Senior Analyst (12 months) — created Tableau dashboards |
| • Wrote complex queries (CTEs, window functions) | • Visualised KPIs for 10 product managers |
| • No BI tool experience mentioned | • Limited SQL depth mentioned |

**Answer: Depends on what the job posting emphasises** — but if you had to pick:  
- Choose **A** if the role is SQL-heavy (deeper query skills)
- Choose **B** if the role requires Tableau and stakeholder communication (scope marker: 10 PMs)

If genuinely unsure and the bullets don't make it clear → **skip**.

---

### Example 3: Tie (Rare)

**Pair 019**  
**Role**: ML Engineer

| Candidate A | Candidate B |
|-------------|-------------|
| • Built TensorFlow models in production for 18 months | • Deployed PyTorch models to production for 16 months |
| • Served 2M recommendations/day | • Maintained 99.9% model uptime serving 1.5M users |
| • Owned model retraining pipeline | • Led A/B testing for model improvements |

**Answer: tie** — Both have strong verbs, scope markers, adequate tenure, and leadership signals. The difference is stylistic, not substantial. This is a genuine tie.

---

## FAQ

**Q: What if one candidate has more bullets than the other?**  
A: Judge based on the **highest-quality evidence**, not volume. One strong "Led X for 2 years serving 1M users" beats five "Assisted with Y" bullets.

**Q: What if the bullets are vague or don't match the role?**  
A: If you can't tell who's more ready from the bullets shown → **skip**. Don't guess.

**Q: Should I penalise non-native English phrasing?**  
A: **No.** If the meaning is clear, treat grammatically awkward phrasing the same as fluent phrasing. We're measuring readiness, not writing style.

**Q: How many ties should I use?**  
A: Roughly **5-10%** of pairs. Most pairs have a clear winner. If you're using "tie" more than 20% of the time, you may be overthinking — pick the candidate with stronger evidence even if it's close.

**Q: How long should this take?**  
A: ~20-30 pairs should take 30-45 minutes. If a pair takes longer than 2 minutes → **skip** it and move on.

**Q: Can I change my answers later?**  
A: No — judgements are saved immediately. But overlap pairs (where the same pair appears in reverse order) let us measure your internal consistency, which is useful data.

---

## After Rating

Once you've completed your session:

```bash
# Compute inter-rater agreement (requires ≥2 raters)
python agreement.py

# Fit Bradley-Terry model to convert pairwise wins to a continuous ranking
python bradley_terry.py

# Compare BT ranking to model scores (requires model_scores.json from the scoring API)
python compare.py
```

---

**Thank you for participating!** Your ratings establish the human ceiling for this task — the best any automated system can hope to achieve. Low inter-rater agreement isn't a failure; it's a finding about the difficulty of the problem.
