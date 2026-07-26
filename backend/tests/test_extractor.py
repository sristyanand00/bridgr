"""
Tests for skill extraction logic.

These tests focus on testable components without requiring full ML model setup.
"""

import pytest
from core_ml.extractor import STOP_SKILLS


pytestmark = pytest.mark.requires_ml


class TestSkillExtractor:
    
    def test_stop_word_filtering(self):
        """Test that stop words are properly defined and filtered."""
        # Test that common stop words are in STOP_SKILLS
        assert "work" in STOP_SKILLS
        assert "experience" in STOP_SKILLS  
        assert "skills" in STOP_SKILLS
        assert "management" in STOP_SKILLS
        assert "using" in STOP_SKILLS
        assert "with" in STOP_SKILLS
        
        # Test that actual skills are NOT in stop words
        assert "python" not in STOP_SKILLS
        assert "java" not in STOP_SKILLS
        assert "sql" not in STOP_SKILLS

    def test_stop_skills_constant_structure(self):
        """Test that STOP_SKILLS constant is properly defined."""
        assert isinstance(STOP_SKILLS, set)
        assert len(STOP_SKILLS) > 10  # Should have many stop words
        assert all(isinstance(word, str) for word in STOP_SKILLS)
        assert all(word.lower() == word for word in STOP_SKILLS)  # Should be lowercase

    def test_stop_skills_includes_common_words(self):
        """Test that STOP_SKILLS includes expected common words."""
        expected_stop_words = {
            "work", "use", "ability", "using", "used", "strong",
            "experience", "skills", "knowledge", "understanding", 
            "management", "team", "working", "the", "and", "with", "for"
        }
        
        # All expected stop words should be present
        for word in expected_stop_words:
            assert word in STOP_SKILLS, f"'{word}' should be in STOP_SKILLS"

    def test_skill_list_filtering_logic(self):
        """Test the skill filtering logic without initializing SkillExtractor."""
        # Simulate the filtering logic used in SkillExtractor.__init__
        test_skill_list = ["python", "work", "java", "experience", "sql", "skills", "docker"]
        
        filtered_skills = [s for s in test_skill_list if s.lower() not in STOP_SKILLS]
        
        # Should keep actual skills
        assert "python" in filtered_skills
        assert "java" in filtered_skills  
        assert "sql" in filtered_skills
        assert "docker" in filtered_skills
        
        # Should filter out stop words
        assert "work" not in filtered_skills
        assert "experience" not in filtered_skills
        assert "skills" not in filtered_skills