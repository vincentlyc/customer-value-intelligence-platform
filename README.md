# Customer Value Intelligence Platform

A portfolio-ready analytics demo positioned for **Solution Architect / Business Architect** interviews.

This project demonstrates how customer data can be transformed into practical decisions around:

- segment strategy
- retention prioritization
- channel performance
- executive-facing KPI storytelling

## Project structure

- `src/generate_fake_data.py` — synthetic customer / transaction / campaign generator
- `src/pipeline.py` — mart and business summary pipeline
- `src/visualize.py` — presentation chart renderer
- `src/app.py` — Streamlit decision dashboard
- `tests/` — unit tests for generation and pipeline logic
- `docs/ARCHITECTURE_NOTES.md` — architecture narrative + Mermaid diagram

## Quick start

```bash
make install
make data
make pipeline
make viz
make run
```

Or run scripts directly:

```bash
python -m src.generate_fake_data --customers 2000 --transactions 40000 --seed 42
python -m src.pipeline --data-dir ./data --output-dir ./outputs
python -m src.visualize --data-dir ./data --output-dir ./outputs
streamlit run src/app.py
```

## Codespaces quick start

If you run this in **GitHub Codespaces**:

```bash
pip install -r requirements.txt
python -m src.generate_fake_data --customers 1000 --transactions 20000 --seed 42
python -m src.pipeline --data-dir ./data --output-dir ./outputs
streamlit run src/app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```

Then open the **Ports** panel and click **Open in Browser** on port `8501`.

## Demo page note

The Streamlit screen shown in your screenshot is the **official DEMO page** for this project: 

- title: `Customer Value Intelligence Demo`
- filters: `Segment`, `Store`
- KPI cards: `Customers`, `Revenue`, `Avg Revenue`, `Avg Recency`
- visual blocks: `Segment Revenue Mix`, `Churn Risk Distribution`
- operational table: `Top Customers`

Use this page during interview walkthroughs as the executive decision-view UI.

## CLI notes

- `generate_fake_data.py`
  - `--customers`, `--transactions` require positive integers
  - `--output-dir` supports custom output location for scenario demos
- `pipeline.py`
  - accepts `--data-dir` and `--output-dir` for flexible local runs
- `visualize.py`
  - accepts `--data-dir` and `--output-dir` for reproducible chart exports

## Dashboard highlights

- KPI cards: customer count, total revenue, average revenue, average recency
- Sidebar filters: segment and store
- Segment revenue mix and churn risk distribution charts
- Top-customer operational table
- Segment/store summaries for executive drill-down

## Troubleshooting (Codespaces)

- If `localhost:8501` cannot be opened, use Codespaces **Ports → Open in Browser** URL.
- If dashboard shows missing CSV errors, run generator + pipeline before launching app.
- If port is not visible, manually add/forward port `8501`.

## Architecture positioning

This is intentionally framed as a business-to-technology decision platform, not just an LTV notebook.

See [docs/ARCHITECTURE_NOTES.md](docs/ARCHITECTURE_NOTES.md) for the architecture interview script and Mermaid flow diagram.

## Notes

- Data in `data/` is fully synthetic and safe for portfolio sharing.
- The chart scripts use a Microsoft JhengHei-first font fallback in code.
