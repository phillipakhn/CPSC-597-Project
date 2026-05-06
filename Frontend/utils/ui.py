import streamlit as st


def inject_security_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(30, 64, 175, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(220, 38, 38, 0.10), transparent 28%),
                #0b1020;
            color: #e5e7eb;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #080d1a 0%, #111827 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }
        .block-container {
            padding-top: 3.5rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #f8fafc;
            letter-spacing: -0.02em;
        }
        .hero-card {
            padding: 1.4rem 1.6rem;
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.90));
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.33);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            color: #38bdf8;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }
        .hero-title {
            color: #f8fafc;
            font-size: 2.0rem;
            line-height: 1.1;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 1rem;
            max-width: 920px;
        }
        .metric-card {
            min-height: 110px;
            padding: 1.05rem 1.1rem;
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.94));
            box-shadow: 0 12px 28px rgba(0,0,0,0.26);
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            color: #f8fafc;
            font-size: 1.72rem;
            font-weight: 800;
            margin-top: 0.28rem;
            overflow-wrap: anywhere;
        }
        .metric-help {
            color: #94a3b8;
            font-size: 0.82rem;
            margin-top: 0.30rem;
        }
        .accent-blue { border-left: 5px solid #38bdf8; }
        .accent-green { border-left: 5px solid #22c55e; }
        .accent-yellow { border-left: 5px solid #eab308; }
        .accent-orange { border-left: 5px solid #f97316; }
        .accent-red { border-left: 5px solid #ef4444; }
        .accent-purple { border-left: 5px solid #a855f7; }
        .section-card {
            padding: 1rem 1.15rem;
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(15, 23, 42, 0.62);
            margin: 0.4rem 0 1rem 0;
        }
        .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 0.35rem;
            margin-bottom: 0.25rem;
            border: 1px solid rgba(148, 163, 184, 0.22);
            background: rgba(15, 23, 42, 0.78);
            color: #e5e7eb;
        }
        .pill-critical { color: #fecaca; border-color: rgba(239, 68, 68, 0.55); background: rgba(127, 29, 29, 0.35); }
        .pill-high { color: #fed7aa; border-color: rgba(249, 115, 22, 0.55); background: rgba(124, 45, 18, 0.35); }
        .pill-medium { color: #fef3c7; border-color: rgba(234, 179, 8, 0.50); background: rgba(113, 63, 18, 0.30); }
        .pill-low { color: #bbf7d0; border-color: rgba(34, 197, 94, 0.45); background: rgba(20, 83, 45, 0.28); }
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.15);
            padding: 0.75rem 0.9rem;
            border-radius: 16px;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 14px;
            overflow: hidden;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 16px;
            padding: 0.35rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            color: #cbd5e1;
            padding: 0.55rem 0.9rem;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(56, 189, 248, 0.14);
            color: #f8fafc;
        }
        div[data-testid="stExpander"] {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.38);
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 12px;
            border: 1px solid rgba(56, 189, 248, 0.35);
            background: rgba(15, 23, 42, 0.70);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, kicker: str = ""):
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">{kicker}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, value, helper: str = "", accent: str = "blue"):
    st.markdown(
        f"""
        <div class="metric-card accent-{accent}">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_panel(title: str, body: str):
    st.markdown(
        f"""
        <div class="section-card">
            <h3 style="margin-top:0; margin-bottom:0.35rem;">{title}</h3>
            <div style="color:#cbd5e1; line-height:1.55;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def severity_pill(label: str):
    cls = {
        "Critical": "pill-critical",
        "High": "pill-high",
        "Medium": "pill-medium",
        "Low": "pill-low",
    }.get(str(label), "")
    return f'<span class="status-pill {cls}">{label}</span>'
