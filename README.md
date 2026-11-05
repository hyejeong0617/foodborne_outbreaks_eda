# Foodborne Disease Outbreak Analysis

**CDC foodborne outbreak surveillance (1998–2015) · Exploratory Data Analysis · SQL · Entity Normalisation · Streamlit**

[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://cdcfoodborneoutbreakseda.streamlit.app/)
[![Notebook validation](https://github.com/hyejeong0617/foodborne_outbreaks_eda/actions/workflows/validate_outbreak_notebooks.yml/badge.svg)](https://github.com/hyejeong0617/foodborne_outbreaks_eda/actions/workflows/validate_outbreak_notebooks.yml)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

**[Explore the interactive dashboard](https://cdcfoodborneoutbreakseda.streamlit.app/)** · **[Review validated notebooks](https://github.com/hyejeong0617/foodborne_outbreaks_eda/actions/runs/42020479803)** · **[View the data source](https://www.kaggle.com/datasets/cdc/foodborne-diseases)**

## At a glance

**Research question:** What changes when foodborne disease surveillance is viewed through *outbreak frequency*, *illness burden*, and *reported clinical severity* rather than any single ranking?

This project analyses **18,839 distinct outbreak records** in the available CDC FDOSS-derived dataset (1998–2015). It combines pandas-based cleaning, domain-informed grouping of free-text food/pathogen labels, exploratory analysis, SQLite queries, and a four-section Streamlit data story.

The goal is not to predict individual illness or assign causal risk. It is to show how careful data preparation, denominator selection, and appropriate visualisation affect the interpretation of public-health surveillance patterns.

| Portfolio evidence | What the project demonstrates |
|---|---|
| Data integrity | Source-record reconciliation; explicit handling of unknown categories and missing clinical outcomes |
| Scientific analysis | Temporal trends, pathogen burden, food–pathogen associations, and differences across outbreak settings |
| SQL | Aggregation, joins, conditional logic, and window functions in a separate analytical notebook |
| Communication | A focused, interactive Streamlit dashboard with accessible light styling and contextual interpretation |
| Reproducibility | GitHub Actions successfully validates the canonical dataset and executes NB3 and NB4 |

## Explore the dashboard

**[Launch the dashboard](https://cdcfoodborneoutbreakseda.streamlit.app/)**

The final portfolio interface is organised around four questions. The year filter updates the visible metrics and figures; selected secondary analyses are available in expandable sections.

| Section | Question | Visual evidence |
|---|---|---|
| **01 · The big picture** | What do 18 years of reported outbreaks reveal? | Annual outbreak counts; optional monthly seasonality |
| **02 · Pathogen burden** | Which pathogens contribute the greatest reported disease burden? | Ranking by illnesses or hospitalisations; hospitalization ratios for selected pathogens |
| **03 · Food & pathogen links** | Which identified food vehicles and pathogens are reported together? | Food frequency; leading food–pathogen combinations by events or illnesses |
| **04 · Where outbreaks happen** | How does the observed burden differ by venue? | Mean illnesses per outbreak; optional hospitalization ratios by setting |

Rather than crowding each view with every analysis, the dashboard foregrounds one question and a small number of interpretable figures. **The deeper EDA and SQL work remains in the notebooks.**

## Selected findings & interpretation

- **Trend and seasonality:** Reported outbreak counts change considerably across 1998–2015; monthly summaries offer a second view. Changes in reporting do **not**, by themselves, establish changes in individual exposure or incidence.
- **Frequency versus severity:** In the full-period dashboard, **Norovirus** leads the ranking by reported illnesses. Switching to hospitalizations changes the ranking and therefore the public-health question being asked.
- **Food–pathogen combinations:** Grouped foods and pathogens allow repeated reporting patterns to be compared. A frequently reported pair is an *association in surveillance records*, not proof that a particular ingredient caused the outbreak.
- **Setting differences:** Reported outbreak size varies across venues; **Prison/Jail** stands out for average illnesses per event in the full-period view. This descriptive pattern does not establish the reason for that difference.

All rankings are recalculated from the selected data range. The dashboard deliberately avoids fixed historical percentages that can become misleading when definitions or denominators change.

## Data integrity: 2026-11-05 correction

The current canonical file, `data/cleaned_data_grouped.csv`, reflects the latest source-record audit. **Do not use the older 18,828-row figure or treat unreported outcomes as zero.**

| Canonical-data check | Verified value |
|---|---:|
| Distinct source records used for analysis | **18,839** |
| Missing `Hospitalizations` values | **3,560** |
| Missing `Fatalities` values | **3,538** |
| Missing values in `Food_grouped`, `Species_grouped`, `primary_location` | **0** (unknown categories are represented explicitly) |

**Outcome-specific rates:** A hospitalization ratio uses illnesses from events with a recorded hospitalization outcome and a positive illness count; a fatality ratio applies the analogous rule to fatality reporting. Counts that are missing remain `NaN` in the data. These are **descriptive reported-outcome ratios**, not unbiased population estimates of clinical risk. Different degrees of missing reporting may affect comparisons between groups.

Other limitations include unknown/ambiguous food vehicles, surveillance underreporting, unequal reporting practices across years and jurisdictions, free-text categorisation, and the inability to infer causal mechanisms from the observed associations.

## How the analysis was built

1. **Audit and cleaning** — inspect source records, duplicates, missing values, and column types. Preserve distinctions between *unknown*, *missing*, and observed zero.
2. **Entity normalisation** — use RapidFuzz and domain-informed manual mappings to consolidate free-text food and pathogen labels; extract a primary venue label for comparisons. Grouping mixed dishes is an analytical convention, **not confirmation of a contaminated ingredient**.
3. **Exploratory analysis** — examine event counts, disease burden, category rankings, seasonality, and setting-level outcomes in `NB3_EDA.ipynb`.
4. **SQL analysis** — use SQLite for aggregation, derived indicators, joins, conditional categories, and window-function analyses in `NB4_SQL_Analysis.ipynb`.
5. **Communication** — implement the distilled analysis as a four-section, year-filtered Streamlit data story in `dashboard.py`.

### Repository map

| File | Purpose |
|---|---|
| [`data/outbreaks.csv`](data/outbreaks.csv) | CDC-derived raw source |
| [`data/cleaned_data_grouped.csv`](data/cleaned_data_grouped.csv) | Current canonical input to dashboard and validated notebooks |
| [`NB1_Data_Cleaning.ipynb`](NB1_Data_Cleaning.ipynb) | Original cleaning process / historical notebook |
| [`NB2_Entity_Normalisation.ipynb`](NB2_Entity_Normalisation.ipynb) | Original grouping process / historical notebook |
| [`NB3_EDA.ipynb`](NB3_EDA.ipynb) | Current EDA notebook (validated execution) |
| [`NB4_SQL_Analysis.ipynb`](NB4_SQL_Analysis.ipynb) | Current SQL notebook (validated execution) |
| [`dashboard.py`](dashboard.py) | Final four-section Streamlit dashboard |
| [`.streamlit/config.toml`](.streamlit/config.toml) | Light theme |
| [`validate_outbreak_notebooks.yml`](.github/workflows/validate_outbreak_notebooks.yml) | CI dataset assertions and notebook execution |

**Version note:** NB1/NB2 retain historical descriptions/output counts from an earlier cleaning pipeline. The authoritative analysis input is now `data/cleaned_data_grouped.csv`; NB1/NB2 are **not claimed to have been rerun and independently reconciled end-to-end** against the corrected dataset. The 2026-11-05 automated validation specifically covers the canonical file plus NB3 and NB4.

## Reproducibility

On **2026-11-05**, manually triggered [GitHub Actions run #42020479803](https://github.com/hyejeong0617/foodborne_outbreaks_eda/actions/runs/42020479803) completed successfully on `main` at commit [`fd52ccf`](https://github.com/hyejeong0617/foodborne_outbreaks_eda/commit/fd52ccfe4c3aa1fc949cc363361e03562aabf157):

- Asserted **18,839 rows**, **3,560** missing hospitalization outcomes, and **3,538** missing fatality outcomes.
- Successfully executed **NB3 (EDA)** and **NB4 (SQL)** using Python 3.11.
- Uploaded the executed notebook files as an Actions artifact.

This verifies that those notebooks executed successfully against that dataset and commit. It does **not** validate every scientific interpretation, all historical preprocessing notebooks, or interactive browser behaviour. The current dashboard design was updated subsequently and was not part of that notebook workflow.

### Run locally

```bash
git clone https://github.com/hyejeong0617/foodborne_outbreaks_eda.git
cd foodborne_outbreaks_eda
python -m pip install -r requirements.txt
streamlit run dashboard.py
```

For notebook validation, see [the GitHub Actions workflow](.github/workflows/validate_outbreak_notebooks.yml). Results are version-specific; rerun it after changing the underlying data or notebooks.

## Tools and contributions

**Tools:** Python, pandas, NumPy, RapidFuzz, SQLite, SQL, matplotlib, seaborn, Plotly, Streamlit, GitHub Actions.

**My contribution:** research framing, food-safety interpretation, analytical choices about category grouping and denominators, EDA/SQL analysis, dashboard development, and evidence-based documentation. The project connects food microbiology domain knowledge with transparent, reproducible scientific data analysis.

**Data attribution:** CDC foodborne disease outbreak surveillance data distributed through [Kaggle's CDC Foodborne Diseases dataset](https://www.kaggle.com/datasets/cdc/foodborne-diseases). This is a retrospective analysis of historical records, not official CDC advice or a real-time surveillance tool.

## Related work

- [RASFF Risk Predictor](https://github.com/hyejeong0617/rasff_risk_predictor) — regulatory notification analysis and machine learning
- [Aeromonas Growth Predictor](https://github.com/hyejeong0617/aeromonas-growth-predictor) — predictive microbiology and ML
- [Aeromonas AMR Genomics](https://github.com/hyejeong0617/amr_genomics_aeromonas) — genomics and antimicrobial resistance

---

**Hyejeong Lee** · PhD in Biotechnology · Scientific Data Science & Applied AI  
[GitHub](https://github.com/hyejeong0617) · [LinkedIn](https://www.linkedin.com/in/hyejeong-lee-75887465/)
