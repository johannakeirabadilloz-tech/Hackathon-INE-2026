"""Adaptación de temas, tarjetas y sidebar del panel Streamlit Dashboard_089."""
from html import escape
import streamlit as st

THEMES = {
    "Claro": dict(bg="#F6F8FB", surface="#FFFFFF", sidebar="#FFFFFF", text="#162334", muted="#56677C", border="#DDE4ED"),
    "Oscuro": dict(bg="#0E1117", surface="#171B22", sidebar="#11151C", text="#F2F6FA", muted="#B0BBCB", border="#334054"),
}


def apply_theme(name):
    t = THEMES[name]
    st.markdown(f"""<style>
    :root, .stApp {{color-scheme:{'dark' if name == 'Oscuro' else 'light'};
        --text-color:{t['text']};--background-color:{t['bg']};--secondary-background-color:{t['surface']};}}
    .stApp, [data-testid="stAppViewContainer"] {{background:{t['bg']};color:{t['text']};}}
    [data-testid="stHeader"] {{background:transparent;}}
    [data-testid="stSidebar"] {{background:{t['sidebar']};border-right:1px solid {t['border']};}}
    .block-container {{max-width:1440px;padding-top:2rem;padding-bottom:3rem;}}
    h1,h2,h3 {{color:{t['text']}!important;letter-spacing:-.025em;}}
    h1 {{font-size:2.35rem!important;line-height:1.15!important;}}
    [data-testid="stMetric"] {{background:{t['surface']};border:1px solid {t['border']};border-radius:10px;padding:18px;min-height:115px;box-shadow:0 6px 20px #00000005;}}
    [data-testid="stMetricLabel"] {{color:{t['muted']};font-size:.8rem;}}
    [data-testid="stMetricValue"] {{color:{t['text']};font-weight:750;}}
    [data-testid="stVerticalBlockBorderWrapper"] {{border-color:{t['border']}!important;}}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{color:{t['muted']}!important;}}
    [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] summary {{color:{t['text']};}}
    [data-testid="stButton"] button, [data-testid="stDownloadButton"] button,
    [data-testid="stLinkButton"] a, [data-testid="stBaseButton-headerNoPadding"],
    [data-testid="stBaseButton-header"], [data-testid="stBaseButton-minimal"],
    [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button {{
        background:{t['surface']}!important;color:{t['text']}!important;
        border:1px solid {t['border']}!important;border-radius:8px;}}
    [data-testid="stDownloadButton"] button p, [data-testid="stButton"] button p,
    [data-testid="stLinkButton"] a p {{color:{t['text']}!important;}}
    button[kind="headerNoPadding"], button[kind="header"], button[kind="minimal"],
    button[kind="headerNoPadding"] span, button[kind="header"] span {{color:{t['text']}!important;}}
    button:focus-visible, a:focus-visible {{outline:2px solid #D65D91!important;outline-offset:3px;}}
    [data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover,
    [data-testid="stLinkButton"] a:hover {{border-color:#D65D91!important;background:{t['border']}!important;}}
    [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="input"] input,
    [data-baseweb="popover"] > div, [data-baseweb="menu"],
    [role="listbox"], [role="option"] {{background:{t['surface']}!important;color:{t['text']}!important;}}
    [data-baseweb="select"] input, [data-baseweb="select"] svg,
    [data-baseweb="select"] [role="button"], [data-baseweb="select"] span {{color:{t['text']};fill:currentColor;}}
    [role="option"]:hover, [role="option"][aria-selected="true"] {{background:{t['border']}!important;}}
    [data-baseweb="tag"] {{background:#A51D57!important;color:#FFFFFF!important;}}
    [data-baseweb="tag"] span, [data-baseweb="tag"] svg {{color:#FFFFFF!important;}}
    [data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"],
    [data-testid="stMultiSelect"] .react-aria-ComboBox > [role="group"] {{
        background:{t['surface']}!important;color:{t['text']}!important;border-color:{t['border']}!important;}}
    [data-testid="stSelectbox"] input, [data-testid="stMultiSelect"] input {{
        background:transparent!important;color:{t['text']}!important;caret-color:{t['text']};}}
    [data-testid="stSelectbox"] button, [data-testid="stMultiSelect"] button {{
        background:transparent!important;color:{t['text']}!important;}}
    [data-testid="stSelectbox"] svg, [data-testid="stMultiSelect"] svg {{color:{t['text']}!important;}}
    [data-testid="stMultiSelect"] [data-tag] {{background:#A51D57!important;color:white!important;}}
    [data-testid="stMultiSelect"] [data-tag] button, [data-testid="stMultiSelect"] [data-tag] svg {{color:white!important;}}
    .react-aria-Popover, .react-aria-ListBox, [data-rac][data-trigger="ComboBox"] {{
        background:{t['surface']}!important;color:{t['text']}!important;border-color:{t['border']}!important;}}
    [data-baseweb="radio"] > div:first-child {{background:{t['surface']};border-color:{t['muted']};}}
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"],
    [data-testid="stSlider"] [data-testid="stThumbValue"] {{color:{t['text']}!important;}}
    [data-testid="stTable"] {{overflow-x:auto;border:1px solid {t['border']};border-radius:9px;background:{t['surface']};}}
    [data-testid="stTable"] table {{color:{t['text']}!important;background:{t['surface']}!important;width:100%;}}
    [data-testid="stTable"] th {{background:{t['sidebar']}!important;color:{t['text']}!important;font-weight:700;}}
    [data-testid="stTable"] td {{background:{t['surface']}!important;color:{t['text']}!important;}}
    [data-testid="stTable"] th, [data-testid="stTable"] td {{border-color:{t['border']}!important;padding:.65rem .75rem;}}
    [data-testid="stTable"] tbody tr:nth-child(even) td {{background:{t['bg']}!important;}}
    [data-testid="stTable"] a {{color:{t['text']}!important;}}
    .eyebrow {{color:#B3336D;font-size:.73rem;font-weight:800;letter-spacing:.15em;margin:0 0 .7rem;}}
    .intro {{color:{t['muted']};font-size:1.02rem;max-width:850px;line-height:1.65;margin-bottom:1.5rem;}}
    .brand {{font-size:1.1rem;font-weight:800;letter-spacing:-.03em;margin:.4rem 0 .15rem;color:{t['text']};}}
    .brand span {{color:#B3336D;}}
    .brand-note {{font-size:.75rem;color:{t['muted']};margin-bottom:1.5rem;}}
    .profile-card {{border:1px solid {t['border']};border-top:4px solid var(--accent);border-radius:10px;background:{t['surface']};padding:17px;min-height:235px;}}
    .profile-label {{font-weight:800;font-size:.74rem;min-height:36px;color:var(--accent);}}
    .profile-value {{font-size:2rem;font-weight:800;color:{t['text']};margin:.4rem 0;}}
    .profile-sub {{font-size:.78rem;color:{t['muted']};line-height:1.6;}}
    .source-note {{font-size:.76rem;color:{t['muted']};border-top:1px solid {t['border']};padding-top:1rem;margin-top:2rem;}}
    @media(max-width:640px) {{h1{{font-size:1.8rem!important;}}.block-container{{padding:1.3rem 1rem;}}}}
    </style>""", unsafe_allow_html=True)
    return t


def profile_card(number, name, color, value, change, share):
    st.markdown(f"""<div class="profile-card" style="--accent:{color}">
    <div class="profile-label">{number:02d} / {escape(name)}</div>
    <div class="profile-value">{value:.1f}%</div>
    <div class="profile-sub">Participación entre especificados<br>{escape(change)}<br>
    <strong>{share:.1f}%</strong> de la lista nominal analizada en 2024</div></div>""", unsafe_allow_html=True)
