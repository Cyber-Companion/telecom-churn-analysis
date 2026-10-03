"""Builds dashboard/telco_churn_dashboard.html — self-contained interactive
dashboard (plotly.js via CDN): Churn Overview / Churn Drivers / Revenue at Risk.
Run from project root:  python python/build_dashboard.py
"""
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.io import to_html

RAW = "data/raw/Telco-Customer-Churn.csv"
OUT = "dashboard/telco_churn_dashboard.html"

NAVY, TEAL, RED, AMBER, SLATE, LIGHT = (
    "#1f2a44", "#2a9d8f", "#e76f51", "#e9c46a", "#5b6b7f", "#f4f6f9")

# ---------------------------------------------------------------- data
df = pd.read_csv(RAW)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace(" ", np.nan),
                                   errors="coerce")
df["is_churned"] = df["Churn"] == "Yes"
df["tenure_band"] = pd.cut(df["tenure"], [0, 6, 12, 24, 48, 100],
                           labels=["0–6", "7–12", "13–24", "25–48", "49+"])

churn_rate = df.is_churned.mean()
n = len(df)
rev_lost = df.loc[df.is_churned, "MonthlyCharges"].sum()
rev_total = df.MonthlyCharges.sum()
seg = df[(df.Contract == "Month-to-month")
         & (df.PaymentMethod == "Electronic check") & (df.tenure <= 12)]
seg_rate = seg.is_churned.mean()


def kpi(label, value, sub=""):
    return (f'<div class="kpi"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>')


def fig_html(fig, first):
    js = "cdn" if os.environ.get("PLOTLY_CDN", "1") == "1" else True
    return to_html(fig, full_html=False, include_plotlyjs=(js if first else False),
                   config={"displaylogo": False})


def base_layout(title, hbar=False):
    m = dict(l=170, r=90, t=60, b=50) if hbar else dict(l=50, r=30, t=60, b=50)
    return dict(title=dict(text=title, font=dict(size=15, color=NAVY)),
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="Segoe UI, Arial", color=SLATE), margin=m)


def churn_bar(series, title, color, hbar=True):
    s = (series.mul(100).round(1).sort_values(ascending=not hbar)
         if hbar else series.mul(100).round(1))
    if hbar:
        s = s.sort_values()
        fig = go.Figure(go.Bar(
            x=s.values, y=s.index, orientation="h", marker_color=color,
            text=s.map(lambda v: f"{v}%"), textposition="outside"))
        fig.update_layout(**base_layout(title, hbar=True),
                          xaxis=dict(range=[0, s.values.max() * 1.22]))
    else:
        fig = go.Figure(go.Bar(x=s.index.astype(str), y=s.values,
                               marker_color=color,
                               text=s.map(lambda v: f"{v}%"),
                               textposition="outside"))
        fig.update_layout(**base_layout(title),
                          xaxis_title="", yaxis_title="churn %")
    return fig


# ------------------------------------------------- Page 1
f1 = churn_bar(df.groupby("Contract")["is_churned"].mean(),
               "Churn rate by contract (%)", RED)
f2 = churn_bar(df.groupby("tenure_band", observed=True)["is_churned"].mean(),
               "Churn rate by tenure band, months (%)", TEAL, hbar=False)

donut = df.is_churned.value_counts()
f3 = go.Figure(go.Pie(
    labels=["Stayed", "Churned"], values=[donut[False], donut[True]], hole=0.45,
    marker=dict(colors=[TEAL, RED]),
    textinfo="label+percent"))
f3.update_layout(**base_layout("Customer base: churned vs stayed"))

mc = df.groupby("is_churned")["MonthlyCharges"].mean()
f4 = go.Figure(go.Bar(
    x=["Stayed", "Churned"], y=[mc[False], mc[True]],
    marker_color=[TEAL, RED],
    text=[f"${mc[False]:.2f}", f"${mc[True]:.2f}"], textposition="outside"))
f4.update_layout(**base_layout("Avg monthly charges: stayed vs churned ($)"),
                 yaxis_title="$")

# ------------------------------------------------- Page 2
f5 = churn_bar(df.groupby("PaymentMethod")["is_churned"].mean(),
               "Churn rate by payment method (%)", RED)
f6 = churn_bar(df.groupby("InternetService")["is_churned"].mean(),
               "Churn rate by internet service (%)", RED)

ts = df[df.InternetService != "No"].groupby("TechSupport")["is_churned"].mean()
f7 = go.Figure(go.Bar(
    x=["No tech support", "Has tech support"],
    y=[ts["No"] * 100, ts["Yes"] * 100], marker_color=[RED, TEAL],
    text=[f"{ts['No']*100:.1f}%", f"{ts['Yes']*100:.1f}%"],
    textposition="outside"))
f7.update_layout(**base_layout("Tech support cuts churn by nearly 2/3 (%)"),
                 yaxis_title="churn %")

demo = pd.Series({
    "Senior citizens": df[df.SeniorCitizen == 1].is_churned.mean() * 100,
    "No partner": df[df.Partner == "No"].is_churned.mean() * 100,
    "No dependents": df[df.Dependents == "No"].is_churned.mean() * 100,
    "Paperless billing": df[df.PaperlessBilling == "Yes"].is_churned.mean() * 100,
}).sort_values()
f8 = go.Figure(go.Bar(x=demo.values, y=demo.index, orientation="h",
                      marker_color=AMBER,
                      text=[f"{v:.1f}%" for v in demo.values],
                      textposition="outside"))
f8.update_layout(**base_layout("Churn rate by customer profile (%)", hbar=True),
                 xaxis=dict(range=[0, demo.values.max() * 1.22]))

# ------------------------------------------------- Page 3
cmp_ = pd.DataFrame({
    "segment": ["Whole base", "High-risk segment*"],
    "customers": [n, len(seg)],
    "churn_rate": [churn_rate * 100, seg_rate * 100],
    "monthly_revenue": [rev_total, seg.MonthlyCharges.sum()],
}).round(1)
rows = "".join(
    "<tr>" + "".join(f"<td>{c}</td>" for c in
                     [r.segment, f"{int(r.customers):,}",
                      f"{r.churn_rate:.1f}%",
                      f"${r.monthly_revenue:,.0f}"]) + "</tr>"
    for r in cmp_.itertuples())
table_seg = (f'<div class="chart full"><div class="dtable-title">High-risk segment vs whole base '
             f'<span style="font-weight:400;font-size:12px">* month-to-month + electronic check + tenure ≤ 12 mo</span></div>'
             f'<table class="dtable"><thead><tr><th>Segment</th><th>Customers</th>'
             f'<th>Churn rate</th><th>Monthly revenue</th></tr></thead>'
             f"<tbody>{rows}</tbody></table></div>")

save = seg.MonthlyCharges.sum() * (seg_rate - 0.30)  # if segment churn cut to 30%
f9 = go.Figure(go.Bar(
    x=["Revenue lost<br>today", "Revenue saved<br>if segment churn → 30%"],
    y=[rev_lost, save], marker_color=[RED, TEAL],
    text=[f"${rev_lost:,.0f}", f"${save:,.0f}"], textposition="outside"))
f9.update_layout(**base_layout("Monthly revenue: lost vs recoverable ($)"),
                 yaxis_title="$")

# ---------------------------------------------------------------- assemble
figs = [f1, f2, f3, f4, f5, f6, f7, f8, f9]
snippets, first = [], True
for fig in figs:
    snippets.append(fig_html(fig, first))
    first = False
(s1a, s1b, s1c, s1d, s2a, s2b, s2c, s2d, s3a) = snippets

p1k = "".join([
    kpi("Churn rate", f"{churn_rate:.1%}", f"{int(df.is_churned.sum()):,} of {n:,}"),
    kpi("Customers", f"{n:,}", "telecom base"),
    kpi("Revenue at risk", f"${rev_lost:,.0f}/mo", f"{rev_lost/rev_total:.1%} of monthly revenue"),
    kpi("Avg tenure", f"{df.loc[df.is_churned,'tenure'].mean():.0f} mo churned",
        f"vs {df.loc[~df.is_churned,'tenure'].mean():.0f} mo stayed"),
])
p2k = "".join([
    kpi("Month-to-month", "42.7%", "vs 2.8% two-year (15x)"),
    kpi("Electronic check", "45.3%", "vs 15.2% card autopay"),
    kpi("Fiber optic", "41.9%", "vs 19.0% DSL"),
    kpi("First 6 months", "53.3%", "vs 9.5% after 4 years"),
])
p3k = "".join([
    kpi("Target segment", f"{len(seg):,}", "13.5% of base"),
    kpi("Segment churn", f"{seg_rate:.1%}", "vs 26.5% overall"),
    kpi("Churners in segment", f"{int(seg.is_churned.sum()):,}",
        f"{seg.is_churned.sum()/df.is_churned.sum():.1%} of all churn"),
    kpi("Recoverable", f"${save:,.0f}/mo", "if segment churn → 30%"),
])

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Telecom Customer Churn Dashboard</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:{LIGHT};margin:0;color:{SLATE}}}
header{{background:{NAVY};color:white;padding:22px 32px}}
header h1{{margin:0;font-size:22px}} header p{{margin:6px 0 0;opacity:.75;font-size:13px}}
nav{{display:flex;gap:8px;padding:14px 32px 0;flex-wrap:wrap}}
nav button{{border:none;background:#dde3ec;color:{NAVY};padding:10px 20px;border-radius:8px 8px 0 0;
  font-size:14px;font-weight:600;cursor:pointer}}
nav button.active{{background:white;color:{NAVY}}}
.page{{display:none;background:white;margin:0 32px 32px;padding:24px;border-radius:0 8px 8px 8px}}
.page.active{{display:block}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}}
.kpi{{background:{LIGHT};border-left:4px solid {RED};border-radius:6px;padding:14px 16px}}
.kpi-label{{font-size:12px;text-transform:uppercase;letter-spacing:.5px;opacity:.7}}
.kpi-value{{font-size:24px;font-weight:700;color:{NAVY};margin:4px 0}}
.kpi-sub{{font-size:12px;opacity:.7}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.chart{{border:1px solid #e6eaf0;border-radius:8px;padding:8px;margin-bottom:16px}}
.full{{grid-column:1/-1}}
.insight{{background:#fdf1ec;border-left:4px solid {RED};border-radius:6px;padding:14px 18px;
  margin:4px 0 20px;font-size:14px;line-height:1.6}}
.insight b{{color:{NAVY}}}
.dtable-title{{font-size:15px;font-weight:600;color:{NAVY};padding:14px 8px 10px}}
table.dtable{{width:100%;border-collapse:collapse;font-size:13px;margin:0 0 8px}}
table.dtable th{{background:{NAVY};color:white;text-align:left;padding:10px 12px;font-weight:600}}
table.dtable td{{padding:9px 12px;border-bottom:1px solid #edf0f4}}
table.dtable tbody tr:nth-child(even){{background:{LIGHT}}}
footer{{text-align:center;font-size:12px;color:#8a97a8;padding:0 0 28px}}
@media(max-width:900px){{.kpis,.grid2{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>Telecom Customer Churn Dashboard</h1>
<p>7,043 customers &middot; SQL &rarr; Python &rarr; interactive dashboard &middot; by Adnan Habib</p></header>
<nav>
<button class="active" onclick="show('p1',this)">Churn Overview</button>
<button onclick="show('p2',this)">Churn Drivers</button>
<button onclick="show('p3',this)">Revenue at Risk</button>
</nav>

<div id="p1" class="page active">
<div class="kpis">{p1k}</div>
<div class="insight"><b>Key insight:</b> <b>26.5%</b> of customers churn. The first 6 months are
critical (<b>53.3%</b> churn) and churned customers actually paid <b>more</b> ($74.44 vs $61.27) —
the company is losing high-value customers.</div>
<div class="grid2"><div class="chart">{s1a}</div><div class="chart">{s1b}</div>
<div class="chart">{s1c}</div><div class="chart">{s1d}</div></div></div>

<div id="p2" class="page">
<div class="kpis">{p2k}</div>
<div class="insight"><b>Key insight:</b> contract type is the #1 driver (<b>42.7% vs 2.8%</b>), followed by
electronic-check billing (<b>45.3%</b>) and fiber optic (<b>41.9%</b>). Tech support alone cuts
churn from <b>41.6% → 15.2%</b>.</div>
<div class="grid2"><div class="chart">{s2a}</div><div class="chart">{s2b}</div>
<div class="chart">{s2c}</div><div class="chart">{s2d}</div></div></div>

<div id="p3" class="page">
<div class="kpis">{p3k}</div>
<div class="insight"><b>Recommendation:</b> target the high-risk segment (month-to-month + electronic check +
tenure ≤ 12 mo) with annual-contract discounts, autopay migration, and a 90-day onboarding save
program. Cutting its churn to 30% recovers <b>${save:,.0f}/month</b>.</div>
<div class="grid2">{table_seg}<div class="chart full">{s3a}</div></div></div>

<footer>Data: IBM telco customer churn (open data) &middot; Built with Python/Plotly</footer>
<script>
function show(id,btn){{document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
document.querySelectorAll('nav button').forEach(b=>b.classList.remove('active'));
document.getElementById(id).classList.add('active');btn.classList.add('active');
window.dispatchEvent(new Event('resize'));}}
</script></body></html>"""

os.makedirs("dashboard", exist_ok=True)
with open(OUT, "w") as fh:
    fh.write(html)
print(f"dashboard written: {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
