# Manual Verification Checklist — Phase 5

**Purpose**: Verify that dashboard implementation matches Phase 5 requirements  
**Date**: Phase 5 Verification  
**Verifier**: QA/Development Team  

---

## 1. Dashboard UI Verification

### 1.1 App Home Page (app.py)

**Check**: Hero section displays "5 IT Carreras" label

Steps:
1. Start dashboard: `streamlit run src/dashboard/app.py`
2. Navigate to home page (default route)
3. Look for hero section with metrics card

Expected:
- [ ] Card shows: "✅ Carreras IT Detectadas: 5"
- [ ] Card displays list of 5 IT careers in tooltip
- [ ] Card shows: "✅ Estudiantes Cargados: [count]" (formatted with commas)
- [ ] Card shows: "📊 Cobertura de Salarios: [percentage]%"
- [ ] Card shows: "🔄 Última Actualización: [timestamp YYYY-MM-DD HH:MM]"

---

### 1.2 KPIs Page (01_kpis.py)

**Check**: Success badge shows IT career validation

Steps:
1. Navigate to "KPIs" page in sidebar
2. Look at top of page

Expected:
- [ ] Green success badge displays: "✅ 5 IT Carreras | [count] Egresados Analizados | Cobertura de salarios: [%]%"
- [ ] Below badge: "Período de análisis: 2024-2028" (or similar year range)
- [ ] All KPI metrics visible: tasa de empleo, % en área, salario promedio
- [ ] No validation errors displayed (or only info-level warnings)

---

### 1.3 Employment Insertion Page (02_insercion.py)

**Check**: Career filter info + temporal analysis explanation

Steps:
1. Navigate to "Inserción Laboral" page
2. Look at top sections

Expected:
- [ ] Shows: "✅ Showing: Ingeniería de Sistemas, Software, Data, Telecomunicaciones, Ciberseguridad"
- [ ] Shows: "📅 Análisis temporal: Muestra la línea de tiempo graduación→empleo (cohortes 2024-2028)"
- [ ] Sample size badge shows color indicator (green/orange/blue depending on count)
- [ ] Temporal evolution chart visible (X-axis should be graduation year, not entry year)

---

### 1.4 Skill Gap Page (03_skill_gap.py)

**Check**: Skill coverage shows realistic percentages (not 0/100 binary)

Steps:
1. Navigate to "Brecha de Habilidades" page
2. Look at skill gap visualization

Expected:
- [ ] Multiple skills displayed with coverage percentages
- [ ] Coverage values include range like 25%, 45%, 60%, 80% (realistic variation)
- [ ] NOT just 0% and 100% values
- [ ] Note mentions: "Usa fuzzy matching (umbral 0.80) para detectar habilidades"
- [ ] Skill similarity scores visible (0.0-1.0 range)

---

### 1.5 Chatbot Page (04_chatbot.py)

**Check**: Chatbot context mentions IT careers scope

Steps:
1. Navigate to "Chatbot" page
2. Send test message: "What are the IT careers in this analysis?"

Expected:
- [ ] Bot response mentions 5 IT careers
- [ ] Bot response indicates IT focus (not general university data)
- [ ] Context in response clearly states scope limitation

---

## 2. Data Integrity Verification

### 2.1 Career Filtering

**Check**: Only 5 IT careers in data

Steps:
1. Open Python REPL or Jupyter notebook in project directory
2. Run:
   ```python
   from src.dashboard.components.data_loader import load_df
   df = load_df()
   print("Unique careers:", df['NombreCarrera'].unique())
   print("Career count:", df['NombreCarrera'].nunique())
   ```

Expected:
- [ ] Exactly 5 unique careers displayed
- [ ] All careers are in: `['Ingeniería de Sistemas', 'Ingeniería de Software', 'Ciencia de Datos', 'Telecomunicaciones y Redes', 'Ciberseguridad']`
- [ ] No non-IT careers (Diseño Gráfico, Derecho, etc.)

---

### 2.2 Skill Gap Coverage Realism

**Check**: Coverage percentages are realistic (not binary 0/100)

Steps:
1. Run:
   ```python
   from src.dashboard.components.data_loader import get_skill_gap
   sg = get_skill_gap()
   print(sg[['habilidad', 'cobertura_%']].head(10))
   print("Coverage range:", sg['cobertura_%'].min(), "-", sg['cobertura_%'].max())
   ```

Expected:
- [ ] Coverage values span realistic range (e.g., 20-95%)
- [ ] NOT all values 0 or 100
- [ ] Multiple intermediate values (30%, 45%, 60%, etc.)
- [ ] Similarity scores visible and in 0.0-1.0 range

---

### 2.3 Temporal Analysis Uses graduation_year

**Check**: Groupby column is graduation_year, not entry year

Steps:
1. Run:
   ```python
   from src.dashboard.components.data_loader import get_empleo_temporal
   et = get_empleo_temporal()
   print("Temporal data:")
   print(et[['anio', 'tasa_empleo']].head(10))
   print("\nGrouping column explanation:")
   print("'anio' should represent graduation cohorts, not entry cohorts")
   ```

Expected:
- [ ] 'anio' column contains graduation years
- [ ] Years span appropriate range for graduation cohorts (4+ years typically)
- [ ] Employment rates show realistic variation across cohorts
- [ ] If data shows employment by graduation year, confirms correct grouping

---

## 3. Error Handling Verification

### 3.1 Data Quality Errors Visible

**Check**: Validation errors displayed properly

Steps:
1. Navigate through all dashboard pages
2. Look for error/warning indicators

Expected:
- [ ] If salary coverage < 50%: See ⚠️ warning in KPI page
- [ ] If graduation year estimated: See ℹ️ info note in Inserción page
- [ ] No silent failures (all data quality issues visible to user)
- [ ] Error messages are in Spanish and user-friendly

---

### 3.2 Error Tracking in Data

**Check**: Functions return _errors key

Steps:
1. Run:
   ```python
   from src.dashboard.components.data_loader import get_kpis, get_skill_gap
   kpis = get_kpis()
   print("KPI errors:", kpis.get('_errors', []))
   
   sg = get_skill_gap()
   if '_errors' in sg.columns:
       print("Skill gap errors:", sg['_errors'].iloc[0])
   ```

Expected:
- [ ] `get_kpis()` returns dict with '_errors' key (list)
- [ ] `get_skill_gap()` includes '_errors' column or key
- [ ] Errors populated during validation steps
- [ ] Empty list [] if no validation issues

---

## 4. Test Execution Verification

### 4.1 Unit Tests Pass

**Check**: All data validation unit tests pass

Steps:
1. Run:
   ```bash
   cd /path/to/project
   pytest tests/dashboard/test_data_validation.py -v
   ```

Expected:
- [ ] All TestValidateCareers tests pass (6+ tests)
- [ ] All TestValidateGraduationYear tests pass (5+ tests)
- [ ] All TestValidateSalaryData tests pass (5+ tests)
- [ ] All TestFuzzyMatchSkill tests pass (8+ tests)
- [ ] All TestDataValidationIntegration tests pass (1+ tests)
- [ ] **Total**: 25+ unit tests passing

---

### 4.2 Integration Tests Pass

**Check**: End-to-end integration tests pass

Steps:
1. Run:
   ```bash
   pytest tests/dashboard/test_integration.py -v
   ```

Expected:
- [ ] All TestLoadDfIntegration tests pass
- [ ] All TestGetKpisIntegration tests pass (5+ tests)
- [ ] All TestGetSkillGapIntegration tests pass (5+ tests)
- [ ] All TestGetEmpleoTemporalIntegration tests pass (4+ tests)
- [ ] All TestDataFlowConsistency tests pass (2+ tests)
- [ ] **Total**: 16+ integration tests passing

---

## 5. Documentation Verification

### 5.1 README Updated

**Check**: README explains IT alignment scope

Steps:
1. Open `README.md` and `README.es.md`
2. Look for sections about:
   - IT career focus
   - Skill gap methodology (fuzzy matching)
   - Temporal analysis (graduation year)

Expected:
- [ ] Section explaining 5 IT careers scope
- [ ] Documentation of CSV-only data flow (no SQL Server required)
- [ ] Explanation of fuzzy matching threshold (0.80)
- [ ] Note about graduation year vs entry year analysis
- [ ] Data attribution clear (sources: CSV, SQL Server optional)

---

### 5.2 Design Document Updated

**Check**: Design notes reflect implementation

Steps:
1. Review `design.md`
2. Check if implementation matches architecture decisions

Expected:
- [ ] All Phase 5 implementation items documented
- [ ] Technical approach section clear
- [ ] File changes section matches actual code
- [ ] Architecture decisions aligned with implementation

---

## 6. Specification Compliance Verification

### 6.1 Requirement: Show Only 5 IT Careers

**Verification**:
```python
from src.dashboard.components.data_loader import load_df, IT_CAREERS
df = load_df()
unique_careers = df['NombreCarrera'].unique().tolist()
assert len(unique_careers) <= 5
assert all(c in IT_CAREERS for c in unique_careers)
```

- [ ] ✅ Requirement met: Only IT careers in data
- [ ] Evidence: Unique careers match IT_CAREERS constant

---

### 6.2 Requirement: Fuzzy Matching for Skills

**Verification**:
```python
from src.dashboard.components.data_loader import get_skill_gap
sg = get_skill_gap()
coverage = sg['cobertura_%'].dropna().unique()
print(f"Coverage range: {coverage.min()}-{coverage.max()}%")
assert coverage.max() < 100 or coverage.min() > 0  # Not all binary
```

- [ ] ✅ Requirement met: Coverage % in 0-100 range (realistic, not binary)
- [ ] Evidence: Multiple coverage values, fuzzy matching producing realistic scores

---

### 6.3 Requirement: Temporal Analysis Uses Graduation Year

**Verification**:
```python
from src.dashboard.components.data_loader import get_empleo_temporal
et = get_empleo_temporal()
# Should group by graduation_year, creating cohort-based analysis
assert len(et) > 0
assert 'anio' in et.columns
```

- [ ] ✅ Requirement met: Groupby column is graduation_year
- [ ] Evidence: Employment rates grouped by graduation cohort

---

### 6.4 Requirement: Error Handling Visible

**Verification**:
```python
from src.dashboard.components.data_loader import get_kpis
kpis = get_kpis()
if kpis['_errors']:
    print(f"Errors found: {kpis['_errors']}")
    # Navigate to dashboard to see error display
```

- [ ] ✅ Requirement met: Errors returned and displayed in UI
- [ ] Evidence: `_errors` key populated, shown in st.error/st.warning calls

---

### 6.5 Requirement: Data Attribution Clear

**Verification**:
- [ ] ✅ Dashboard app.py hero shows data source info
- [ ] ✅ README documents CSV-only fallback
- [ ] ✅ Error messages indicate if using CSV vs SQL Server
- [ ] Evidence: Source attribution visible to users

---

## 7. Sign-Off

| Item | Status | Notes |
|------|--------|-------|
| Unit Tests Pass | [ ] | 25+ tests |
| Integration Tests Pass | [ ] | 16+ tests |
| UI Verification Complete | [ ] | All 5 pages checked |
| Data Integrity Verified | [ ] | Careers, skills, temporal |
| Error Handling Works | [ ] | Visible & tracked |
| Documentation Updated | [ ] | README & design.md |
| Spec Requirements Met | [ ] | All 5 requirements |

**Verification Date**: ___________  
**Verified By**: ___________  
**Status**: [ ] PASS [ ] FAIL  

---

**Notes / Issues Found**:
(Space for documenting any issues or edge cases found during verification)

