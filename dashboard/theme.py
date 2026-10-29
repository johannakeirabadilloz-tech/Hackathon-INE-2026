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
