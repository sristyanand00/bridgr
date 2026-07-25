# Evidence Level Annotation Guide

**Date**: July 25, 2026  
**Annotator**: [TO BE FILLED IN]

## Evidence Level Definitions

### Level 0: Absent
- The skill is not mentioned anywhere in the resume
- No evidence of any exposure to this technology or skill

### Level 1: Claimed  
- Skill appears only in skills/summary section without context
- Listed in "Technologies:", "Skills:", or similar sections
- No evidence of actual application or use

**Examples:**
- "Skills: Python, Java, SQL, Docker"
- "Technologies: React, Node.js, MongoDB" 
- "Proficient in: Machine Learning, Data Science"

### Level 2: Exposed
- Skill mentioned in project context OR
- Weak action verbs used OR  
- Less than 6 months professional experience

**Examples:**
- "Personal project using React and Node.js"
- "Assisted with Python script development" 
- "Helped implement SQL queries"
- "Supported team with Docker deployments"
- "Junior developer (3 months) - Python development"

### Level 3: Applied
- Professional experience AND
- Strong action verbs AND
- 6+ months tenure

**Examples:**
- "Developed REST APIs using Python Flask (18 months)"
- "Built responsive web applications with React"
- "Implemented database schemas using PostgreSQL"
- "Deployed microservices on AWS EKS"

### Level 4: Owned
- Level 3 conditions PLUS one of:
  - Leadership verb (led, architected, owned, designed, drove)
  - Scope marker (team size, user counts, data volume, SLA)  
  - 24+ months experience

**Examples:**
- "Led migration of legacy system to microservices architecture"
- "Designed scalable Python backend serving 1M+ daily users"
- "Architected React application used by 50+ internal teams"
- "Senior Python developer (30 months) - owned payment processing system"
- "Managed team of 5 engineers building ML pipeline"

## Ambiguous Cases Rules

### Multiple Mentions
- Take the **highest** level across all mentions
- If skill appears in both skills section (level 1) and experience (level 3), assign level 3

### Unclear Tenure
- If dates are vague ("2021-Present", "Recent experience"), ask for clarification
- Default to 12 months if reasonable range is 6-24 months

### Technology Variants  
- Treat variations as the same skill: "React" = "React.js" = "ReactJS"
- "Python" includes "Python 3", "Python scripting", etc.

### Educational vs Professional
- University/bootcamp projects count as Level 2 (exposed)
- Internships count as professional experience if 3+ months

## Worked Examples Per Level

### Level 1 Examples:
1. **Resume Text**: "Technical Skills: Python, JavaScript, SQL, Git, Linux"
   **Skill**: Python
   **Level**: 1 (appears only in skills section)

2. **Resume Text**: "Proficient in machine learning frameworks including TensorFlow and PyTorch"  
   **Skill**: TensorFlow
   **Level**: 1 (claimed proficiency without application context)

3. **Resume Text**: "Summary: Experienced software engineer with knowledge of React, Node.js, and cloud technologies"
   **Skill**: React
   **Level**: 1 (mentioned in summary without concrete evidence)

### Level 2 Examples:
1. **Resume Text**: "Personal Projects: Built a todo application using React and Express.js"
   **Skill**: React  
   **Level**: 2 (project context but not professional)

2. **Resume Text**: "Software Engineer Intern (2 months) - Assisted senior developers with Python automation scripts"
   **Skill**: Python
   **Level**: 2 (short tenure, weak verb)

3. **Resume Text**: "Junior Developer (Jan 2023-Apr 2023) - Helped implement user authentication using JWT tokens"
   **Skill**: JWT/Authentication  
   **Level**: 2 (short tenure, weak verb)

### Level 3 Examples:
1. **Resume Text**: "Software Engineer (12 months) - Developed REST API endpoints using Python Flask framework"
   **Skill**: Python
   **Level**: 3 (professional, strong verb, adequate tenure)

2. **Resume Text**: "Full Stack Developer (18 months) - Built responsive web applications using React and Redux"
   **Skill**: React
   **Level**: 3 (professional, strong verb, good tenure)

3. **Resume Text**: "Data Engineer (2 years) - Implemented ETL pipelines using Apache Spark and Kafka"
   **Skill**: Apache Spark
   **Level**: 3 (professional, strong verb, sufficient tenure)

### Level 4 Examples:
1. **Resume Text**: "Senior Software Engineer (30 months) - Led development of microservices architecture using Docker and Kubernetes"
   **Skill**: Docker
   **Level**: 4 (leadership verb + long tenure)

2. **Resume Text**: "Engineering Manager (2 years) - Architected scalable Python backend serving 2M+ daily requests"
   **Skill**: Python  
   **Level**: 4 (leadership verb + scope marker)

3. **Resume Text**: "Principal Engineer - Designed machine learning platform used by 40+ data scientists across the organization"
   **Skill**: Machine Learning
   **Level**: 4 (leadership verb + scope marker)

---

**Instructions for Use:**
1. Read each resume bullet point carefully
2. Identify all mentioned skills/technologies  
3. For each skill, determine the highest evidence level based on context
4. When in doubt, err on the side of lower level (be conservative)
5. Document reasoning for any level 4 assignments
6. Take breaks every 20 examples to maintain consistency