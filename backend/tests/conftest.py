"""
Pytest fixtures for the test suite.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock


@pytest.fixture
def sample_resume_dict():
    """Sample resume data as parsed dictionary."""
    return {
        "sections": {
            "skills": ["Python", "SQL", "Machine Learning", "Docker"],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "start_date": "2021-01",
                    "end_date": "Present",
                    "bullets": [
                        "Developed machine learning models using Python and scikit-learn",
                        "Led deployment of containerized services on AWS EKS",
                        "Managed team of 5 engineers across multiple projects"
                    ]
                },
                {
                    "title": "Software Developer",
                    "company": "StartupCo", 
                    "start_date": "2019-06",
                    "end_date": "2020-12",
                    "bullets": [
                        "Built REST APIs using Python Flask",
                        "Assisted with SQL database optimization"
                    ]
                }
            ],
            "projects": [
                {
                    "name": "Personal Portfolio Website",
                    "description": "Built responsive website using React and deployed on Vercel"
                }
            ]
        },
        "total_yoe": 30  # months
    }


@pytest.fixture
def sample_postings():
    """Sample job posting requirements."""
    return [
        {
            "title": "Senior ML Engineer",
            "requirements": [
                "3+ years Python experience",
                "Machine learning model deployment", 
                "Docker containerization",
                "Leadership experience preferred"
            ]
        }
    ]


@pytest.fixture
def mock_core():
    """Mock IntelligenceCore for testing without ML dependencies."""
    mock = MagicMock()
    
    # Mock skill extraction
    mock.extract_skills_from_resume.return_value = [
        {"skill": "python", "evidence_level": 3, "months_since_used": 6},
        {"skill": "machine_learning", "evidence_level": 2, "months_since_used": 12},
        {"skill": "docker", "evidence_level": 3, "months_since_used": 3}
    ]
    
    # Mock requirements extraction
    mock.extract_requirements_from_postings.return_value = [
        {
            "skill": "python", 
            "required_level": 3,
            "criticality": 1.0,
            "frequency": 1.0,
            "is_blocker": False
        },
        {
            "skill": "machine_learning",
            "required_level": 3, 
            "criticality": 0.9,
            "frequency": 0.8,
            "is_blocker": False
        },
        {
            "skill": "docker",
            "required_level": 2,
            "criticality": 0.7,
            "frequency": 0.6, 
            "is_blocker": False
        }
    ]
    
    return mock


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF file bytes for testing file validation."""
    # Real PDF magic bytes header + minimal content
    pdf_header = b"%PDF-1.4\n"
    pdf_body = b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    pdf_footer = b"xref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\n%%EOF"
    return pdf_header + pdf_body + pdf_footer