import streamlit as st
import subprocess
import sys
import os
import json
import pandas as pd
from dotenv import load_dotenv, set_key
from datetime import datetime, timedelta

load_dotenv()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
ENV_PATH   = os.path.join(BASE_DIR, '.env')

st.set_page_config(
    page_title="Review Pulse — ChatGPT India",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --bg:#ffffff; --bg2:#f5f5f4; --bg3:#efefed;
  --text:#1a1a18; --text2:#6b6b68; --text3:#9f9f9b;
  --border:rgba(0,0,0,0.12); --border2:rgba(0,0,0,0.22);
  --green:#1D9E75; --green-bg:#E1F5EE; --green-border:#5DCAA5; --green-text:#0F6E56;
  --red:#E24B4A;   --red-bg:#FCEBEB;   --red-text:#A32D2D;
  --amber:#BA7517;
  --blue:#378ADD;  --blue-bg:#E6F1FB;  --blue-text:#185FA5;
  --purple:#7F77DD;
  --radius:8px; --radius-lg:12px;
  --font:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}

#MainMenu, header[data-testid="stHeader"], footer { visibility:hidden; height:0; }
[data-testid="stToolbar"], .stDeployButton { display:none !important; }
.stApp { background:var(--bg3) !important; font-family:var(--font) !important; }
section.main > div.block-container { max-width:700px !important; padding:1rem 1.2rem 4rem !important; }

/* Hero */
.hero { text-align:center; padding:2rem 1rem 1.5rem; }
.app-icon {
  width:52px; height:52px; border-radius:14px;
  background:#1a1a1a; display:flex; align-items:center;
  justify-content:center; margin:0 auto 12px;
}
.hero h1 { font-size:20px; font-weight:600; margin-bottom:6px; color:var(--text); }
.hero p   { font-size:14px; color:var(--text2); line-height:1.6; max-width:380px; margin:0 auto; }
.next-pill {
  display:inline-flex; align-items:center; gap:6px;
  background:var(--green-bg); border:0.5px solid var(--green-border);
  border-radius:20px; padding:5px 14px; font-size:12px;
  color:var(--green-text); font-weight:500; margin-top:12px;
}
.pill-dot { width:7px; height:7px; border-radius:50%; background:var(--green); display:inline-block; }

/* Progress card */
.prog-card {
  background:var(--bg); border:0.5px solid var(--border);
  border-radius:var(--radius-lg); padding:1.25rem; margin:1rem 0;
}
.prog-title { font-size:12px; font-weight:500; color:var(--text2); text-align:center; margin-bottom:1rem; }
.prog-steps { display:flex; align-items:center; justify-content:center; }
.ps  { display:flex; flex-direction:column; align-items:center; gap:5px; flex:1; }
.ps-icon { width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:14px; }
.ps-icon.done { background:var(--green-bg); }
.ps-icon.wait { background:var(--bg2); }
.ps-lbl { font-size:10px; text-align:center; line-height:1.3; max-width:60px; }
.ps-lbl.done { color:var(--green-text); font-weight:600; }
.ps-lbl.wait { color:var(--text3); }
.ps-line { height:2px; flex:0.5; border-radius:2px; margin-bottom:22px; }
.ps-line.done { background:var(--green); }
.ps-line.wait { background:var(--border); }

/* Section label */
.sec-lbl {
  font-size:11px; font-weight:600; color:var(--text2);
  text-transform:uppercase; letter-spacing:0.07em; margin-bottom:10px;
}

/* Stats grid */
.stats-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:1.25rem; }
.sc { background:var(--bg2); border-radius:var(--radius); padding:10px 12px; }
.sc-lbl  { font-size:11px; color:var(--text2); margin-bottom:3px; }
.sc-val  { font-size:20px; font-weight:600; color:var(--text); }
.sc-note { font-size:10px; color:var(--text3); margin-top:2px; }

/* Theme rows */
.theme-row {
  display:flex; align-items:center; gap:10px;
  background:var(--bg); border:0.5px solid var(--border);
  border-radius:var(--radius); padding:10px 12px; margin-bottom:6px; flex-wrap:wrap;
}
.tdot   { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.tinfo  { flex:1; min-width:140px; }
.ttitle { font-size:13px; font-weight:600; color:var(--text); }
.tsub   { font-size:11px; color:var(--text2); margin-top:2px; line-height:1.4; }
.tright { display:flex; align-items:center; gap:8px; }
.bar-bg   { width:64px; height:4px; background:var(--bg2); border-radius:4px; overflow:hidden; }
.bar-fill { height:100%; border-radius:4px; }
.tpct { font-size:12px; font-weight:600; min-width:28px; text-align:right; color:var(--text); }
.pill     { font-size:10px; padding:2px 8px; border-radius:20px; font-weight:600; white-space:nowrap; }
.pill-neg { background:var(--red-bg);   color:var(--red-text); }
.pill-pos { background:var(--green-bg); color:var(--green-text); }
.pill-neu { background:var(--bg2);      color:var(--text2); }

/* Divider */
.divider { border:none; border-top:0.5px solid var(--border); margin:1.25rem 0; }

/* Quotes */
.quotes-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.qcard  { background:var(--bg); border:0.5px solid var(--border); border-radius:var(--radius); padding:12px; }
.qstars { font-size:11px; color:var(--amber); margin-bottom:5px; }
.qtext  { font-size:12px; line-height:1.55; font-style:italic; margin-bottom:5px; color:var(--text); }
.qmeta  { font-size:10px; color:var(--text3); }

/* Actions */
.actions { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.ac { background:var(--bg2); border-radius:var(--radius); padding:12px; display:flex; gap:8px; }
.an { font-size:11px; font-weight:600; color:var(--text3); min-width:18px; }
.at { font-size:12px; line-height:1.5; color:var(--text); }

/* Rating bars */
.rbar-row  { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
.rbar-lbl  { font-size:12px; color:var(--text2); width:24px; text-align:right; flex-shrink:0; }
.rbar-bg   { flex:1; height:8px; background:var(--bg2); border-radius:4px; overflow:hidden; }
.rbar-fill { height:100%; border-radius:4px; }
.rbar-n    { font-size:12px; color:var(--text2); width:24px; }

/* Review table */
.table-wrap { overflow-x:auto; }
.rtable { width:100%; border-collapse:collapse; font-size:12px; }
.rtable th { text-align:left; padding:7px 8px; font-size:11px; font-weight:600; color:var(--text2); border-bottom:0.5px solid var(--border); }
.rtable td { padding:9px 8px; border-bottom:0.5px solid var(--border); vertical-align:top; line-height:1.5; color:var(--text); }
.rtable tr:last-child td { border-bottom:none; }
.star-c { color:var(--amber); white-space:nowrap; }
.tchip  { font-size:10px; padding:2px 7px; border-radius:20px; background:var(--bg2); border:0.5px solid var(--border); color:var(--text2); white-space:nowrap; }

/* Get Report card */
.get-card { background:var(--bg); border:0.5px solid var(--border); border-radius:var(--radius-lg); padding:1.5rem; margin:1.5rem 0 1rem; }
.get-card h2 { font-size:16px; font-weight:600; margin-bottom:5px; color:var(--text); }
.get-card p  { font-size:13px; color:var(--text2); margin-bottom:0; line-height:1.55; }

/* Or divider */
.or-row  { display:flex; align-items:center; gap:10px; margin:16px 0; }
.or-line { flex:1; height:0.5px; background:var(--border); }
.or-txt  { font-size:12px; color:var(--text3); }

/* Reassure */
.reassure { display:flex; gap:14px; justify-content:center; margin-top:14px; flex-wrap:wrap; }
.ri { font-size:11px; color:var(--text3); }

/* Empty state */
.empty-state { text-align:center; padding:2.5rem 1rem; color:var(--text2); font-size:14px; line-height:1.7; background:var(--bg); border:0.5px solid var(--border); border-radius:var(--radius-lg); }
.es-icon { font-size:2rem; margin-bottom:0.5rem; }

/* Streamlit text input */
.stTextInput > div > div > input {
  height:42px !important; border-radius:var(--radius) !important;
  border:0.5px solid var(--border2) !important; background:var(--bg2) !important;
  color:var(--text) !important; font-size:13px !important; font-family:var(--font) !important;
}
.stTextInput > div > div > input:focus {
  border-color:var(--green) !important;
  box-shadow:0 0 0 2px rgba(29,158,117,0.12) !important;
}
.stTextInput label { display:none !important; }

/* Primary button */
div[data-testid="stButton"] > button[kind="primary"] {
  background:var(--green) !important; color:#fff !important;
  border:none !important; border-radius:var(--radius) !important;
  font-size:14px !important; font-weight:600 !important;
  font-family:var(--font) !important; height:44px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover { background:var(--green-text) !important; }

/* Secondary / download buttons */
div[data-testid="stDownloadButton"] > button,
div[data-testid="stButton"] > button:not([kind="primary"]) {
  height:42px !important; border-radius:var(--radius) !important;
  border:0.5px solid var(--border2) !important; background:transparent !important;
  color:var(--text) !important; font-size:13px !important; font-family:var(--font) !important;
}
div[data-testid="stDownloadButton"] > button:hover,
div[data-testid="stButton"] > button:not([kind="primary"]):hover { background:var(--bg2) !important; }

/* Progress bar */
.stProgress > div > div { background:var(--green) !important; }

/* Expander */
.stExpander { border:0.5px solid var(--border) !important; border-radius:var(--radius) !important; background:var(--bg) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def file_exists(path):
    return os.path.exists(path) and os.path.getsize(path) > 0

def load_pulse():
    p = os.path.join(DATA_DIR, 'pulse.json')
    return json.load(open(p)) if file_exists(p) else None

def load_clustered():
    p = os.path.join(DATA_DIR, 'clustered_reviews.csv')
    return pd.read_csv(p) if file_exists(p) else None

def load_raw():
    p = os.path.join(DATA_DIR, 'raw_reviews.csv')
    return pd.read_csv(p) if file_exists(p) else None

def next_monday_str():
    today = datetime.now()
    days_ahead = 7 - today.weekday()
    return (today + timedelta(days=days_ahead)).strftime("Monday, %d %b · 7:00 AM IST")

def run_phase(phase):
    proc = subprocess.Popen(
        [sys.executable, 'main.py', '--phase', phase],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, cwd=BASE_DIR
    )
    logs = []
    for line in proc.stdout:
        logs.append(line.rstrip())
    proc.wait()
    return proc.returncode == 0, logs

def star_str(r):
    try:
        r = int(float(r))
        return '★' * r + '☆' * (5 - r)
    except Exception:
        return str(r)


# ── File states ───────────────────────────────────────────────────────────────
def get_states():
    return (
        file_exists(os.path.join(DATA_DIR,   'raw_reviews.csv')),
        file_exists(os.path.join(DATA_DIR,   'clustered_reviews.csv')),
        file_exists(os.path.join(DATA_DIR,   'pulse.json')),
        file_exists(os.path.join(OUTPUT_DIR, 'weekly_pulse.html')),
    )

raw_ok, cluster_ok, pulse_ok, report_ok = get_states()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="app-icon">
    <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
      <circle cx="13" cy="13" r="9" stroke="white" stroke-width="1.4"/>
      <path d="M9.5 13c0-1.9 1.6-3.5 3.5-3.5s3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5"
            stroke="white" stroke-width="1.4" stroke-linecap="round"/>
      <circle cx="13" cy="13" r="1.4" fill="white"/>
    </svg>
  </div>
  <h1>ChatGPT India — Review Pulse</h1>
  <p>200 Play Store reviews analysed every week. See what users love, hate, and want — in plain English.</p>
  <div class="next-pill">
    <div class="pill-dot"></div>
    Next auto-report: {next_monday_str()}
  </div>
</div>
""", unsafe_allow_html=True)


# ── Progress card ─────────────────────────────────────────────────────────────
def step(done):
    return ("✅", "done") if done else ("⬜", "wait")

s1i, s1c = step(raw_ok)
s2i, s2c = step(cluster_ok)
s3i, s3c = step(pulse_ok)
s4i, s4c = step(report_ok)
l1 = "done" if raw_ok and cluster_ok else "wait"
l2 = "done" if cluster_ok and pulse_ok else "wait"
l3 = "done" if pulse_ok and report_ok else "wait"
all_ready = all([raw_ok, cluster_ok, pulse_ok, report_ok])

st.markdown(f"""
<div class="prog-card">
  <div class="prog-title">{"This week's report is ready" if all_ready else "Pipeline status"}</div>
  <div class="prog-steps">
    <div class="ps"><div class="ps-icon {s1c}">{s1i}</div><div class="ps-lbl {s1c}">Reviews collected</div></div>
    <div class="ps-line {l1}"></div>
    <div class="ps"><div class="ps-icon {s2c}">{s2i}</div><div class="ps-lbl {s2c}">Themes found</div></div>
    <div class="ps-line {l2}"></div>
    <div class="ps"><div class="ps-icon {s3c}">{s3i}</div><div class="ps-lbl {s3c}">Insights ready</div></div>
    <div class="ps-line {l3}"></div>
    <div class="ps"><div class="ps-icon {s4c}">{s4i}</div><div class="ps-lbl {s4c}">Report built</div></div>
    <div class="ps-line wait"></div>
    <div class="ps"><div class="ps-icon wait">📬</div><div class="ps-lbl wait">Send to you</div></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Generate Report button ────────────────────────────────────────────────────
btn_label = "↺ Re-generate Report" if all_ready else "▶ Generate Report"
_, mid, _ = st.columns([1, 2, 1])
with mid:
    generate = st.button(btn_label, type="primary", use_container_width=True)

if generate:
    PHASES = [
        ("1/4  Scraping Play Store reviews…",  "scrape"),
        ("2/4  Clustering into themes…",        "cluster"),
        ("3/4  Analysing with Groq LLM…",       "analyse"),
        ("4/4  Generating report…",             "report"),
    ]
    status_box = st.empty()
    progress   = st.progress(0)
    with st.expander("📋 Details", expanded=False):
        log_box = st.empty()

    all_ok = True
    all_logs = []
    for i, (label, phase) in enumerate(PHASES):
        status_box.info(f"⟳ {label}")
        ok, logs = run_phase(phase)
        all_logs.extend(logs)
        log_box.code('\n'.join(all_logs[-30:]))
        progress.progress((i + 1) / len(PHASES))
        if not ok:
            status_box.error(f"❌ {label.split('…')[0]} failed. Check logs above.")
            all_ok = False
            break

    if all_ok:
        status_box.success("✅ Report generated! Scroll down to see insights.")
        st.rerun()


# ── INSIGHTS ──────────────────────────────────────────────────────────────────
pulse     = load_pulse()
raw       = load_raw()
clustered = load_clustered()

if not pulse:
    st.markdown("""
    <div class="empty-state">
      <div class="es-icon">📊</div>
      No insights yet — click <strong>Generate Report</strong> above to run the pipeline.
    </div>
    """, unsafe_allow_html=True)
else:
    themes = pulse.get('top_themes', [])
    total  = sum(t.get('review_count', 0) for t in themes) or (len(raw) if raw is not None else 0)
    pos_t  = [t for t in themes if t.get('sentiment') == 'positive']
    neg_t  = [t for t in themes if t.get('sentiment') == 'negative']
    avg_r  = raw['rating'].mean() if raw is not None and 'rating' in raw.columns else 0
    pos_pct = round(len(pos_t) / len(themes) * 100) if themes else 0
    neg_pct = round(len(neg_t) / len(themes) * 100) if themes else 0

    # ── Stats ──
    st.markdown(f"""
    <div class="stats-grid">
      <div class="sc"><div class="sc-lbl">Reviews</div><div class="sc-val">{total}</div><div class="sc-note">This week</div></div>
      <div class="sc"><div class="sc-lbl">Avg rating</div><div class="sc-val" style="color:var(--amber)">{avg_r:.1f} ★</div><div class="sc-note">&nbsp;</div></div>
      <div class="sc"><div class="sc-lbl">Positive</div><div class="sc-val" style="color:var(--green)">{pos_pct}%</div><div class="sc-note">{len(pos_t)} themes</div></div>
      <div class="sc"><div class="sc-lbl">Negative</div><div class="sc-val" style="color:var(--red)">{neg_pct}%</div><div class="sc-note">{len(neg_t)} themes</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Themes ──
    st.markdown('<div class="sec-lbl">What users are talking about</div>', unsafe_allow_html=True)
    SEN_COLOR = {'positive': 'var(--green)', 'negative': 'var(--red)', 'mixed': 'var(--amber)'}
    SEN_PILL  = {'positive': 'pill-pos',     'negative': 'pill-neg',   'mixed': 'pill-neu'}
    t_html = ''
    for t in themes:
        name      = t.get('theme_name', '')
        summary   = t.get('summary', '')
        sentiment = t.get('sentiment', 'mixed')
        count     = t.get('review_count', 0)
        pct       = round(count / total * 100) if total else 0
        bar_w     = min(100, pct * 2.5)
        color     = SEN_COLOR.get(sentiment, 'var(--amber)')
        pill      = SEN_PILL.get(sentiment, 'pill-neu')
        t_html += f"""
        <div class="theme-row">
          <div class="tdot" style="background:{color}"></div>
          <div class="tinfo">
            <div class="ttitle">{name}</div>
            <div class="tsub">{summary[:90]}</div>
          </div>
          <div class="tright">
            <div class="bar-bg"><div class="bar-fill" style="width:{bar_w}%;background:{color}"></div></div>
            <div class="tpct">{pct}%</div>
            <span class="pill {pill}">{sentiment.capitalize()}</span>
          </div>
        </div>"""
    st.markdown(t_html, unsafe_allow_html=True)

    # ── Quotes ──
    st.markdown('<div class="divider"></div><div class="sec-lbl">What users said</div>', unsafe_allow_html=True)
    STARS = {'positive': '★★★★★', 'negative': '★☆☆☆☆', 'mixed': '★★★☆☆'}
    q_html = '<div class="quotes-grid">'
    shown = 0
    for t in themes:
        for q in t.get('top_quotes', [])[:1]:
            if shown >= 4: break
            stars = STARS.get(t.get('sentiment', 'mixed'), '★★★☆☆')
            q_html += f"""
            <div class="qcard">
              <div class="qstars">{stars}</div>
              <div class="qtext">"{q}"</div>
              <div class="qmeta">{t.get('theme_name', '')}</div>
            </div>"""
            shown += 1
        if shown >= 4: break
    q_html += '</div>'
    st.markdown(q_html, unsafe_allow_html=True)

    # ── Actions ──
    st.markdown('<div class="divider"></div><div class="sec-lbl">Recommended actions</div>', unsafe_allow_html=True)
    top_actions = pulse.get('top_3_actions', [])
    theme_actions = [t.get('action_item', '') for t in themes if t.get('action_item')]
    all_actions = (top_actions + theme_actions)[:4]
    a_html = '<div class="actions">'
    for i, action in enumerate(all_actions, 1):
        a_html += f'<div class="ac"><div class="an">0{i}</div><div class="at">{action}</div></div>'
    a_html += '</div>'
    st.markdown(a_html, unsafe_allow_html=True)

    # ── Raw reviews (collapsible) ──
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    with st.expander("📋 View raw review data"):
        if raw is not None and 'rating' in raw.columns:
            total_r = len(raw)
            counts  = raw['rating'].value_counts()
            BAR_C   = {5:'var(--green)', 4:'#5DCAA5', 3:'#EF9F27', 2:'#D85A30', 1:'var(--red)'}
            b_html  = ''
            for star in [5, 4, 3, 2, 1]:
                n   = int(counts.get(star, 0))
                pct = round(n / total_r * 100) if total_r else 0
                b_html += f"""
                <div class="rbar-row">
                  <div class="rbar-lbl">{star}★</div>
                  <div class="rbar-bg"><div class="rbar-fill" style="width:{pct}%;background:{BAR_C[star]}"></div></div>
                  <div class="rbar-n">{n}</div>
                </div>"""
            st.markdown(f'<div style="margin-bottom:1rem"><div class="sec-lbl">Rating distribution — {total_r} reviews</div>{b_html}</div>', unsafe_allow_html=True)

        search = st.text_input("Search reviews", placeholder="Search reviews…", label_visibility="collapsed")

        if clustered is not None and 'theme_label' in clustered.columns:
            df = clustered[['date','rating','review_text','theme_label']].copy()
            df.columns = ['Date','Rating','Review','Theme']
        elif raw is not None:
            df = raw[['date','rating','review_text']].copy()
            df.columns = ['Date','Rating','Review']
            df['Theme'] = ''
        else:
            df = pd.DataFrame()

        if search and not df.empty:
            mask = df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
            df = df[mask]

        if not df.empty:
            rows_html = ''
            for _, row in df.head(50).iterrows():
                rows_html += f"""
                <tr>
                  <td class="star-c">{star_str(row['Rating'])}</td>
                  <td>{str(row['Review'])[:130]}</td>
                  <td><span class="tchip">{str(row.get('Theme',''))[:25]}</span></td>
                  <td style="font-size:10px;color:var(--text3);white-space:nowrap">{str(row['Date'])[:10]}</td>
                </tr>"""
            st.markdown(f"""
            <div class="table-wrap">
              <table class="rtable">
                <thead><tr><th>Rating</th><th>Review</th><th>Theme</th><th>Date</th></tr></thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>""", unsafe_allow_html=True)


# ── DOWNLOAD REPORT ───────────────────────────────────────────────────────────
html_path = os.path.join(OUTPUT_DIR, 'weekly_pulse.html')

st.markdown('<div class="divider"></div><div class="sec-lbl">Download report</div>', unsafe_allow_html=True)

if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None

if file_exists(html_path):
    if st.session_state.pdf_bytes is None:
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            if st.button("⬇ Download PDF", use_container_width=True, type="primary"):
                with st.spinner("Generating PDF…"):
                    import io
                    from xhtml2pdf import pisa
                    html_content = open(html_path, 'r', encoding='utf-8').read()
                    buf = io.BytesIO()
                    pisa.CreatePDF(html_content, dest=buf)
                    st.session_state.pdf_bytes = buf.getvalue()
                st.rerun()
    else:
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.download_button(
                "⬇ Download PDF",
                data=st.session_state.pdf_bytes,
                file_name="weekly_pulse.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
else:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.button("⬇ Download PDF", disabled=True, use_container_width=True, type="primary")
