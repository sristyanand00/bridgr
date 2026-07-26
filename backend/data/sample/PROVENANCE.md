# O*NET Sample Data — Provenance

## Source

This file is a hand-curated extract derived from the
[O*NET Resource Center](https://www.onetcenter.org/) database, which is
produced by the U.S. Department of Labor/Employment and Training Administration
(USDOL/ETA) and made available under the
[O*NET Content Model](https://www.onetcenter.org/content.html).

**Original database:** O*NET 28.2 Database  
**Download page:** <https://www.onetcenter.org/database.html>  
**Files used as reference:** `Occupation Data.txt`, `Skills.txt`, `Technology Skills.txt`

## Licence

O*NET data is in the public domain. From the O*NET Resource Center:

> "O*NET content is available to users at no cost and may be used for
> research, development, and other applications consistent with the purposes
> for which O*NET was developed."

No restrictions apply to commercial or derivative use. Attribution to
USDOL/ETA is customary.

## What is in this sample

`occupations.csv` contains **50 occupations** selected to give broad coverage
of tech-adjacent roles that are common targets for Bridgr users.

### Selection criteria

1. **High query volume** — occupations most frequently searched on
   job boards by early-career and career-switching candidates.
2. **Tech adjacency** — roles with a meaningful technology skill component
   so the skill extractor has signal to work with.
3. **SOC diversity** — at least one occupation from each of the major SOC
   groups (11–53) that plausibly involves computer use.
4. **Modern additions** — SOC codes in the 15-1299.xx range (not yet in the
   official O*NET tabular files) have been added manually to cover roles
   such as Data Engineer, ML Engineer, DevOps Engineer, Site Reliability
   Engineer, and Cloud Engineer, which are underrepresented in the 2019
   SOC taxonomy.

### Columns

| Column | Description |
|--------|-------------|
| `soc_code` | Standard Occupational Classification code |
| `title` | O*NET occupation title (or close approximation for 15-1299.xx) |
| `tech_skills` | Comma-separated technology skills drawn from `Technology Skills.txt` and curated additions |
| `soft_skills` | Comma-separated soft skills with `Scale ID = IM` and `Data Value > 3.0` |

## Limitations

- Skills are simplified and normalised to lowercase, single-token or
  hyphenated names for compatibility with the skill extractor.
- Salary and demand data are **not** included; use the full O*NET extract
  for that.
- For full coverage (1,000+ occupations) run:

```bash
python scripts/setup_data.py
```

Then set `ONET_EXTRACT_PATH` in `backend/.env` to the extracted folder.
