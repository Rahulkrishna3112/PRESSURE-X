from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT 

st.set_page_config(page_title="PRESSURE-X | Cricket Analytics", page_icon="🏏", layout="wide")

# RR-inspired pink and blue palette
NAVY = "#142B55"
BLUE = "#2456A6"
PINK = "#E84C91"
PALE_BLUE = "#EAF1FF"
PALE_PINK = "#FCEAF2"
INK = "#18243A"
MUTED = "#667085"

st.markdown(f"""
<style>
  .stApp {{ background: #F7F9FC; color: {INK}; }}
  [data-testid="stSidebar"] {{ background: #F0F4FC; }}
  .hero {{ background: linear-gradient(110deg, {NAVY} 0%, {BLUE} 65%, {PINK} 100%); padding: 1.45rem 1.7rem; border-radius: 16px; color: white; margin-bottom: 1rem; }}
  .hero h1 {{ color: white; font-size: 2.25rem; margin: 0; letter-spacing: .04em; }}
  .hero p {{ color: #F8EAF1; margin: .3rem 0 0 0; font-size: 1rem; }}
  .metric-card {{ background: white; border: 1px solid #E3E9F3; border-top: 4px solid {PINK}; border-radius: 12px; padding: 14px 16px; }}
  .metric-label {{ color: {MUTED}; font-size: .82rem; }}
  .metric-value {{ color: {NAVY}; font-weight: 750; font-size: 1.8rem; }}
  .section-note {{ color: {MUTED}; font-size: .88rem; }}
  h1,h2,h3 {{ color: {NAVY}; }}
  div[data-testid="stMetric"] {{ background: white; padding: 12px 14px; border: 1px solid #E3E9F3; border-radius: 12px; }}
  div[data-testid="stMetric"] label {{ color: {MUTED}; }}
  .warning {{ background: {PALE_PINK}; border-left: 4px solid {PINK}; padding: 12px 15px; border-radius: 8px; }}
  .info {{ background: {PALE_BLUE}; border-left: 4px solid {BLUE}; padding: 12px 15px; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_csv(name):
    path = DATA / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

bat_top = load_csv("top10_batters.csv")
bowl_top = load_csv("top10_bowlers.csv")
bat_all = load_csv("top_batters_ranked.csv")
bowl_all = load_csv("top_bowlers_ranked.csv")
sensitivity = load_csv("sample_threshold_sensitivity.csv")
coverage = load_csv("match_coverage.csv")
audit = load_csv("run_audit.csv")
eligibility = load_csv("top10_eligibility_audit.csv")
deliveries = load_csv("delivery_pressure_states.csv")

if bat_top.empty or bowl_top.empty:
    st.error("Required ranking CSV files are missing. Keep the supplied data folder beside app.py.")
    st.stop()

# Pull run-level values from the audited output rather than hardcoding them.
def audit_value(key, fallback=0):
    if audit.empty or not {"metric", "value"}.issubset(audit.columns):
        return fallback
    row = audit.loc[audit.metric.astype(str) == key, "value"]
    return int(float(row.iloc[0])) if not row.empty else fallback

matches = audit_value("matches_2022_onward", 458)
rows = audit_value("delivery_rows", len(deliveries))
ipl_matches = audit_value("IPL_matches", 367)
smat_matches = audit_value("SMAT_matches", 91)

st.markdown(f"""
<div class="hero">
  <h1>PRESSURE-X</h1>
  <p>CRICKET PRESSURE PERFORMANCE ANALYTICS &nbsp;|&nbsp; IPL + SMAT &nbsp;|&nbsp; 2022 ONWARDS</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## PRESSURE-X")
    st.caption("V1 · SuperSelectoRR Season 2")
    page = st.radio("Navigate", ["Overview", "Batter Analysis", "Bowler Analysis", "Pressure Explorer", "Methodology & Reliability"])
    st.divider()
    st.caption("Data source: final V1 run outputs")
    st.caption("Scores are comparative model outputs, not player valuations.")

if page == "Overview":
    st.subheader("Tournament overview")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Matches analysed", f"{matches:,}")
    c2.metric("Delivery records", f"{rows:,}")
    c3.metric("IPL matches", f"{ipl_matches:,}")
    c4.metric("SMAT matches", f"{smat_matches:,}")

    left,right = st.columns([1.1,1])
    with left:
        st.markdown("### Top pressure-performing batters")
        chart = px.bar(bat_top.sort_values("pressure_score"), x="pressure_score", y="player", orientation="h",
                       text="pressure_score", color_discrete_sequence=[PINK])
        chart.update_traces(texttemplate="%{text:.3f}", textposition="outside", cliponaxis=False)
        chart.update_layout(height=440, margin=dict(l=5,r=45,t=10,b=5), xaxis_title="V1 pressure score", yaxis_title="", showlegend=False)
        st.plotly_chart(chart, use_container_width=True)
    with right:
        st.markdown("### Top pressure-performing bowlers")
        chart = px.bar(bowl_top.sort_values("pressure_score"), x="pressure_score", y="player", orientation="h",
                       text="pressure_score", color_discrete_sequence=[BLUE])
        chart.update_traces(texttemplate="%{text:.3f}", textposition="outside", cliponaxis=False)
        chart.update_layout(height=440, margin=dict(l=5,r=45,t=10,b=5), xaxis_title="V1 pressure score", yaxis_title="", showlegend=False)
        st.plotly_chart(chart, use_container_width=True)

    if not coverage.empty:
        st.markdown("### Match coverage by competition and season")
        cov = coverage.copy()
        cov["season"] = cov.season.astype(str)
        fig = px.bar(cov, x="season", y="matches", color="competition", barmode="group",
                     color_discrete_map={"IPL": BLUE, "SMAT": PINK}, text="matches")
        fig.update_layout(height=330, xaxis_title="Season", yaxis_title="Matches", legend_title="Competition")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="info"><b>How to read this dashboard:</b> A higher positive V1 score indicates a stronger pressure-versus-baseline profile under the defined scoring formula. Always read the score alongside sample size and the reliability notes.</div>', unsafe_allow_html=True)

elif page == "Batter Analysis":
    st.subheader("Batter performance under pressure")
    st.caption("Rankings use the final V1 specialist-batter output. All values below are loaded from the supplied CSV results.")
    min_n = st.slider("Minimum pressure and baseline balls to display", 0, 200, 30, 5)
    df = bat_all[(bat_all.pressure_balls >= min_n) & (bat_all.baseline_balls >= min_n)].copy()
    df = df.sort_values("pressure_score", ascending=False)
    st.dataframe(df[["rank","player","pressure_score","pressure_balls","baseline_balls","pressure_runs_per_ball","baseline_runs_per_ball","pressure_boundary_rate","baseline_boundary_rate","pressure_dot_rate","baseline_dot_rate","pressure_dismissal_rate","baseline_dismissal_rate"]],
                 use_container_width=True, hide_index=True,
                 column_config={"pressure_score": st.column_config.NumberColumn(format="%.4f"),
                                 "pressure_runs_per_ball": st.column_config.NumberColumn(format="%.3f"),
                                 "baseline_runs_per_ball": st.column_config.NumberColumn(format="%.3f")})
    if not df.empty:
        selected = st.selectbox("Inspect a batter", df.player.tolist())
        p = df.loc[df.player == selected].iloc[0]
        a,b,c = st.columns(3)
        a.metric("V1 pressure score", f"{p.pressure_score:.4f}")
        b.metric("Pressure balls", int(p.pressure_balls))
        c.metric("Baseline balls", int(p.baseline_balls))
        metrics = pd.DataFrame({"Metric":["Runs per ball","Boundary rate","Dot-ball rate","Dismissal rate"],
                                "Pressure":[p.pressure_runs_per_ball,p.pressure_boundary_rate,p.pressure_dot_rate,p.pressure_dismissal_rate],
                                "Baseline":[p.baseline_runs_per_ball,p.baseline_boundary_rate,p.baseline_dot_rate,p.baseline_dismissal_rate]})
        fig = px.bar(metrics.melt(id_vars="Metric",var_name="Situation",value_name="Rate"), x="Metric",y="Rate",color="Situation",barmode="group",
                     color_discrete_map={"Pressure":PINK,"Baseline":BLUE},text_auto=".3f")
        fig.update_layout(height=360, yaxis_title="Rate", xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
        if isinstance(p.get("role_source"), str) and p.role_source.startswith("http"):
            st.markdown(f"Role verification source: [{p.verified_role}]({p.role_source})")

elif page == "Bowler Analysis":
    st.subheader("Bowling performance under pressure")
    st.caption("Bowler ranking output uses legal-ball exposure for the minimum-sample gate; score components are shown as rates from V1.")
    min_n = st.slider("Minimum pressure and baseline legal balls to display", 0, 200, 30, 5)
    df = bowl_all[(bowl_all.pressure_balls >= min_n) & (bowl_all.baseline_balls >= min_n)].copy().sort_values("pressure_score", ascending=False)
    st.dataframe(df[["rank","player","pressure_score","pressure_balls","baseline_balls","pressure_runs_per_ball","baseline_runs_per_ball","pressure_wicket_rate","baseline_wicket_rate","pressure_dot_rate","baseline_dot_rate","pressure_boundary_rate","baseline_boundary_rate"]],
                 use_container_width=True,hide_index=True,
                 column_config={"pressure_score":st.column_config.NumberColumn(format="%.4f")})
    if not df.empty:
        selected = st.selectbox("Inspect a bowler",df.player.tolist())
        p = df.loc[df.player == selected].iloc[0]
        a,b,c = st.columns(3)
        a.metric("V1 pressure score",f"{p.pressure_score:.4f}")
        b.metric("Pressure legal balls",int(p.pressure_balls))
        c.metric("Baseline legal balls",int(p.baseline_balls))
        metrics = pd.DataFrame({"Metric":["Runs per ball","Wicket rate","Dot-ball rate","Boundary rate"],
                                "Pressure":[p.pressure_runs_per_ball,p.pressure_wicket_rate,p.pressure_dot_rate,p.pressure_boundary_rate],
                                "Baseline":[p.baseline_runs_per_ball,p.baseline_wicket_rate,p.baseline_dot_rate,p.baseline_boundary_rate]})
        fig = px.bar(metrics.melt(id_vars="Metric",var_name="Situation",value_name="Rate"),x="Metric",y="Rate",color="Situation",barmode="group",
                     color_discrete_map={"Pressure":PINK,"Baseline":BLUE},text_auto=".3f")
        fig.update_layout(height=360,yaxis_title="Rate",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
        if selected == "Chama Milind":
            st.markdown('<div class="warning"><b>Interpretation caution:</b> Chama Milind has zero baseline wickets in the V1 output. The wicket-rate component uses a denominator floor, which materially influences his score. Treat the rank as a model result requiring further validation, not definitive evidence of superiority.</div>',unsafe_allow_html=True)
        if isinstance(p.get("role_source"), str) and p.role_source.startswith("http"):
            st.markdown(f"Role verification source: [{p.verified_role}]({p.role_source})")

elif page == "Pressure Explorer":
    st.subheader("Explore pressure states in the ball-by-ball data")
    if deliveries.empty:
        st.warning("delivery_pressure_states.csv is missing from data/. Add it to enable this page.")
    else:
        d = deliveries.copy()
        d["date"] = pd.to_datetime(d.date, errors="coerce")
        competitions = sorted(d.competition.dropna().unique().tolist())
        chosen_comp = st.multiselect("Competition",competitions,default=competitions)
        d = d[d.competition.isin(chosen_comp)]
        innings = sorted(d.innings.dropna().unique().tolist())
        chosen_innings = st.multiselect("Innings",innings,default=innings)
        d = d[d.innings.isin(chosen_innings)]
        if not d.empty:
            threshold = st.slider("Pressure score percentile threshold (display filter)",0,100,75,5)
            cutoff = d.pressure.quantile(threshold/100)
            d["pressure_band"] = d.pressure.ge(cutoff).map({True:"High pressure",False:"Other deliveries"})
            x,y,z = st.columns(3)
            x.metric("Filtered deliveries",f"{len(d):,}")
            y.metric(f"{threshold}th percentile cutoff",f"{cutoff:.3f}")
            z.metric("High-pressure deliveries",f"{(d.pressure >= cutoff).sum():,}")
            fig = px.histogram(d,x="pressure",color="pressure_band",nbins=40,barmode="overlay",opacity=.8,
                               color_discrete_map={"High pressure":PINK,"Other deliveries":BLUE})
            fig.update_layout(height=350,xaxis_title="Pressure score",yaxis_title="Deliveries",legend_title="Band")
            st.plotly_chart(fig,use_container_width=True)
            phase = d.assign(over_group=pd.cut(d.over,[-1,5,10,15,20],labels=["Overs 1–5","Overs 6–10","Overs 11–15","Overs 16–20"]))
            phase_summary = phase.groupby(["over_group","pressure_band"],observed=False).size().reset_index(name="deliveries")
            fig2 = px.bar(phase_summary,x="over_group",y="deliveries",color="pressure_band",barmode="group",
                          color_discrete_map={"High pressure":PINK,"Other deliveries":BLUE})
            fig2.update_layout(height=330,xaxis_title="Over phase",yaxis_title="Deliveries")
            st.plotly_chart(fig2,use_container_width=True)
            st.caption("This page recomputes a display-only percentile within the selected subset. The official V1 rankings use the original global 75th-percentile pressure definition.")

elif page == "Methodology & Reliability":
    st.subheader("V1 methodology and reliability")
    st.markdown("""
**Pressure definition**  
The V1 heuristic considers wickets lost, innings phase, current run rate and required run rate. Deliveries at or above the 75th percentile of the calculated pressure score are treated as high-pressure deliveries.

**Confidence adjustment**  
`Final score = Raw score × n / (n + 60)`  
Here, `n` is the number of high-pressure deliveries or legal balls for that player. This shrinks scores from smaller samples towards zero.

**Minimum sample gate**  
Players need at least 30 pressure and 30 baseline observations. Bowlers additionally require at least 18 legal balls in each band.

**Important distinction**  
A positive score is a relative comparison against that player's baseline under this specific V1 formula. It is not a direct estimate of skill, future performance, or causal impact.
""")
    st.markdown("### Sensitivity to minimum sample size")
    if not sensitivity.empty:
        counts = sensitivity.groupby(["sample_threshold_each_band","role"]).size().reset_index(name="qualified_players")
        fig = px.line(counts,x="sample_threshold_each_band",y="qualified_players",color="role",markers=True,
                      color_discrete_map={"BATTER":PINK,"BOWLER":BLUE})
        fig.update_layout(height=350,xaxis_title="Minimum observations in each band",yaxis_title="Eligible ranked players")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(counts.pivot(index="sample_threshold_each_band",columns="role",values="qualified_players").fillna(0).astype(int),use_container_width=True)
    st.markdown("### Data and eligibility audit")
    if not eligibility.empty:
        st.dataframe(eligibility,use_container_width=True,hide_index=True)
    st.markdown('<div class="warning"><b>Known V1 limitations</b><ul><li>Batter rankings are sample-size sensitive: 10 qualify at a 30-observation gate, 9 at 50, and 6 at 75 or 100.</li><li>Chama Milind has zero baseline wickets; the denominator floor influences the wicket-rate contribution.</li><li>Coverage is IPL-heavy: 367 IPL matches versus 91 SMAT matches.</li><li>SMAT coverage is incomplete, especially 2024/25; no 2025/26 SMAT matches are included.</li><li>Only 59 player roles were verified; 769 unverified roles were held out.</li></ul></div>',unsafe_allow_html=True)
    st.markdown("### Match coverage table")
    if not coverage.empty:
        st.dataframe(coverage,use_container_width=True,hide_index=True)

st.divider()
st.caption("PRESSURE-X V1 · SuperSelectoRR Season 2 case study · Built with Streamlit · Results are subject to the documented data and methodology limitations.")
