"""
Tests — Dashboard Data Validation Functions (Phase 5)

Unit tests for data validation functions in data_loader.py:
- _validate_careers()
- _validate_graduation_year()
- _validate_salary_data()
- _fuzzy_match_skill()

Each function tested with:
- Happy path (normal expected behavior)
- Edge cases (boundary conditions)
- Error cases (exceptional inputs)
"""

import sys
import os
import pandas as pd
import numpy as np
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from dashboard.components.data_loader import (
    _validate_careers,
    _validate_graduation_year,
    _validate_salary_data,
    _fuzzy_match_skill,
    IT_CAREERS
)


class TestValidateCareers:
    """Test _validate_careers() function - IT career filtering"""
    
    def test_happy_path_filters_to_it_careers(self):
        """Happy path: DataFrame with mixed careers → filtered to IT only"""
        data = {
            'EstudianteID': [1, 2, 3, 4, 5, 6],
            'NombreCarrera': [
                'Ingeniería de Sistemas',
                'Ingeniería de Software',
                'Diseño Gráfico',
                'Ciencia de Datos',
                'Derecho',
                'Telecomunicaciones y Redes'
            ],
            'SalarioMensualUSD': [2500, 2800, 1500, 3000, 1200, 2700]
        }
        df = pd.DataFrame(data)
        
        df_filtered, errors = _validate_careers(df)
        
        assert len(df_filtered) == 4, "Should filter to 4 IT careers"
        assert all(c in IT_CAREERS for c in df_filtered['NombreCarrera'].unique()), \
            "All careers should be in IT_CAREERS list"
        assert len(errors) == 0, "Should not have errors for valid IT careers"
    
    def test_edge_case_all_it_careers(self):
        """Edge case: All rows are IT careers → no filtering needed"""
        data = {
            'EstudianteID': [1, 2, 3, 4, 5],
            'NombreCarrera': [
                'Ingeniería de Sistemas',
                'Ingeniería de Software',
                'Ciencia de Datos',
                'Ciberseguridad',
                'Telecomunicaciones y Redes'
            ]
        }
        df = pd.DataFrame(data)
        
        df_filtered, errors = _validate_careers(df)
        
        assert len(df_filtered) == 5, "All IT rows should pass"
        assert len(errors) == 0, "No errors for all-IT data"
    
    def test_error_case_empty_dataframe(self):
        """Error case: Empty DataFrame → should error gracefully"""
        df = pd.DataFrame(columns=['EstudianteID', 'NombreCarrera'])
        
        df_filtered, errors = _validate_careers(df)
        
        assert len(df_filtered) == 0, "Empty input → empty output"
        assert len(errors) > 0, "Should have error message"
    
    def test_error_case_no_it_careers_found(self):
        """Error case: No IT careers in data → should error"""
        data = {
            'EstudianteID': [1, 2, 3],
            'NombreCarrera': ['Derecho', 'Diseño Gráfico', 'Administración']
        }
        df = pd.DataFrame(data)
        
        df_filtered, errors = _validate_careers(df)
        
        assert len(df_filtered) == 0, "No IT careers → empty output"
        assert len(errors) > 0, "Should have error"


class TestValidateGraduationYear:
    """Test _validate_graduation_year() function - graduation date estimation"""
    
    def test_happy_path_semester_8_present(self):
        """Happy path: SemestreActual=8 → use anio_y directly"""
        data = {
            'anio_y': [2022, 2022, 2022],
            'SemestreActual': [8, 8, 8]
        }
        df = pd.DataFrame(data)
        
        grad_year = _validate_graduation_year(df)
        
        assert grad_year.iloc[0] == 2022, "Graduated (sem 8) → year stays 2022"
        assert grad_year.iloc[1] == 2022
        assert grad_year.iloc[2] == 2022
    
    def test_happy_path_semester_less_than_8(self):
        """Happy path: SemestreActual < 8 → estimate graduation year"""
        data = {
            'anio_y': [2022, 2022, 2022],
            'SemestreActual': [6, 4, 2]
        }
        df = pd.DataFrame(data)
        
        grad_year = _validate_graduation_year(df)
        
        assert grad_year.iloc[0] == 2023, "sem 6 + 1 year = 2023"
        assert grad_year.iloc[1] == 2024, "sem 4 + 2 years = 2024"
        assert grad_year.iloc[2] == 2025, "sem 2 + 3 years = 2025"
    
    def test_edge_case_missing_semester_column(self):
        """Edge case: SemestreActual missing → fallback to anio_y + 4"""
        data = {
            'anio_y': [2022, 2023]
        }
        df = pd.DataFrame(data)
        
        grad_year = _validate_graduation_year(df)
        
        assert grad_year.iloc[0] == 2026, "No semester → anio_y + 4"
        assert grad_year.iloc[1] == 2027
    
    def test_error_case_null_semester(self):
        """Error case: NaN semester values → should handle gracefully"""
        data = {
            'anio_y': [2022, 2022, 2022],
            'SemestreActual': [8, np.nan, 4]
        }
        df = pd.DataFrame(data)
        
        grad_year = _validate_graduation_year(df)
        
        assert grad_year.iloc[0] == 2022, "sem 8 normal"
        assert grad_year.iloc[1] == 2026, "NaN → treated as 0, add max 4 years"
        assert grad_year.iloc[2] == 2024, "sem 4 normal"


class TestValidateSalaryData:
    """Test _validate_salary_data() function - salary coverage detection"""
    
    def test_happy_path_100_percent_coverage(self):
        """Happy path: 100% salary data → no warnings"""
        data = {
            'SalarioMensualUSD': [2500, 2800, 3000, 2700, 3200]
        }
        df = pd.DataFrame(data)
        
        errors = _validate_salary_data(df)
        
        assert len(errors) == 0, "100% coverage → no warnings"
    
    def test_edge_case_75_percent_coverage(self):
        """Edge case: 75% coverage (50-80 range) → info warning"""
        data = {
            'SalarioMensualUSD': [2500, 2800, 3000, np.nan]
        }
        df = pd.DataFrame(data)
        
        errors = _validate_salary_data(df)
        
        assert len(errors) > 0, "Should have info message"
        assert "ℹ️" in errors[0], "Should be info"
    
    def test_error_case_30_percent_coverage(self):
        """Error case: 30% coverage (< 50%) → warning about bias"""
        data = {
            'SalarioMensualUSD': [2500, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        }
        df = pd.DataFrame(data)
        
        errors = _validate_salary_data(df)
        
        assert len(errors) > 0, "Should warn about low coverage"
        assert "⚠️" in errors[0], "Should be warning"
    
    def test_error_case_missing_salary_column(self):
        """Error case: SalarioMensualUSD column missing → error"""
        data = {
            'OtherColumn': [1, 2, 3]
        }
        df = pd.DataFrame(data)
        
        errors = _validate_salary_data(df)
        
        assert len(errors) > 0, "Should error if column missing"


class TestFuzzyMatchSkill:
    """Test _fuzzy_match_skill() function - semantic skill matching"""
    
    def test_happy_path_exact_match(self):
        """Happy path: Exact skill match → score 1.0"""
        score = _fuzzy_match_skill("Python", ["Python", "Java", "C++"])
        
        assert score == 1.0, "Exact match → 1.0"
    
    def test_happy_path_near_exact_match(self):
        """Happy path: Very close match (e.g., Python vs python)"""
        score = _fuzzy_match_skill("Python", ["python", "Java"])
        
        # Case-normalized, should match
        assert score == 1.0, "Case-insensitive should match exactly"
    
    def test_error_case_empty_academic_skills(self):
        """Error case: Empty academic skills list → 0.0"""
        score = _fuzzy_match_skill("Python", [])
        
        assert score == 0.0, "Empty academic skills → 0.0"
    
    def test_error_case_well_below_threshold(self):
        """Error case: Completely different skills → 0.0"""
        score = _fuzzy_match_skill("Python", ["Photography", "Graphic Design", "Music"])
        
        assert score == 0.0, "Completely different skills → 0.0"
    
    def test_edge_case_case_insensitive(self):
        """Edge case: Matching should be case-insensitive"""
        score_lower = _fuzzy_match_skill("python", ["Python"])
        score_upper = _fuzzy_match_skill("PYTHON", ["python"])
        
        assert score_lower == 1.0, "Lowercase should match uppercase"
        assert score_upper == 1.0, "Uppercase should match lowercase"
    
    def test_edge_case_whitespace_tolerance(self):
        """Edge case: Matching should handle extra whitespace"""
        score = _fuzzy_match_skill("  Python  ", ["Python"])
        
        assert score == 1.0, "Should handle extra whitespace"
    
    def test_edge_case_returns_0_or_score(self):
        """Edge case: Returns either 0.0 or similarity score > threshold"""
        scores = [
            _fuzzy_match_skill("test", ["test"]),
            _fuzzy_match_skill("test", ["xyz"]),
            _fuzzy_match_skill("Python", ["Python", "JavaScript"]),
            _fuzzy_match_skill("unrelated", ["completely", "different"])
        ]
        
        # All scores should be valid (0.0-1.0) and reflect threshold logic
        assert all(0.0 <= s <= 1.0 for s in scores), "All scores in valid range"
        assert scores[0] == 1.0, "Exact match"
        assert scores[1] == 0.0, "No match"


class TestDataValidationIntegration:
    """Integration tests combining validation functions"""
    
    def test_full_validation_pipeline(self):
        """Integration: Full pipeline - careers, graduation year, salary validation"""
        data = {
            'EstudianteID': [1, 2, 3, 4, 5, 6],
            'NombreCarrera': [
                'Ingeniería de Sistemas',
                'Ciencia de Datos',
                'Ingeniería de Software',
                'Diseño Gráfico',
                'Telecomunicaciones y Redes',
                'Ciberseguridad'
            ],
            'anio_y': [2020, 2020, 2020, 2020, 2020, 2020],
            'SemestreActual': [8, 7, 6, 5, 8, 6],
            'SalarioMensualUSD': [2500, np.nan, 2800, 1500, 3000, 2700]
        }
        df = pd.DataFrame(data)
        
        # Step 1: Filter careers
        df_filtered, career_errors = _validate_careers(df)
        assert len(df_filtered) == 5, "Non-IT should be filtered out"
        
        # Step 2: Validate graduation years
        grad_year = _validate_graduation_year(df_filtered)
        assert len(grad_year) == 5, "Should have grad year for all rows"
        assert all(g >= 2020 for g in grad_year), "All grad years reasonable"
        
        # Step 3: Validate salary data
        salary_errors = _validate_salary_data(df_filtered)
        assert len(salary_errors) == 0 or "ℹ️" in salary_errors[0], "Should be info or no error"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
