# PRESSURE-X — Streamlit Dashboard

Interactive dashboard for the PRESSURE-X V1 cricket pressure-performance case study (IPL + SMAT, 2022 onwards).

## Features
- Competition overview and V1 Top 10 rankings
- Batter and bowler ranking tables with player-level pressure vs baseline comparisons
- Ball-by-ball pressure explorer using the V1 delivery-state output
- Sample-threshold sensitivity, eligibility audit, match coverage and limitations
- Rajasthan Royals-inspired pink/blue visual styling

## Run locally (Windows PowerShell)

```powershell
cd path\to\PRESSURE-X-Streamlit
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in the terminal (normally `http://localhost:8501`).

## Data files
All CSVs in `data/` are outputs from the final PRESSURE-X V1 run. The dashboard does not recalculate player scores. It visualises the supplied audited outputs.

The dashboard uses:
- `top10_batters.csv`, `top10_bowlers.csv`
- `top_batters_ranked.csv`, `top_bowlers_ranked.csv`
- `sample_threshold_sensitivity.csv`
- `match_coverage.csv`, `run_audit.csv`
- `top10_eligibility_audit.csv`
- `delivery_pressure_states.csv`

## Interpretation notes
- V1 pressure states are based on wickets lost, innings phase, current run rate and required run rate.
- High-pressure deliveries in the ranking methodology are at or above the global 75th percentile of pressure.
- Confidence adjustment: `final_score = raw_score * n / (n + 60)`.
- The default minimum sample gate is 30 pressure and 30 baseline observations; bowlers additionally require at least 18 legal balls in each band.
- Scores are relative model outputs, not causal estimates or definitive player valuations.
- The dashboard explicitly flags sample sensitivity, IPL-heavy coverage, incomplete SMAT coverage, role-verification limits and Chama Milind's zero-baseline-wicket issue.

## Deploy to Streamlit Community Cloud
1. Push this project folder to a public GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository.
3. Set the main file path to `app.py`.
4. Deploy. Keep `requirements.txt` and the `data/` directory in the repository.

## Suggested repository hygiene
Do not commit `.venv/`, `__pycache__/`, `.streamlit/secrets.toml`, or raw Cricsheet archives unless redistribution rights and repository size have been checked.

## Project status
This is a dashboard for **PRESSURE-X V1**. The V2 methodology is future work and is not represented as completed or validated here.
