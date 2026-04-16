# Customer Value Intelligence Platform

A Codex-ready portfolio project designed for **Solution Architect / Business Architect** positioning.

This pack is built to help Codex directly scaffold, extend, and refine a production-style analytics project with:

- business-facing architecture narrative
- modular Python package
- synthetic demo data
- visualization scripts
- acceptance criteria and implementation prompts

## What this project demonstrates

This project simulates a customer intelligence platform that helps business teams answer:

- Which customers are high value?
- Which segments are likely to churn?
- Which stores or channels contribute most revenue?
- How should CRM / marketing prioritize interventions?

## Included in this pack

- `prompts/CODEX_BOOTSTRAP_PROMPT.md` — prompt you can paste into Codex
- `docs/PROJECT_SPEC.md` — project scope and business goals
- `docs/ACCEPTANCE_CRITERIA.md` — delivery and quality checklist
- `src/generate_fake_data.py` — synthetic customer / transaction / campaign data generator
- `src/visualize.py` — chart generation script
- `src/pipeline.py` — transformation and feature engineering pipeline
- `src/app.py` — lightweight Streamlit demo app
- `data/` — pre-generated demo data
- `outputs/` — pre-rendered chart images

## Quick start

```bash
pip install -r requirements.txt
python src/generate_fake_data.py
python src/pipeline.py
python src/visualize.py
streamlit run src/app.py
```

## Recommended prompt flow in Codex

1. Open `prompts/CODEX_BOOTSTRAP_PROMPT.md`
2. Ask Codex to inspect the repo and implement missing enhancements
3. Ask Codex to:
   - add tests
   - improve feature engineering
   - harden CLI interface
   - extend the dashboard
   - add architecture diagram as Mermaid

## Architecture positioning

This is intentionally framed as a business-to-technology decision platform, not just an LTV notebook.

### Business layer

- customer value strategy
- CRM prioritization
- churn risk visibility
- growth opportunity identification

### Data layer

- transaction facts
- customer dimensions
- campaign responses
- curated analytics mart

### Application layer

- KPI charts
- segment analysis
- business storytelling dashboard

## Notes

- Data in `data/` is fully synthetic.
- The chart scripts use a Microsoft JhengHei-first font fallback in code. If the font is not installed in the environment, matplotlib will fall back automatically.
