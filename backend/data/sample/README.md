# O*NET 50-Occupation Sample

This directory contains a minimal sample of O*NET skill data for 50 common
tech occupations. It lets the app run in full mode immediately after cloning,
without downloading the full 50MB dataset.

To unlock all 1,000+ occupations, run:

    python scripts/setup_data.py

Then set `ONET_EXTRACT_PATH` in `backend/.env` to point at the extracted directory.

## Occupations included

The sample covers the 50 most-requested roles in the readiness scorer:

Software Developer, Data Scientist, Data Analyst, Machine Learning Engineer,
DevOps Engineer, Cloud Engineer, Frontend Developer, Backend Developer,
Full Stack Developer, Data Engineer, NLP Engineer, Android Developer,
iOS Developer, QA Engineer, Security Engineer, Database Administrator,
Systems Architect, Product Manager, Scrum Master, Business Analyst,
IT Manager, Network Engineer, Embedded Systems Engineer, Site Reliability Engineer,
Blockchain Developer, Computer Vision Engineer, MLOps Engineer,
Cybersecurity Analyst, IT Support Specialist, Technical Writer,
Game Developer, AR/VR Developer, Robotics Engineer, Quantitative Analyst,
BI Developer, Salesforce Developer, SAP Consultant, ERP Specialist,
Cloud Architect, Solutions Architect, Platform Engineer, Infrastructure Engineer,
Research Scientist, AI Researcher, Data Governance Analyst, ETL Developer,
Streaming Engineer, Search Engineer, Recommendation Systems Engineer,
Computer Graphics Engineer.
