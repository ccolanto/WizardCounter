import streamlit as st
import pandas as pd
import altair as alt
import json
import os
import re
import requests
from datetime import datetime
from pathlib import Path

# Google Gemini API
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(page_title="The Grand Fardini", page_icon="🧙", layout="wide")

# Initialize dark_mode early (before CSS that uses it)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Default to dark mode to match system default

# Generate theme-specific CSS based on toggle state
if st.session_state.dark_mode:
    # Dark mode CSS
    theme_css = """
    <style>
        /* ===== DARK MODE THEME ===== */
        :root {
            --text-primary: #fafafa;
            --text-secondary: #ccc;
            --bg-primary: #0e1117;
            --bg-secondary: #262730;
            --bg-hover: #3d3d4d;
            --border-color: #444;
            --accent: #ff4b4b;
        }
        
        /* Base backgrounds */
        .stApp, [data-testid="stAppViewContainer"], .main, [data-testid="stHeader"] { background-color: #0e1117 !important; }
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #262730 !important; }
        
        /* Text colors */
        body, .stApp, p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, div, li, td, th,
        [data-testid="stSidebar"] *, .stToggle label span, [data-testid="stWidgetLabel"] { color: #fafafa !important; }
        
        /* Inputs */
        input, textarea, select, .stTextInput input, .stNumberInput input, .stSelectbox select,
        [data-baseweb="input"] input, .stNumberInput > div > div > input {
            background-color: #262730 !important; color: #fafafa !important; border-color: #444 !important;
        }
        
        /* Selectbox */
        .stSelectbox > div > div, .stSelectbox [data-baseweb="select"] > div, .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] span, .stSelectbox [data-baseweb="select"] div { background-color: #262730 !important; color: #fafafa !important; }
        [data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul, [data-baseweb="popover"] li { background-color: #262730 !important; color: #fafafa !important; }
        [data-baseweb="popover"] li:hover { background-color: #3d3d4d !important; }
        
        /* Buttons */
        .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) { background-color: #262730 !important; color: #fafafa !important; border-color: #444 !important; }
        [data-testid="stSidebar"] .stButton > button, [data-testid="stSidebar"] .stButton { width: 100% !important; min-width: 100% !important; }
        [data-testid="stSidebar"] [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; }
        
        /* Radio/Tabs */
        .stRadio > div > label { background: #262730 !important; color: #fafafa !important; }
        .stRadio > div > label:hover { background: #3d3d4d !important; }
        .stRadio [role="radiogroup"], .stRadio > div { background-color: transparent !important; }
        .stRadio [role="radio"], .stRadio > div > label, .stRadio > div > div > label { background-color: #262730 !important; color: #fafafa !important; border-color: #444 !important; }
        .stRadio [role="radio"]:hover, .stRadio > div > label:hover { background-color: #3d3d4d !important; }
        .stRadio [role="radio"][aria-checked="true"], .stRadio > div > label[data-checked="true"], .stRadio > div > label:has(input:checked) { background-color: #ff4b4b !important; color: #ffffff !important; }
        
        /* Hide radio circles */
        .stRadio input[type="radio"], .stRadio > div > label > div:first-child, .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; width: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }
        
        /* Expanders */
        .streamlit-expanderHeader { background-color: #262730 !important; color: #fafafa !important; }
        .streamlit-expanderContent { background-color: #1a1a2e !important; }
        
        /* Data frames/Tables */
        .stDataFrame, .stDataFrame td, .stDataFrame th, table, tr, td, th, .stTable, .stTable td, .stTable th { background-color: #262730 !important; color: #fafafa !important; border-color: #444 !important; }
        [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div, [data-testid="stDataFrame"] iframe { background-color: #262730 !important; }
        .dvn-scroller, .gdg-style, [class*="glideDataEditor"], [data-testid="stDataFrame"] [class*="cell"], [data-testid="stDataFrame"] [role="gridcell"], [data-testid="stDataFrame"] [role="columnheader"] { background-color: #262730 !important; color: #fafafa !important; }
        [data-testid="stDataFrame"] span, [data-testid="stDataFrame"] div { color: #fafafa !important; }
        
        /* Toggle */
        .stToggle > label > div, [data-baseweb="checkbox"] > div:first-child { background-color: #444 !important; border: 2px solid #666 !important; }
        .stToggle > label > div[data-checked="true"], [data-baseweb="checkbox"] > div:first-child[aria-checked="true"], [role="checkbox"][aria-checked="true"] { background-color: #ff4b4b !important; border-color: #ff4b4b !important; }
        [data-baseweb="checkbox"] > div:first-child > div, .stToggle > label > div > div { background-color: #fafafa !important; }
        
        /* Number inputs */
        .stNumberInput button, .stNumberInput [data-testid="stNumberInputStepUp"], .stNumberInput [data-testid="stNumberInputStepDown"] { background-color: #262730 !important; color: #fafafa !important; border-color: #444 !important; }
        .stNumberInput button:hover { background-color: #3d3d4d !important; }
        .stNumberInput button svg { fill: #fafafa !important; stroke: #fafafa !important; }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"], .stTabs [data-baseweb="tab"] { background-color: #262730 !important; color: #fafafa !important; }
        .stTabs [data-baseweb="tab"]:hover { background-color: #3d3d4d !important; }
        .stTabs [aria-selected="true"] { background-color: #0e1117 !important; color: #fafafa !important; }
        
        /* Containers */
        [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], .element-container, .stMarkdown, [data-testid="column"] { background-color: transparent !important; }
        [data-testid="stMetric"], [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] { background-color: transparent !important; color: #fafafa !important; }
        
        /* Charts */
        .stPlotlyChart, .js-plotly-plot, .plotly, .plot-container, .vega-embed, [data-testid="stVegaLiteChart"] { background-color: #0e1117 !important; }
        .js-plotly-plot .plotly .bg { fill: #0e1117 !important; }
        .vega-embed .vega-bindings { color: #fafafa !important; }
        
        .stContainer, [data-testid="stExpander"], [data-testid="stForm"] { background-color: #0e1117 !important; }
        .stAlert { border-color: #444 !important; }
    </style>
    """
else:
    # Light mode CSS
    theme_css = """
    <style>
        /* ===== LIGHT MODE THEME ===== */
        :root {
            --text-primary: #262730;
            --text-secondary: #555;
            --bg-primary: #ffffff;
            --bg-secondary: #f0f2f6;
            --bg-hover: #e0e2e6;
            --border-color: #ddd;
            --accent: #ff4b4b;
        }
        
        /* Base backgrounds */
        .stApp, [data-testid="stAppViewContainer"], .main, [data-testid="stHeader"] { background-color: #ffffff !important; }
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #f0f2f6 !important; }
        
        /* Text colors */
        body, .stApp, p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, div, li, td, th,
        [data-testid="stSidebar"] *, .stToggle label span, [data-testid="stWidgetLabel"] { color: #262730 !important; }
        
        /* Sidebar button text - force black */
        [data-testid="stSidebar"] button, [data-testid="stSidebar"] button *, [data-testid="stSidebar"] .stButton button * { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
        
        /* Inputs */
        input, textarea, select, .stTextInput input, .stNumberInput input, .stSelectbox select,
        [data-baseweb="input"] input, .stNumberInput > div > div > input {
            background-color: #ffffff !important; color: #262730 !important; border: 1px solid #888 !important; border-radius: 4px !important;
        }
        
        /* Sidebar inputs */
        [data-testid="stSidebar"] .stTextInput > div > div, [data-testid="stSidebar"] [data-baseweb="base-input"], [data-testid="stSidebar"] [data-baseweb="input"] { background-color: #ffffff !important; border: 1px solid #555 !important; border-radius: 4px !important; }
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] .stTextInput input { background-color: #ffffff !important; color: #000000 !important; -webkit-text-fill-color: #000000 !important; border: none !important; }
        
        /* Selectbox */
        .stSelectbox > div > div, .stSelectbox [data-baseweb="select"] > div, .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] span, .stSelectbox [data-baseweb="select"] div { background-color: #ffffff !important; color: #262730 !important; }
        [data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul, [data-baseweb="popover"] li { background-color: #ffffff !important; color: #262730 !important; }
        [data-baseweb="popover"] li:hover { background-color: #f0f2f6 !important; }
        
        /* Secondary buttons */
        .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) { background-color: #e8e8e8 !important; color: #1a1a1a !important; border: 2px solid #999 !important; }
        .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover { background-color: #d0d0d0 !important; border-color: #666 !important; }
        
        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton > button { background-color: #d8d8d8 !important; color: #000000 !important; border: 2px solid #888 !important; font-weight: 600 !important; width: 100% !important; min-width: 100% !important; }
        [data-testid="stSidebar"] .stButton { width: 100% !important; }
        [data-testid="stSidebar"] [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; }
        [data-testid="stSidebar"] .stButton > button:hover { background-color: #c0c0c0 !important; border-color: #555 !important; }
        [data-testid="stSidebar"] .stButton > button[kind="primary"], [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] { background-color: #ff4b4b !important; color: #ffffff !important; border: 2px solid #cc0000 !important; }
        
        /* Primary button text white */
        [data-testid="stSidebar"] .stButton > button[kind="primary"] *, .stButton > button[kind="primary"] *, .stButton > button[data-testid="baseButton-primary"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
        
        /* Disabled buttons */
        .stButton > button:disabled, .stButton > button[disabled] { background-color: #e0e0e0 !important; color: #888888 !important; border: 1px solid #bbb !important; opacity: 0.7 !important; cursor: not-allowed !important; }
        .stButton > button:disabled *, .stButton > button[disabled] * { color: #888888 !important; -webkit-text-fill-color: #888888 !important; }
        
        /* Radio/Tabs */
        .stRadio > div > label { background: #f0f2f6 !important; color: #262730 !important; }
        .stRadio > div > label:hover { background: #e0e2e6 !important; }
        .stRadio [role="radiogroup"], .stRadio > div { background-color: transparent !important; }
        .stRadio [role="radio"], .stRadio > div > label, .stRadio > div > div > label { background-color: #f0f2f6 !important; color: #262730 !important; border-color: #ddd !important; }
        .stRadio [role="radio"]:hover, .stRadio > div > label:hover { background-color: #e0e2e6 !important; }
        .stRadio [role="radio"][aria-checked="true"], .stRadio > div > label[data-checked="true"], .stRadio > div > label:has(input:checked) { background-color: #ff4b4b !important; color: #ffffff !important; }
        
        /* Hide radio circles */
        .stRadio input[type="radio"], .stRadio > div > label > div:first-child, .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; width: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }
        
        /* Expanders */
        .streamlit-expanderHeader { background-color: #f0f2f6 !important; color: #262730 !important; }
        .streamlit-expanderContent { background-color: #ffffff !important; }
        
        /* Data frames/Tables */
        .stDataFrame, .stDataFrame td, .stDataFrame th, table, tr, td, th, .stTable, .stTable td, .stTable th { background-color: #ffffff !important; color: #262730 !important; border-color: #ddd !important; }
        [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div, [data-testid="stDataFrame"] iframe { background-color: #ffffff !important; }
        .dvn-scroller, .gdg-style, [class*="glideDataEditor"], [data-testid="stDataFrame"] [class*="cell"], [data-testid="stDataFrame"] [role="gridcell"], [data-testid="stDataFrame"] [role="columnheader"] { background-color: #ffffff !important; color: #262730 !important; }
        [data-testid="stDataFrame"] span, [data-testid="stDataFrame"] div { color: #262730 !important; }
        
        /* Toggle */
        .stToggle > label > div, [data-baseweb="checkbox"] > div:first-child { background-color: #ccc !important; border: 2px solid #999 !important; }
        .stToggle > label > div[data-checked="true"], [data-baseweb="checkbox"] > div:first-child[aria-checked="true"], [role="checkbox"][aria-checked="true"] { background-color: #ff4b4b !important; border-color: #ff4b4b !important; }
        [data-baseweb="checkbox"] > div:first-child > div, .stToggle > label > div > div { background-color: #ffffff !important; }
        
        /* Number inputs */
        .stNumberInput button, .stNumberInput [data-testid="stNumberInputStepUp"], .stNumberInput [data-testid="stNumberInputStepDown"] { background-color: #f0f2f6 !important; color: #262730 !important; border-color: #ddd !important; }
        .stNumberInput button:hover { background-color: #e0e2e6 !important; }
        .stNumberInput button svg { fill: #262730 !important; stroke: #262730 !important; }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"], .stTabs [data-baseweb="tab"] { background-color: #f0f2f6 !important; color: #262730 !important; }
        .stTabs [data-baseweb="tab"]:hover { background-color: #e0e2e6 !important; }
        .stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #262730 !important; }
        
        /* Containers */
        [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], .element-container, .stMarkdown, [data-testid="column"] { background-color: transparent !important; }
        [data-testid="stMetric"], [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] { background-color: transparent !important; color: #262730 !important; }
        
        /* Charts */
        .stPlotlyChart, .js-plotly-plot, .plotly, .plot-container, .vega-embed, [data-testid="stVegaLiteChart"] { background-color: #ffffff !important; }
        .js-plotly-plot .plotly .bg { fill: #ffffff !important; }
        .vega-embed .vega-bindings { color: #262730 !important; }
        
        .stContainer, [data-testid="stExpander"], [data-testid="stForm"] { background-color: #ffffff !important; }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# Always-applied CSS (layout, sizing, touch targets)
st.markdown("""
<style>
    /* ===== SIDEBAR COLLAPSE BUTTON ===== */
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"], button[kind="header"], [data-testid="baseButton-header"],
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarNav"] button, section[data-testid="stSidebar"] > div:first-child button {
        opacity: 1 !important; visibility: visible !important; display: flex !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button { min-height: 54px !important; font-size: 1.1rem !important; padding: 0.75rem 1.5rem !important; border-radius: 12px !important; margin: 6px 0 !important; font-weight: 500 !important; color: var(--text-primary, inherit) !important; }
    .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] { min-height: 60px !important; font-size: 1.25rem !important; font-weight: 600 !important; color: white !important; }
    .stButton > button[kind="secondary"], .stButton > button[data-testid="baseButton-secondary"] { color: var(--text-primary, inherit) !important; background: var(--bg-secondary, #f0f2f6) !important; border: 1px solid var(--border-color, #ddd) !important; }
    .stButton > button[kind="secondary"]:hover { background: var(--bg-hover, #e0e2e6) !important; }
    button:active, .stButton > button:active { transform: scale(0.97) !important; transition: transform 0.1s !important; }
    
    /* ===== NUMBER INPUTS ===== */
    .stNumberInput > div > div > input { font-size: 1.5rem !important; height: 54px !important; text-align: center !important; font-weight: 600 !important; color: var(--text-primary, inherit) !important; }
    .stNumberInput button { min-width: 48px !important; min-height: 48px !important; display: flex !important; align-items: center !important; justify-content: center !important; padding: 0 !important; }
    .stNumberInput button svg { width: 18px !important; height: 18px !important; position: relative !important; top: -5px !important; }
    .stNumberInput [data-testid="stNumberInputStepUp"], .stNumberInput [data-testid="stNumberInputStepDown"] { width: 48px !important; height: 48px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    
    /* ===== RADIO BUTTONS (Tab Style) ===== */
    .stRadio > div { gap: 8px !important; }
    .stRadio > div > label { padding: 14px 24px !important; font-size: 1.15rem !important; border-radius: 12px !important; min-height: 52px !important; display: flex !important; align-items: center !important; justify-content: center !important; background: var(--bg-secondary, #f0f2f6) !important; border: 2px solid transparent !important; transition: all 0.15s ease !important; font-weight: 500 !important; color: var(--text-primary, inherit) !important; }
    .stRadio > div > label:hover { background: var(--bg-hover, #e0e2e6) !important; transform: scale(1.02) !important; }
    .stRadio > div > label[data-checked="true"], .stRadio > div > label:has(input:checked) { background: #ff4b4b !important; color: white !important; border-color: #ff4b4b !important; }
    
    /* ===== SELECT BOXES ===== */
    .stSelectbox > div > div { min-height: 52px !important; font-size: 1.1rem !important; color: var(--text-primary, inherit) !important; }
    .stSelectbox [data-baseweb="select"] { min-height: 52px !important; }
    
    /* ===== TEXT INPUTS ===== */
    .stTextInput > div > div > input { min-height: 52px !important; font-size: 1.1rem !important; padding: 0 12px !important; line-height: 52px !important; display: flex !important; align-items: center !important; color: var(--text-primary, inherit) !important; }
    [data-testid="stSidebar"] .stTextInput > div > div > input { min-height: 44px !important; height: 44px !important; padding: 0 12px !important; padding-bottom: 4px !important; line-height: 40px !important; }
    
    /* ===== CHECKBOXES ===== */
    .stCheckbox > label { padding: 10px 0 !important; min-height: 48px !important; display: flex !important; align-items: center !important; }
    .stCheckbox > label > span { font-size: 1.1rem !important; }
    .stCheckbox > label > div[data-testid="stCheckbox"] { width: 26px !important; height: 26px !important; }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader { font-size: 1.15rem !important; min-height: 52px !important; padding: 12px !important; color: var(--text-primary, inherit) !important; }
    
    /* ===== LAYOUT ===== */
    [data-testid="column"] { padding: 0 10px !important; }
    .stForm > div > div { margin-bottom: 1rem !important; }
    .block-container { padding: 1rem 2rem 3rem 2rem !important; }
    
    /* ===== TYPOGRAPHY ===== */
    h2, .stSubheader { font-size: 1.6rem !important; margin-top: 1.5rem !important; }
    h3 { font-size: 1.3rem !important; }
    .stNumberInput label, .stTextInput label, .stSelectbox label { font-size: 1.1rem !important; font-weight: 600 !important; color: var(--text-primary, inherit) !important; }
    .stMarkdown, .stText, p, span, label { color: var(--text-primary, inherit) !important; }
    .stCaption, [data-testid="stCaption"] { color: var(--text-secondary, #555) !important; }
    
    /* ===== DATA TABLES ===== */
    .stDataFrame td, .stDataFrame th { font-size: 1rem !important; padding: 12px 8px !important; }
    
    /* ===== ALERTS ===== */
    .stAlert, .stInfo, .stWarning, .stSuccess, .stError { padding: 16px !important; font-size: 1.05rem !important; border-radius: 10px !important; }
    .stAlert p, .stInfo p, .stWarning p, .stSuccess p, .stError p { color: inherit !important; }
    
    /* ===== MODALS ===== */
    [data-testid="stModal"] button { min-height: 50px !important; min-width: 50px !important; }
    
    /* ===== SLIDERS ===== */
    .stSlider > div { padding: 10px 0 !important; }
    .stSlider [data-testid="stThumbValue"] { font-size: 1.1rem !important; }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button { min-height: 54px !important; font-size: 1.1rem !important; }
    
    /* ===== COLOR PICKER ===== */
    .stColorPicker > div { min-height: 48px !important; }
    [data-testid="stSidebar"] .stColorPicker { margin: 0 !important; padding: 0 !important; }
    [data-testid="stSidebar"] .stColorPicker > div { min-height: 36px !important; height: 36px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    [data-testid="stSidebar"] .stColorPicker label { display: none !important; }
    
    /* ===== SIDEBAR LAYOUT ===== */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { align-items: center !important; }
    [data-testid="stSidebar"] [data-testid="column"] { display: flex !important; flex-direction: column !important; justify-content: center !important; align-items: center !important; }
    [data-testid="stSidebar"] * { color: var(--text-primary, inherit); }
    .player-name-cell { display: flex !important; align-items: center !important; height: 36px !important; font-weight: 500 !important; margin: 0 !important; padding: 0 !important; }
    
    /* Sidebar button sizing */
    [data-testid="stSidebar"] button[kind="secondary"]:has(p:contains("💾")), [data-testid="stSidebar"] .stButton > button { min-height: 44px !important; min-width: 44px !important; font-size: 1.3rem !important; padding: 8px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    [data-testid="stSidebar"] [data-testid="column"] .stButton { display: flex !important; justify-content: center !important; align-items: center !important; margin: 0 !important; padding: 0 !important; width: auto !important; max-width: none !important; }
    [data-testid="stSidebar"] [data-testid="column"] .stButton > button:not([data-baseweb="button"]) { min-height: 36px !important; min-width: 36px !important; }
    
    /* Sidebar horizontal button layout */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton { width: 100% !important; flex: 1 !important; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button { height: 44px !important; min-height: 44px !important; max-height: 44px !important; width: 100% !important; min-width: 100% !important; display: flex !important; align-items: center !important; justify-content: center !important; box-sizing: border-box !important; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex: 1 1 0 !important; width: 0 !important; min-width: 0 !important; }
    
    /* Button inner element fixes */
    [data-testid="stSidebar"] [data-testid="column"] .stButton > button > div, [data-testid="stSidebar"] [data-testid="column"] .stButton > button > div > p, [data-testid="stSidebar"] [data-testid="column"] .stButton > button p { max-width: none !important; width: auto !important; margin: 0 !important; padding: 0 !important; text-align: center !important; display: flex !important; align-items: center !important; justify-content: center !important; flex: none !important; }
    .stButton [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] .stButton [data-testid="stMarkdownContainer"] { width: auto !important; max-width: none !important; min-width: 0 !important; display: flex !important; justify-content: center !important; align-items: center !important; }
    .stButton [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] .stButton [data-testid="stMarkdownContainer"] p { width: auto !important; max-width: none !important; margin: 0 !important; text-align: center !important; }
    [data-testid="stSidebar"] [data-testid="column"] .stButton button div[class*="emotion-cache"] { width: auto !important; max-width: none !important; }
</style>
""", unsafe_allow_html=True)

# Save directory for game files
SAVE_DIR = Path(__file__).parent / "saved_games"
SAVE_DIR.mkdir(exist_ok=True)

# API key config files (stored locally, NOT committed to git)
NVIDIA_API_KEY_FILE = Path(__file__).parent / ".nvidia_api_key"
GEMINI_API_KEY_FILE = Path(__file__).parent / ".gemini_api_key"
# Legacy file for backward compatibility
API_KEY_FILE = Path(__file__).parent / ".api_key"

def load_saved_api_key(provider="nvidia"):
    """Load the API key from the config file if it exists."""
    if provider == "gemini":
        key_file = GEMINI_API_KEY_FILE
    else:
        key_file = NVIDIA_API_KEY_FILE
        # Check legacy file if new file doesn't exist
        if not key_file.exists() and API_KEY_FILE.exists():
            key_file = API_KEY_FILE
    
    if key_file.exists():
        try:
            with open(key_file, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    return ""

def save_api_key(api_key, provider="nvidia"):
    """Save the API key to a config file."""
    if provider == "gemini":
        key_file = GEMINI_API_KEY_FILE
    else:
        key_file = NVIDIA_API_KEY_FILE
    
    try:
        with open(key_file, 'w') as f:
            f.write(api_key)
    except Exception:
        pass

# API Provider Configuration
API_PROVIDERS = ["Google Gemini (Free)", "NVIDIA"]
DEFAULT_PROVIDER = "Google Gemini (Free)"

# NVIDIA API Configuration
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODELS = {
    "DeepSeek-R1 (Slower, More Creative)": "deepseek-ai/deepseek-r1",
    "Llama 3.1 70B (Fast)": "meta/llama-3.1-70b-instruct",
    "Llama 3.1 8B (Fastest)": "meta/llama-3.1-8b-instruct",
}
DEFAULT_NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

# Google Gemini API Configuration
GEMINI_MODELS = {
    "Gemini 3.0 Flash - Best (20/day)": "gemini-3-flash-preview",
    "Gemini 2.5 Flash - Smart (20/day)": "gemini-2.5-flash",
    "Gemini 2.5 Flash Lite - Fast (20/day)": "gemini-2.5-flash-lite",
    "Gemma 3 27B - Unlimited (Lower Quality)": "gemma-3-27b-it",
}
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# Default colors for new players
DEFAULT_COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"]

# Initialize session state with defaults (dark_mode initialized earlier before CSS)
SESSION_DEFAULTS = {
    'players': [], 'current_round': 1, 'game_data': {}, 'game_started': False,
    'max_rounds': 0, 'current_save_file': None, 'player_colors': {}, 'active_tab': 0,
    'starting_dealer_index': 0, 'shot_players': [], 'round_roasts': {},
    'api_provider': DEFAULT_PROVIDER, 'enable_roasts': False, 'api_verified': False,
    'selected_nvidia_model': DEFAULT_NVIDIA_MODEL, 'selected_gemini_model': DEFAULT_GEMINI_MODEL,
    'game_finished': False, 'show_celebration': False, 'manual_roast': {},
    'game_summary': None, 'game_stats': None,
}
for key, default in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default
# Load API keys if not already loaded
if 'nvidia_api_key' not in st.session_state:
    st.session_state.nvidia_api_key = load_saved_api_key("nvidia")
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = load_saved_api_key("gemini")

def get_theme_colors():
    """Return theme-aware colors based on current dark_mode setting."""
    if st.session_state.dark_mode:
        return {
            'bg_primary': '#0e1117', 'bg_secondary': '#262730', 'bg_hover': '#3d3d4d',
            'text_primary': '#fafafa', 'text_secondary': '#ccc', 'border': '#444',
            'popup_bg': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
            'card_bg': 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
            'roast_bg': 'linear-gradient(135deg, #2d1b69 0%, #11998e 100%)',
            'banner_bg': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            'chart_grid': '#444', 'stat_text': '#98D8C8',
        }
    else:
        return {
            'bg_primary': '#ffffff', 'bg_secondary': '#f0f2f6', 'bg_hover': '#e0e2e6',
            'text_primary': '#262730', 'text_secondary': '#555', 'border': '#ddd',
            'popup_bg': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #dee2e6 100%)',
            'card_bg': 'linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%)',
            'roast_bg': 'linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%)',
            'banner_bg': 'linear-gradient(135deg, #fff5f5 0%, #ffe3e3 100%)',
            'chart_grid': '#ddd', 'stat_text': '#495057',
        }

def calculate_score(bid, tricks):
    """Calculate score for a round based on bid and tricks won."""
    if bid == tricks:
        return 20 + (10 * tricks)
    else:
        return -10 * abs(bid - tricks)

def get_total_scores():
    """Calculate total scores for all players (only completed rounds, not current round unless game is finished)."""
    totals = {player: 0 for player in st.session_state.players}
    current_round = st.session_state.get('current_round', 1)
    game_finished = st.session_state.get('game_finished', False)
    
    for round_num, round_data in st.session_state.game_data.items():
        if round_num < current_round or game_finished:
            for player, data in round_data.items():
                if data['bid'] is not None and data['tricks'] is not None:
                    totals[player] += calculate_score(data['bid'], data['tricks'])
    return totals

def get_shot_players(round_num):
    """Return list of players who need to take a shot (off by 2+ tricks)."""
    shot_players = []
    for player in st.session_state.players:
        data = st.session_state.game_data.get(round_num, {}).get(player, {'bid': None, 'tricks': None})
        bid, tricks = data.get('bid', 0) or 0, data.get('tricks', 0) or 0
        if abs(bid - tricks) >= 2:
            shot_players.append(player)
    return shot_players

def init_round_data(round_num):
    """Initialize game data for a round if it doesn't exist."""
    if round_num not in st.session_state.game_data:
        st.session_state.game_data[round_num] = {
            player: {'bid': None, 'tricks': None} for player in st.session_state.players
        }

def analyze_game_stats():
    """Analyze the full game and return comprehensive statistics."""
    max_rounds = st.session_state.max_rounds
    players = st.session_state.players
    
    # Build running totals per round for each player
    running_totals = {p: [0] for p in players}  # Start at 0
    round_scores = {p: [] for p in players}
    round_standings = []  # List of standings after each round
    
    for r in range(1, max_rounds + 1):
        if r in st.session_state.game_data:
            round_standing = {}
            for p in players:
                data = st.session_state.game_data[r].get(p, {'bid': None, 'tricks': None})
                bid = data['bid']
                tricks = data['tricks']
                if bid is not None and tricks is not None:
                    score = calculate_score(bid, tricks)
                    round_scores[p].append(score)
                    running_totals[p].append(running_totals[p][-1] + score)
                else:
                    round_scores[p].append(0)
                    running_totals[p].append(running_totals[p][-1])
                round_standing[p] = running_totals[p][-1]
            round_standings.append(sorted(round_standing.items(), key=lambda x: x[1], reverse=True))
    
    stats = {
        'running_totals': running_totals,
        'round_scores': round_scores,
        'round_standings': round_standings,
        'analysis': {}
    }
    
    # Calculate interesting statistics for each player
    for p in players:
        scores = round_scores[p]
        totals = running_totals[p]
        
        # Best and worst rounds
        if scores:
            best_round_score = max(scores)
            worst_round_score = min(scores)
            best_round = scores.index(best_round_score) + 1
            worst_round = scores.index(worst_round_score) + 1
        else:
            best_round_score = worst_round_score = best_round = worst_round = 0
        
        # Correct bids count
        correct_bids = sum(1 for s in scores if s > 0)
        
        # Biggest 3-round jump and drop
        max_3round_jump = 0
        max_3round_drop = 0
        jump_rounds = (0, 0)
        drop_rounds = (0, 0)
        
        if len(totals) >= 4:
            for i in range(len(totals) - 3):
                change = totals[i+3] - totals[i]
                if change > max_3round_jump:
                    max_3round_jump = change
                    jump_rounds = (i+1, i+3)
                if change < max_3round_drop:
                    max_3round_drop = change
                    drop_rounds = (i+1, i+3)
        
        # Lead changes - how many times they took/lost the lead
        times_in_lead = 0
        lead_changes_involving = 0
        was_leading = False
        
        for i, standing in enumerate(round_standings):
            currently_leading = standing[0][0] == p if standing else False
            if currently_leading:
                times_in_lead += 1
            if currently_leading != was_leading:
                lead_changes_involving += 1
            was_leading = currently_leading
        
        # Comeback or choke stats
        if len(round_standings) >= 2:
            first_standing = [x[0] for x in round_standings[0]]
            last_standing = [x[0] for x in round_standings[-1]]
            start_rank = first_standing.index(p) + 1 if p in first_standing else len(players)
            end_rank = last_standing.index(p) + 1 if p in last_standing else len(players)
            rank_change = start_rank - end_rank  # Positive = improved
        else:
            start_rank = end_rank = rank_change = 0
        
        # Hot and cold streaks
        current_streak = 0
        max_hot_streak = 0
        max_cold_streak = 0
        for s in scores:
            if s > 0:
                if current_streak >= 0:
                    current_streak += 1
                else:
                    current_streak = 1
                max_hot_streak = max(max_hot_streak, current_streak)
            else:
                if current_streak <= 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                max_cold_streak = max(max_cold_streak, abs(current_streak))
        
        stats['analysis'][p] = {
            'final_score': totals[-1] if totals else 0,
            'best_round': best_round,
            'best_round_score': best_round_score,
            'worst_round': worst_round,
            'worst_round_score': worst_round_score,
            'correct_bids': correct_bids,
            'total_rounds': len(scores),
            'accuracy': round(correct_bids / len(scores) * 100, 1) if scores else 0,
            'max_3round_jump': max_3round_jump,
            'jump_rounds': jump_rounds,
            'max_3round_drop': max_3round_drop,
            'drop_rounds': drop_rounds,
            'times_in_lead': times_in_lead,
            'lead_changes': lead_changes_involving,
            'start_rank': start_rank,
            'end_rank': end_rank,
            'rank_change': rank_change,
            'max_hot_streak': max_hot_streak,
            'max_cold_streak': max_cold_streak,
        }
    
    return stats

def generate_game_summary(stats):
    """Use LLM to generate an engaging end-game summary."""
    if not st.session_state.api_verified:
        return None
    
    players = st.session_state.players
    analysis = stats['analysis']
    
    # Build comprehensive stats summary for LLM
    player_summaries = []
    for p in players:
        a = analysis[p]
        summary = f"""{p}:
- Final: #{a['end_rank']} with {a['final_score']} pts
- Accuracy: {a['correct_bids']}/{a['total_rounds']} correct ({a['accuracy']}%)
- Best round: R{a['best_round']} (+{a['best_round_score']} pts), Worst: R{a['worst_round']} ({a['worst_round_score']} pts)
- Biggest 3-round jump: +{a['max_3round_jump']} (R{a['jump_rounds'][0]}-R{a['jump_rounds'][1]})
- Biggest 3-round drop: {a['max_3round_drop']} (R{a['drop_rounds'][0]}-R{a['drop_rounds'][1]})
- Times leading: {a['times_in_lead']} rounds, Lead changes: {a['lead_changes']}
- Started #{a['start_rank']}, Finished #{a['end_rank']} (moved {'+' if a['rank_change'] > 0 else ''}{a['rank_change']} spots)
- Hot streak: {a['max_hot_streak']} correct in a row, Cold streak: {a['max_cold_streak']} misses in a row"""
        player_summaries.append(summary)
    
    # Find superlatives
    superlatives = []
    
    # Best accuracy
    best_accuracy = max(players, key=lambda p: analysis[p]['accuracy'])
    superlatives.append(f"Most Accurate: {best_accuracy} ({analysis[best_accuracy]['accuracy']}%)")
    
    # Worst accuracy
    worst_accuracy = min(players, key=lambda p: analysis[p]['accuracy'])
    superlatives.append(f"Least Accurate: {worst_accuracy} ({analysis[worst_accuracy]['accuracy']}%)")
    
    # Biggest comeback
    biggest_comeback = max(players, key=lambda p: analysis[p]['rank_change'])
    if analysis[biggest_comeback]['rank_change'] > 0:
        superlatives.append(f"Biggest Comeback: {biggest_comeback} (climbed {analysis[biggest_comeback]['rank_change']} spots)")
    
    # Biggest choke
    biggest_choke = min(players, key=lambda p: analysis[p]['rank_change'])
    if analysis[biggest_choke]['rank_change'] < 0:
        superlatives.append(f"Biggest Choke: {biggest_choke} (dropped {abs(analysis[biggest_choke]['rank_change'])} spots)")
    
    # Hottest streak
    hottest = max(players, key=lambda p: analysis[p]['max_hot_streak'])
    superlatives.append(f"Hottest Streak: {hottest} ({analysis[hottest]['max_hot_streak']} correct in a row)")
    
    # Coldest streak
    coldest = max(players, key=lambda p: analysis[p]['max_cold_streak'])
    superlatives.append(f"Coldest Streak: {coldest} ({analysis[coldest]['max_cold_streak']} misses in a row)")
    
    # Best 3-round jump
    best_jumper = max(players, key=lambda p: analysis[p]['max_3round_jump'])
    superlatives.append(f"Best 3-Round Run: {best_jumper} (+{analysis[best_jumper]['max_3round_jump']} pts)")
    
    # Worst 3-round drop
    worst_dropper = min(players, key=lambda p: analysis[p]['max_3round_drop'])
    superlatives.append(f"Worst 3-Round Collapse: {worst_dropper} ({analysis[worst_dropper]['max_3round_drop']} pts)")
    
    prompt = f"""You are a sports commentator giving an exciting end-game summary for a Wizard card game tournament.

FINAL STANDINGS AND PLAYER STATS:
{chr(10).join(player_summaries)}

NOTABLE ACHIEVEMENTS:
{chr(10).join(superlatives)}

Write an exciting, dramatic game summary (3-4 paragraphs) that:
1. Celebrates the winner and their journey to victory
2. Highlights the most dramatic moments (comebacks, chokes, close battles)
3. Gives funny "awards" to each player based on their unique stats
4. Ends with a memorable final statement

Be entertaining, use their names, reference specific stats. Make it feel like a sports broadcast recap!"""

    content, error = generate_ai_content(prompt, max_tokens=800, temperature=0.9, timeout=120)
    return content

def verify_nvidia_api(api_key):
    """Verify that the NVIDIA API key is working."""
    try:
        response = requests.post(
            NVIDIA_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "model": st.session_state.selected_nvidia_model,
                "messages": [{"role": "user", "content": "Say 'API working' in exactly 2 words."}],
                "max_tokens": 50,
                "temperature": 0.5,
                "stream": False
            },
            timeout=60  # Reduced timeout for verification
        )
        
        if response.status_code == 200:
            return True, "API key verified successfully!"
        elif response.status_code == 401:
            return False, "Invalid API key. Please check your key."
        elif response.status_code == 403:
            return False, "Access denied. Check your API key permissions."
        elif response.status_code == 404:
            return False, f"Model not found. Check model name: {st.session_state.selected_nvidia_model}"
        else:
            return False, f"API error: {response.status_code} - {response.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, f"Connection error: {str(e)[:100]}"

def verify_gemini_api(api_key):
    """Verify that the Google Gemini API key is working."""
    if not GEMINI_AVAILABLE:
        return False, "Google Gemini library not installed. Run: pip install google-genai"
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=st.session_state.selected_gemini_model,
            contents="Say 'API working' in exactly 2 words."
        )
        if response and response.text:
            return True, "API key verified successfully!"
        else:
            return False, "API returned empty response."
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid API key. Please check your key."
        elif "quota" in error_msg.lower():
            return False, "API quota exceeded. Try another model in the dropdown below."
        else:
            return False, f"Connection error: {error_msg[:100]}"

def generate_ai_content(prompt, max_tokens=500, temperature=0.9, timeout=60):
    """Generate content using the selected AI provider (Gemini or NVIDIA)."""
    provider = st.session_state.api_provider
    
    if provider == "Google Gemini (Free)":
        if not GEMINI_AVAILABLE:
            return None, "Google Gemini library not installed"
        if not st.session_state.gemini_api_key:
            return None, "No Gemini API key configured"
        
        try:
            client = genai.Client(api_key=st.session_state.gemini_api_key)
            response = client.models.generate_content(
                model=st.session_state.selected_gemini_model,
                contents=prompt
            )
            if response and response.text:
                return response.text, None
            else:
                return None, "Empty response from Gemini"
        except Exception as e:
            return None, f"Gemini error: {str(e)[:100]}"
    
    else:  # NVIDIA
        if not st.session_state.nvidia_api_key:
            return None, "No NVIDIA API key configured"
        
        try:
            response = requests.post(
                NVIDIA_API_URL,
                headers={
                    "Authorization": f"Bearer {st.session_state.nvidia_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "model": st.session_state.selected_nvidia_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get("choices", [{}])[0].get("message", {})
                content = message.get("content") or message.get("reasoning_content") or ""
                if content:
                    return content, None
                else:
                    return None, "Empty response from NVIDIA"
            else:
                return None, f"NVIDIA API error: {response.status_code}"
        except requests.exceptions.Timeout:
            return None, "Request timed out"
        except Exception as e:
            return None, f"NVIDIA error: {str(e)[:100]}"

def generate_roasts(round_num):
    """Generate roasts for players based on their full game history using AI."""
    if not st.session_state.enable_roasts or not st.session_state.api_verified:
        return None
    
    # Build comprehensive game history for each player
    player_histories = []
    totals = get_total_scores()
    sorted_by_score = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    
    for player in st.session_state.players:
        # Current standing
        rank = [i+1 for i, (p, s) in enumerate(sorted_by_score) if p == player][0]
        total_score = totals[player]
        
        # Round-by-round history
        round_details = []
        total_correct = 0
        total_over = 0
        total_under = 0
        biggest_fail = 0
        
        for r in range(1, round_num + 1):
            if r in st.session_state.game_data and player in st.session_state.game_data[r]:
                data = st.session_state.game_data[r].get(player, {'bid': None, 'tricks': None})
                bid = data['bid']
                tricks = data['tricks']
                if bid is not None and tricks is not None:
                    diff = tricks - bid
                    score = calculate_score(bid, tricks)
                    round_details.append(f"R{r}: bid {bid}, got {tricks}, {'✓' if diff == 0 else f'off by {abs(diff)}'} ({score:+d} pts)")
                    
                    if diff == 0:
                        total_correct += 1
                    elif diff > 0:
                        total_over += 1
                    else:
                        total_under += 1
                    
                    if abs(diff) > biggest_fail:
                        biggest_fail = abs(diff)
        
        # Build player summary
        history = f"""{player} (Rank #{rank}, {total_score} pts total):
  - Correct bids: {total_correct}/{round_num} rounds
  - Overbid: {total_under}x, Underbid: {total_over}x
  - Biggest miss: {biggest_fail} tricks off
  - Round history: {'; '.join(round_details[-5:])}"""  # Last 5 rounds for context
        
        player_histories.append(history)
    
    # Current round performance
    current_performances = []
    for player in st.session_state.players:
        data = st.session_state.game_data[round_num].get(player, {'bid': None, 'tricks': None})
        bid = data['bid'] or 0
        tricks = data['tricks'] or 0
        diff = tricks - bid
        
        if diff == 0:
            status = f"{player} nailed their bid of {bid} (smug success)"
        elif diff > 0:
            status = f"{player} bid {bid} but got {tricks} (overachiever by {diff})"
        else:
            status = f"{player} bid {bid} but only got {tricks} (failed by {abs(diff)})"
        current_performances.append(status)
    
    # Standings summary
    standings = ", ".join([f"#{i+1} {p} ({s} pts)" for i, (p, s) in enumerate(sorted_by_score)])
    
    prompt = f"""You are a witty, sarcastic commentator for a Wizard card game. Round {round_num} of {st.session_state.max_rounds} just ended.

CURRENT STANDINGS: {standings}

FULL PLAYER HISTORIES:
{chr(10).join(player_histories)}

THIS ROUND'S PERFORMANCES:
{chr(10).join(current_performances)}

Write a brief, savage roast for EACH player individually (1-2 sentences each). Use their FULL GAME HISTORY to make it personal - reference their patterns, streaks, choking moments, or consistent failures. Format as:
PLAYER_NAME: [roast]

Be savage but friendly. Reference specific stats, patterns, or memorable moments from their history. Keep each roast short and punchy."""

    raw_content, error = generate_ai_content(prompt, max_tokens=500, temperature=0.9, timeout=60)
    
    if error or not raw_content:
        return {p: f"[Error]: {error or 'Empty response'}" for p in st.session_state.players}
    
    # Parse individual roasts from response
    roasts = {}
    for player in st.session_state.players:
        # Look for "PLAYER_NAME:" pattern
        pattern = rf"{re.escape(player)}[:\s]+(.+?)(?=\n[A-Z]|$)"
        match = re.search(pattern, raw_content, re.IGNORECASE | re.DOTALL)
        if match:
            roast_text = match.group(1).strip()
            # Clean up the roast text
            roast_text = roast_text.strip('"').strip()
            roasts[player] = roast_text
        else:
            roasts[player] = "Even the AI couldn't find words for this performance..."
    
    return roasts

def save_game(title=None, filename=None):
    """Save the current game state to a text file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        players_str = "_".join(st.session_state.players[:3])
        filename = f"wizard_game_{players_str}_{timestamp}.txt"
    
    if title is None:
        title = f"Game: {', '.join(st.session_state.players)}"
    
    game_data_serializable = {
        str(k): v for k, v in st.session_state.game_data.items()
    }
    
    save_data = {
        "title": title,
        "players": st.session_state.players,
        "player_colors": st.session_state.player_colors,
        "starting_dealer_index": st.session_state.starting_dealer_index,
        "current_round": st.session_state.current_round,
        "game_data": game_data_serializable,
        "max_rounds": st.session_state.max_rounds,
        "game_started": st.session_state.game_started,
        "saved_at": datetime.now().isoformat(),
        "total_scores": get_total_scores()
    }
    
    filepath = SAVE_DIR / filename
    with open(filepath, 'w') as f:
        f.write("=== WIZARD CARD GAME SAVE FILE ===\n")
        f.write(f"Title: {title}\n")
        f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Players: {', '.join(st.session_state.players)}\n")
        f.write(f"Round: {st.session_state.current_round} / {st.session_state.max_rounds}\n")
        f.write(f"Scores: {get_total_scores()}\n")
        f.write("=" * 35 + "\n\n")
        f.write("--- JSON DATA (DO NOT EDIT BELOW) ---\n")
        f.write(json.dumps(save_data, indent=2))
    
    st.session_state.current_save_file = filename
    return filename

def load_game(filename):
    """Load a game state from a text file."""
    filepath = SAVE_DIR / filename
    with open(filepath, 'r') as f:
        content = f.read()
    
    json_marker = "--- JSON DATA (DO NOT EDIT BELOW) ---\n"
    json_start = content.find(json_marker) + len(json_marker)
    json_data = content[json_start:]
    
    save_data = json.loads(json_data)
    
    st.session_state.players = save_data["players"]
    st.session_state.player_colors = save_data.get("player_colors", {})
    st.session_state.starting_dealer_index = save_data.get("starting_dealer_index", 0)
    st.session_state.current_round = save_data["current_round"]
    st.session_state.game_data = {
        int(k): v for k, v in save_data["game_data"].items()
    }
    st.session_state.max_rounds = save_data["max_rounds"]
    st.session_state.game_started = save_data["game_started"]
    st.session_state.current_save_file = filename

def get_saved_games():
    """Get list of saved game files."""
    saved_games = []
    for filepath in SAVE_DIR.glob("wizard_game_*.txt"):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Parse JSON data for title
            json_marker = "--- JSON DATA (DO NOT EDIT BELOW) ---\n"
            json_start = content.find(json_marker) + len(json_marker)
            json_data = content[json_start:]
            save_data = json.loads(json_data)
            title = save_data.get("title", "Untitled Game")
            
            # Parse header lines
            lines = content.split("\n")
            saved_at = lines[2].replace("Saved: ", "").strip() if len(lines) > 2 else "Unknown"
            players = lines[3].replace("Players: ", "").strip() if len(lines) > 3 else "Unknown"
            round_info = lines[4].replace("Round: ", "").strip() if len(lines) > 4 else "Unknown"
            
            saved_games.append({
                "filename": filepath.name,
                "title": title,
                "saved_at": saved_at,
                "players": players,
                "round": round_info
            })
        except Exception:
            pass
    saved_games.sort(key=lambda x: x["saved_at"], reverse=True)
    return saved_games

def update_save_title(filename, new_title):
    """Update the title of a saved game."""
    filepath = SAVE_DIR / filename
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract JSON data
    json_marker = "--- JSON DATA (DO NOT EDIT BELOW) ---\n"
    json_start = content.find(json_marker) + len(json_marker)
    json_data = content[json_start:]
    save_data = json.loads(json_data)
    
    # Update title
    save_data["title"] = new_title
    
    # Rewrite file with new title
    with open(filepath, 'w') as f:
        f.write("=== WIZARD CARD GAME SAVE FILE ===\n")
        f.write(f"Title: {new_title}\n")
        f.write(f"Saved: {save_data['saved_at'].replace('T', ' ')[:19]}\n")
        f.write(f"Players: {', '.join(save_data['players'])}\n")
        f.write(f"Round: {save_data['current_round']} / {save_data['max_rounds']}\n")
        f.write(f"Scores: {save_data['total_scores']}\n")
        f.write("=" * 35 + "\n\n")
        f.write("--- JSON DATA (DO NOT EDIT BELOW) ---\n")
        f.write(json.dumps(save_data, indent=2))

def delete_save(filename):
    """Delete a save file."""
    filepath = SAVE_DIR / filename
    if filepath.exists():
        filepath.unlink()

def _clear_game_state():
    """Clear game-specific state (used by reset and replay)."""
    st.session_state.current_round = 1
    st.session_state.game_data = {}
    st.session_state.current_save_file = None
    st.session_state.game_finished = False
    st.session_state.shot_players = []
    st.session_state.round_roasts = {}
    st.session_state.manual_roast = {}
    st.session_state.game_summary = None
    st.session_state.game_stats = None
    st.session_state.active_tab = 0

def reset_game():
    """Reset the game to initial state."""
    _clear_game_state()
    st.session_state.players = []
    st.session_state.player_colors = {}
    st.session_state.starting_dealer_index = 0
    st.session_state.game_started = False
    st.session_state.max_rounds = 0

def replay_game_with_same_players():
    """Start a new game with the same players."""
    players = st.session_state.players.copy()
    colors = st.session_state.player_colors.copy()
    starting_dealer = st.session_state.starting_dealer_index
    
    _clear_game_state()
    st.session_state.players = players
    st.session_state.player_colors = colors
    st.session_state.starting_dealer_index = starting_dealer
    st.session_state.game_started = True
    st.session_state.max_rounds = 60 // len(players)
    init_round_data(1)
    st.session_state.shot_players = []
    st.session_state.round_roasts = {}
    st.session_state.manual_roast = {}
    st.session_state.game_summary = None
    st.session_state.game_stats = None
    st.session_state.active_tab = 0
    
    # Restore players
    st.session_state.players = players
    st.session_state.player_colors = colors
    st.session_state.starting_dealer_index = starting_dealer
    
    # Initialize game data for round 1
    st.session_state.game_data[1] = {
        player: {'bid': None, 'tricks': None} 
        for player in st.session_state.players
    }

def rename_player(old_name, new_name):
    """Rename a player and update all references."""
    if old_name == new_name or new_name in st.session_state.players:
        return False
    
    # Update players list
    idx = st.session_state.players.index(old_name)
    st.session_state.players[idx] = new_name
    
    # Update player colors
    if old_name in st.session_state.player_colors:
        st.session_state.player_colors[new_name] = st.session_state.player_colors.pop(old_name)
    
    # Update game data
    for round_num in st.session_state.game_data:
        if old_name in st.session_state.game_data[round_num]:
            st.session_state.game_data[round_num][new_name] = st.session_state.game_data[round_num].pop(old_name)
    
    return True

# Sidebar for game setup
with st.sidebar:
    st.title("🎩 The Grand Fardini")
    st.caption("v0.5")
    
    # Theme toggle
    dark_mode = st.toggle("🌙", value=st.session_state.dark_mode, help="Dark Mode")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    
    if not st.session_state.game_started:
        st.subheader("Add Players")
        
        # Use a form so Enter key submits
        with st.form(key="add_player_form", clear_on_submit=True):
            new_player = st.text_input("Player Name")
            submit = st.form_submit_button("Add Player", type="primary")
            if submit and new_player:
                if new_player not in st.session_state.players:
                    st.session_state.players.append(new_player)
                    st.rerun()
                else:
                    st.warning("Player already exists!")
        
        if st.session_state.players:
            st.write("**Current Players:**")
            for i, player in enumerate(st.session_state.players):
                # Assign default color if not set
                if player not in st.session_state.player_colors:
                    st.session_state.player_colors[player] = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
                
                col1, col2, col3, col4, col5 = st.columns([2.5, 0.8, 0.8, 0.8, 0.8])
                
                # Editable player name
                with col1:
                    new_name = st.text_input(f"Name {i+1}", value=player, key=f"edit_name_{i}", label_visibility="collapsed")
                    if new_name and new_name != player:
                        if new_name not in st.session_state.players:
                            rename_player(player, new_name)
                            st.rerun()
                        else:
                            st.toast("Player name already exists!")
                
                # Color picker
                with col2:
                    new_color = st.color_picker("", st.session_state.player_colors[player], key=f"color_{player}", label_visibility="collapsed")
                    if new_color != st.session_state.player_colors[player]:
                        st.session_state.player_colors[player] = new_color
                
                # Move up button
                with col3:
                    if i > 0:
                        if st.button("▲", key=f"up_{player}"):
                            st.session_state.players[i], st.session_state.players[i-1] = \
                                st.session_state.players[i-1], st.session_state.players[i]
                            st.rerun()
                
                # Move down button
                with col4:
                    if i < len(st.session_state.players) - 1:
                        if st.button("▼", key=f"down_{player}"):
                            st.session_state.players[i], st.session_state.players[i+1] = \
                                st.session_state.players[i+1], st.session_state.players[i]
                            st.rerun()
                
                # Remove button
                with col5:
                    if st.button("✕", key=f"remove_{player}"):
                        st.session_state.players.remove(player)
                        if player in st.session_state.player_colors:
                            del st.session_state.player_colors[player]
                        st.rerun()
        
        st.markdown("---")
        
        if len(st.session_state.players) >= 3:
            # Calculate max rounds based on number of players
            num_players = len(st.session_state.players)
            calculated_max_rounds = 60 // num_players
            st.info(f"With {num_players} players, max rounds = {calculated_max_rounds}")
            
            # Select starting dealer
            st.markdown("**Select First Dealer:**")
            dealer_options = st.session_state.players
            selected_dealer = st.selectbox(
                "First dealer", 
                dealer_options, 
                index=st.session_state.starting_dealer_index,
                label_visibility="collapsed"
            )
            st.session_state.starting_dealer_index = dealer_options.index(selected_dealer)
            
            if st.button("🎮 Start Game", type="primary"):
                st.session_state.game_started = True
                st.session_state.current_round = 1  # Reset to round 1
                st.session_state.max_rounds = calculated_max_rounds
                st.session_state.game_data = {}  # Clear any old game data
                st.session_state.game_finished = False  # Reset game finished flag
                st.session_state.shot_players = []  # Clear shot players
                st.session_state.round_roasts = {}  # Clear roasts
                st.session_state.active_tab = 0  # Start on Bids tab
                # Initialize game data for round 1
                st.session_state.game_data[1] = {
                    player: {'bid': None, 'tricks': None} 
                    for player in st.session_state.players
                }
                st.rerun()
        else:
            st.warning("Need at least 3 players to start!")
    
    else:
        st.success(f"Game in progress!")
        st.write(f"**Current Round:** {st.session_state.current_round} / {st.session_state.max_rounds}")
        
        # Player management during game
        st.markdown("---")
        with st.expander("👥 Edit Players & Colors", expanded=False):
            for i, player in enumerate(st.session_state.players):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_name = st.text_input(f"Player {i+1}", value=player, key=f"game_edit_name_{i}", label_visibility="collapsed")
                    if new_name and new_name != player:
                        if new_name not in st.session_state.players:
                            rename_player(player, new_name)
                            st.rerun()
                        else:
                            st.toast("Player name already exists!")
                with col2:
                    new_color = st.color_picker("", st.session_state.player_colors.get(player, "#808080"), key=f"game_color_{i}", label_visibility="collapsed")
                    if new_color != st.session_state.player_colors.get(player):
                        st.session_state.player_colors[player] = new_color
        
        st.markdown("---")
        st.subheader("💾 Save Game")
        
        # Get current title from existing save or use default
        default_title = f"Game: {', '.join(st.session_state.players)}"
        if st.session_state.current_save_file:
            # Try to get existing title from save file
            try:
                saved_games = get_saved_games()
                for game in saved_games:
                    if game['filename'] == st.session_state.current_save_file:
                        default_title = game.get('title', default_title)
                        break
            except:
                pass
        
        save_title = st.text_input("Game Title", value=default_title, key="save_title_input")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", type="primary", use_container_width=True):
                # Use existing filename if available, otherwise create new
                filename = st.session_state.current_save_file if st.session_state.current_save_file else None
                save_game(title=save_title, filename=filename)
                st.success(f"Game saved!")
        
        with col2:
            if st.button("📄 Save as New", type="primary", use_container_width=True):
                # Always create a new file
                save_game(title=save_title, filename=None)
                st.success(f"Saved as new file!")
        
        if st.session_state.current_save_file:
            st.caption(f"Current file: {st.session_state.current_save_file}")
        
        st.markdown("---")
        col_new, col_cancel = st.columns(2)
        with col_new:
            if st.button("🔄 New Game", type="primary", use_container_width=True):
                reset_game()
                st.rerun()
        with col_cancel:
            if st.button("❌ Cancel Game", type="primary", use_container_width=True):
                # Save the current game first
                filename = st.session_state.current_save_file if st.session_state.current_save_file else None
                title = f"Game: {', '.join(st.session_state.players)}"
                save_game(title=title, filename=filename)
                st.toast("Game saved!")
                # Reset to fresh state
                reset_game()
                st.rerun()
        
        # Roast settings
        st.markdown("---")
        st.subheader("🔥 AI Roasts")
        st.session_state.enable_roasts = st.toggle("Enable roasts", value=st.session_state.enable_roasts)
        if st.session_state.enable_roasts:
            # Provider selection
            provider_index = API_PROVIDERS.index(st.session_state.api_provider) if st.session_state.api_provider in API_PROVIDERS else 0
            selected_provider = st.selectbox(
                "AI Provider",
                API_PROVIDERS,
                index=provider_index,
                help="Google Gemini is free! NVIDIA requires a account for free API key."
            )
            if selected_provider != st.session_state.api_provider:
                st.session_state.api_provider = selected_provider
                st.session_state.api_verified = False
                st.rerun()
            
            if st.session_state.api_provider == "Google Gemini (Free)":
                # Gemini settings
                if not GEMINI_AVAILABLE:
                    st.error("⚠️ Google Gemini library not installed. Run: pip install google-genai")
                else:
                    # API key input with touchscreen-friendly save button
                    key_col, btn_col = st.columns([4, 1])
                    with key_col:
                        api_key = st.text_input(
                            "Gemini API Key", 
                            value=st.session_state.gemini_api_key, 
                            type="password",
                            help="Get your free API key from aistudio.google.com",
                            key="gemini_key_input"
                        )
                    with btn_col:
                        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # Spacer to align with input
                        save_clicked = st.button("💾", key="save_gemini_key", help="Save API Key", use_container_width=True)
                    
                    # Save on button click or when key changes
                    if save_clicked or api_key != st.session_state.gemini_api_key:
                        if api_key != st.session_state.gemini_api_key:
                            st.session_state.gemini_api_key = api_key
                            st.session_state.api_verified = False
                            save_api_key(api_key, "gemini")
                            if save_clicked:
                                st.toast("API key saved!")
                    
                    if api_key:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            if st.button("🔌 Verify API Key"):
                                with st.spinner("Verifying..."):
                                    success, message = verify_gemini_api(api_key)
                                    if success:
                                        st.session_state.api_verified = True
                                        st.success(message)
                                    else:
                                        st.session_state.api_verified = False
                                        st.error(message)
                        with col2:
                            if st.session_state.api_verified:
                                st.markdown("✅ Verified")
                            else:
                                st.markdown("❌ Not verified")
                        
                        # Gemini model selector
                        model_names = list(GEMINI_MODELS.keys())
                        current_model_name = [k for k, v in GEMINI_MODELS.items() if v == st.session_state.selected_gemini_model]
                        current_index = model_names.index(current_model_name[0]) if current_model_name else 0
                        
                        selected_name = st.selectbox(
                            "AI Model",
                            model_names,
                            index=current_index,
                            help="Gemini 2.5 Flash is fast and free"
                        )
                        if GEMINI_MODELS[selected_name] != st.session_state.selected_gemini_model:
                            st.session_state.selected_gemini_model = GEMINI_MODELS[selected_name]
                            st.session_state.api_verified = False
                            st.rerun()
                    else:
                        st.caption("⚠️ Enter your Gemini API key")
                        st.caption("Get one free at: aistudio.google.com")
            
            else:  # NVIDIA
                # API key input with touchscreen-friendly save button
                key_col, btn_col = st.columns([4, 1])
                with key_col:
                    api_key = st.text_input(
                        "NVIDIA API Key", 
                        value=st.session_state.nvidia_api_key, 
                        type="password",
                        help="Get your API key from build.nvidia.com",
                        key="nvidia_key_input"
                    )
                with btn_col:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # Spacer to align with input
                    save_clicked = st.button("💾", key="save_nvidia_key", help="Save API Key", use_container_width=True)
                
                # Save on button click or when key changes
                if save_clicked or api_key != st.session_state.nvidia_api_key:
                    if api_key != st.session_state.nvidia_api_key:
                        st.session_state.nvidia_api_key = api_key
                        st.session_state.api_verified = False
                        save_api_key(api_key, "nvidia")
                        if save_clicked:
                            st.toast("API key saved!")
                
                if api_key:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if st.button("🔌 Verify API Key"):
                            with st.spinner("Verifying..."):
                                success, message = verify_nvidia_api(api_key)
                                if success:
                                    st.session_state.api_verified = True
                                    st.success(message)
                                else:
                                    st.session_state.api_verified = False
                                    st.error(message)
                    with col2:
                        if st.session_state.api_verified:
                            st.markdown("✅ Verified")
                        else:
                            st.markdown("❌ Not verified")
                    
                    # NVIDIA model selector
                    model_names = list(NVIDIA_MODELS.keys())
                    current_model_name = [k for k, v in NVIDIA_MODELS.items() if v == st.session_state.selected_nvidia_model]
                    current_index = model_names.index(current_model_name[0]) if current_model_name else 1
                    
                    selected_name = st.selectbox(
                        "AI Model",
                        model_names,
                        index=current_index,
                        help="Llama models are faster, DeepSeek-R1 is more creative but slower"
                    )
                    if NVIDIA_MODELS[selected_name] != st.session_state.selected_nvidia_model:
                        st.session_state.selected_nvidia_model = NVIDIA_MODELS[selected_name]
                        st.session_state.api_verified = False
                        st.rerun()
                else:
                    st.caption("⚠️ Enter your NVIDIA API key")
                    st.caption("Get one at: build.nvidia.com")
    
    # Load game section (always visible in sidebar)
    st.markdown("---")
    st.subheader("📂 Load Game")
    saved_games = get_saved_games()
    if saved_games:
        for game in saved_games[:5]:  # Show last 5 saves
            with st.expander(f"📁 {game.get('title', 'Untitled')[:25]}"):
                st.write(f"**Title:** {game.get('title', 'Untitled')}")
                st.write(f"**Saved:** {game['saved_at']}")
                st.write(f"**Players:** {game['players']}")
                st.write(f"**Round:** {game['round']}")
                
                # Edit title
                new_title = st.text_input("Edit Title", value=game.get('title', ''), key=f"edit_title_{game['filename']}")
                if new_title != game.get('title', ''):
                    if st.button("💾 Save Title", key=f"save_title_{game['filename']}"):
                        update_save_title(game['filename'], new_title)
                        st.rerun()
                
                col1, col2 = st.columns(2)
                if col1.button("Load", key=f"load_{game['filename']}"):
                    load_game(game['filename'])
                    st.rerun()
                if col2.button("🗑️", key=f"del_{game['filename']}"):
                    delete_save(game['filename'])
                    st.rerun()
    else:
        st.caption("No saved games found.")

# Main game area
if not st.session_state.game_started:
    st.info("👈 Add players and start the game using the sidebar!")
    
    # Show game rules
    with st.expander("📜 Wizard Game Rules & Scoring"):
        st.markdown("""
        ### Scoring System
        - **Correct Bid:** 20 points + 10 points per trick won
        - **Incorrect Bid:** -10 points per trick over or under
        
        ### Example Scores
        | Bid | Tricks | Score |
        |-----|--------|-------|
        | 0   | 0      | +20   |
        | 3   | 3      | +50   |
        | 2   | 4      | -20   |
        | 3   | 1      | -20   |
        
        ### Cards per Round
        - Round 1: 1 card each
        - Round 2: 2 cards each
        - ... and so on
        
        ### Number of Rounds
        - 60 cards ÷ number of players = max rounds
        """)

else:
    # Current round input
    st.header(f"📍 Round {st.session_state.current_round}")
    
    # Calculate current dealer (rotates each round)
    num_players = len(st.session_state.players)
    current_dealer_index = (st.session_state.starting_dealer_index + st.session_state.current_round - 1) % num_players
    current_dealer = st.session_state.players[current_dealer_index]
    dealer_color = st.session_state.player_colors.get(current_dealer, "#808080")
    
    st.markdown(f"*Each player has {st.session_state.current_round} card(s)* &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"🃏 **Dealer:** <span style='color:{dealer_color}; font-weight:bold;'>{current_dealer}</span>", 
                unsafe_allow_html=True)
    
    # Prominent Roast Display and Button
    if st.session_state.enable_roasts and st.session_state.api_verified:
        roast_col1, roast_col2 = st.columns([3, 1])
        with roast_col2:
            if st.button("🔥 ROAST! 🔥", type="primary", use_container_width=True):
                with st.spinner("Generating roasts..."):
                    roasts = generate_roasts(st.session_state.current_round)
                    if roasts:
                        st.session_state.manual_roast = roasts
                    else:
                        st.session_state.manual_roast = {p: "The AI is speechless..." for p in st.session_state.players}
                st.rerun()
        
        # Always show the roast box if there are roasts to display
        if st.session_state.manual_roast:
            st.markdown(
                """
                <div style='background: linear-gradient(135deg, #8B0000 0%, #FF4500 50%, #FFD700 100%); 
                            padding: 20px; border-radius: 20px; 
                            border: 4px solid #FFD700; 
                            margin: 15px 0; 
                            box-shadow: 0 0 30px #FF4500, 0 0 60px #8B000040;'>
                    <h2 style='color: #FFFFFF; text-align: center; margin: 0 0 15px 0; text-shadow: 2px 2px 4px #000;'>
                        🔥🎤 THE ROASTS 🎤🔥
                    </h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display individual roasts in columns
            roast_cols = st.columns(len(st.session_state.players))
            theme = get_theme_colors()
            for i, player in enumerate(st.session_state.players):
                player_color = st.session_state.player_colors.get(player, "#FF6B6B")
                roast_text = st.session_state.manual_roast.get(player, "No roast available")
                with roast_cols[i]:
                    st.markdown(
                        f"""
                        <div style='background: {theme['card_bg']}; 
                                    padding: 15px; border-radius: 15px; 
                                    border: 3px solid {player_color}; 
                                    margin: 5px 0; 
                                    box-shadow: 0 0 15px {player_color}40;
                                    min-height: 150px;'>
                            <h3 style='color: {player_color}; text-align: center; margin: 0 0 10px 0;'>
                                🔥 {player} 🔥
                            </h3>
                            <p style='color: {theme['text_primary']}; text-align: center; font-size: 1.1em; font-style: italic; 
                                      margin: 0; line-height: 1.4;'>
                                "{roast_text}"
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Button to clear the roast
            if st.button("❌ Clear Roasts", type="secondary"):
                st.session_state.manual_roast = {}
                st.rerun()
    
    # Always show current standings at top
    st.markdown("---")
    totals = get_total_scores()
    sorted_players = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    
    cols = st.columns(len(sorted_players))
    medals = ["🥇", "🥈", "🥉"] + [""] * 10
    
    for i, (player, score) in enumerate(sorted_players):
        player_color = st.session_state.player_colors.get(player, "#808080")
        with cols[i]:
            st.markdown(f"<div style='text-align:center; padding:5px; border-radius:5px; border: 2px solid {player_color};'>"
                       f"<b>{medals[i]} {player}</b><br><span style='font-size:1.2em;'>{score} pts</span></div>", 
                       unsafe_allow_html=True)
    st.markdown("---")
    
    # Tab selection using radio buttons
    tab_options = ["🎯 Bids", "🃏 Tricks Won", "📊 Scoreboard"]
    
    # Check for pending tab change (set before rerun)
    if "pending_tab" in st.session_state:
        st.session_state.active_tab = st.session_state.pending_tab
        del st.session_state.pending_tab
    
    # Use a unique key that includes the active_tab to force widget recreation when tab changes
    selected = st.radio(
        "Navigate", 
        tab_options, 
        index=st.session_state.active_tab, 
        horizontal=True, 
        label_visibility="collapsed",
        key=f"tab_nav_{st.session_state.active_tab}"
    )
    
    # Update active_tab based on selection
    new_tab = tab_options.index(selected)
    if new_tab != st.session_state.active_tab:
        st.session_state.active_tab = new_tab
        st.rerun()
    
    if st.session_state.active_tab == 0:  # Bids tab
        st.subheader("Enter Bids")
        current_round = st.session_state.current_round
        
        # Ensure current round exists in game data
        if current_round not in st.session_state.game_data:
            st.session_state.game_data[current_round] = {
                player: {'bid': None, 'tricks': None} 
                for player in st.session_state.players
            }
        
        cols = st.columns(len(st.session_state.players))
        for i, player in enumerate(st.session_state.players):
            with cols[i]:
                player_color = st.session_state.player_colors.get(player, "#808080")
                st.markdown(f"<b>{player}</b>", unsafe_allow_html=True)
                current_bid = st.session_state.game_data[current_round][player]['bid']
                bid = st.number_input(
                    f"Bid for {player}",
                    min_value=0,
                    max_value=current_round,
                    value=current_bid if current_bid is not None else 0,
                    step=1,
                    key=f"bid_{player}_{current_round}",
                    label_visibility="collapsed"
                )
                st.session_state.game_data[current_round][player]['bid'] = bid
        
        # Show total bids
        total_bids = sum(
            st.session_state.game_data[current_round][p]['bid'] or 0 
            for p in st.session_state.players
        )
        
        # Calculate what the dealer can't say
        cant_say = current_round - total_bids
        num_players = len(st.session_state.players)
        current_dealer_index = (st.session_state.starting_dealer_index + current_round - 1) % num_players
        current_dealer = st.session_state.players[current_dealer_index]
        dealer_color = st.session_state.player_colors.get(current_dealer, "#808080")
        
        # Check if all bids are entered (not None)
        all_bids_entered = all(
            st.session_state.game_data[current_round][p]['bid'] is not None 
            for p in st.session_state.players
        )
        
        if total_bids == current_round:
            st.warning(f"⚠️ Total bids ({total_bids}) = tricks available ({current_round}). Someone must be wrong!")
        else:
            st.info(f"Total bids: {total_bids} / {current_round} tricks available")
        
        # Show dealer restriction
        if 0 <= cant_say <= current_round:
            st.markdown(f"🚫 <b><span style='color:{dealer_color};'>{current_dealer}</span> (dealer) can't say {cant_say}</b>", 
                       unsafe_allow_html=True)
        else:
            # cant_say is below zero or above current_round, dealer can say anything
            st.markdown(f"✅ <b><span style='color:{dealer_color};'>{current_dealer}</span> (dealer) can say anything</b>", 
                       unsafe_allow_html=True)
        
        # Navigation buttons
        st.markdown("---")
        nav_col1, nav_col2 = st.columns([1, 1])
        with nav_col1:
            if st.session_state.current_round > 1:
                if st.button("⬅️ Previous Round", key="prev_round_bids"):
                    st.session_state.current_round -= 1
                    st.rerun()
        with nav_col2:
            # Check if any bids have been entered (at least one bid > 0, or it's round 1 where all 0s could be valid)
            any_nonzero_bid = any(
                (st.session_state.game_data[current_round][p]['bid'] or 0) > 0
                for p in st.session_state.players
            )
            # For round 1, allow all zeros as valid bids; for other rounds require at least one non-zero
            bids_entered = any_nonzero_bid or current_round == 1
            # Only allow going to tricks if total bids != current round (valid bid state) AND bids entered
            bids_valid = total_bids != current_round and bids_entered
            if bids_valid:
                if st.button("Go to Tricks 🃏 ➡️", type="primary", key="go_to_tricks"):
                    st.session_state.pending_tab = 1
                    st.rerun()
            else:
                st.button("Go to Tricks 🃏 ➡️", type="primary", disabled=True, key="go_to_tricks_disabled")
                if not bids_entered:
                    st.caption("⚠️ Enter bids first")
                else:
                    st.caption("⚠️ Total bids cannot equal tricks available")
    
    elif st.session_state.active_tab == 1:  # Tricks tab
        st.subheader("Enter Tricks Won")
        current_round = st.session_state.current_round
        
        cols = st.columns(len(st.session_state.players))
        for i, player in enumerate(st.session_state.players):
            with cols[i]:
                # Show player's bid next to their name
                player_bid = st.session_state.game_data[current_round][player]['bid'] or 0
                player_color = st.session_state.player_colors.get(player, "#808080")
                st.markdown(f"<b>{player}</b> <span style='color:{player_color}; font-size:0.9em;'>(Bid: {player_bid})</span>", 
                           unsafe_allow_html=True)
                
                current_tricks = st.session_state.game_data[current_round][player]['tricks']
                tricks = st.number_input(
                    f"Tricks for {player}",
                    min_value=0,
                    max_value=current_round,
                    label_visibility="collapsed",
                    value=current_tricks if current_tricks is not None else 0,
                    step=1,
                    key=f"tricks_{player}_{current_round}"
                )
                st.session_state.game_data[current_round][player]['tricks'] = tricks
        
        # Show total tricks
        total_tricks = sum(
            st.session_state.game_data[current_round][p]['tricks'] or 0 
            for p in st.session_state.players
        )
        if total_tricks != current_round:
            st.error(f"❌ Total tricks ({total_tricks}) ≠ tricks available ({current_round})")
        else:
            st.success(f"✅ Total tricks: {total_tricks} / {current_round}")
        
        st.markdown("---")
        
        # Round navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_round > 1:
                if st.button("⬅️ Previous Round", key="prev_round_tricks"):
                    st.session_state.current_round -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.current_round < st.session_state.max_rounds:
                # Only allow next round if all tricks are accounted for
                tricks_valid = total_tricks == current_round
                if tricks_valid:
                    if st.button("Next Round ➡️", type="primary", key="next_round_btn"):
                        current_round_num = st.session_state.current_round
                        st.session_state.shot_players = get_shot_players(current_round_num)
                        
                        # Generate roast for this round before moving on
                        if st.session_state.enable_roasts and st.session_state.api_verified:
                            with st.spinner("🔥 Generating roasts... (this may take up to 90 seconds)"):
                                roast = generate_roasts(current_round_num)
                                st.session_state.round_roasts[current_round_num] = roast if roast else "[No roast generated - API may have failed]"
                        elif st.session_state.enable_roasts and not st.session_state.api_verified:
                            st.session_state.round_roasts[current_round_num] = "[API not verified - please verify your API key]"
                        
                        st.session_state.current_round += 1
                        st.session_state.pending_tab = 0
                        init_round_data(st.session_state.current_round)
                        
                        # Auto-save game after each round
                        save_game(filename=st.session_state.current_save_file) if st.session_state.current_save_file else save_game()
                        st.rerun()
                else:
                    st.button("Next Round ➡️", type="primary", disabled=True, key="next_round_btn_disabled")
                    st.caption(f"⚠️ Tricks must equal {current_round}")
            else:
                # Final round - add Finish Game button
                all_tricks_entered = all(
                    st.session_state.game_data[st.session_state.current_round][p]['tricks'] is not None
                    for p in st.session_state.players
                )
                all_bids_entered = all(
                    st.session_state.game_data[st.session_state.current_round][p]['bid'] is not None
                    for p in st.session_state.players
                )
                
                if all_tricks_entered and all_bids_entered and not st.session_state.get('game_finished', False):
                    if st.button("🏆 Finish Game", type="primary"):
                        current_round = st.session_state.current_round
                        st.session_state.shot_players = get_shot_players(current_round)
                        
                        # Generate roast for final round
                        if st.session_state.enable_roasts and st.session_state.api_verified:
                            with st.spinner("🔥 Generating final roasts... (this may take up to 90 seconds)"):
                                roast = generate_roasts(current_round)
                                st.session_state.round_roasts[current_round] = roast if roast else "[No roast generated - API may have failed]"
                        elif st.session_state.enable_roasts and not st.session_state.api_verified:
                            st.session_state.round_roasts[current_round] = "[API not verified - please verify your API key]"
                        
                        st.session_state.game_finished = True
                        st.session_state.show_celebration = True
                        st.session_state.pending_tab = 2
                        st.rerun()
                elif st.session_state.get('game_finished', False):
                    st.success("🏆 Game Complete! View results in Scoreboard tab.")
                else:
                    st.info("Final Round! Enter all bids and tricks, then click Finish Game.")
    
    # Show shot popup if there are players who need to take a shot
    if st.session_state.shot_players:
        theme = get_theme_colors()
        
        # Show roast first if available
        prev_round = st.session_state.current_round - 1
        if prev_round in st.session_state.round_roasts:
            roast_text = st.session_state.round_roasts[prev_round]
            st.markdown(
                f"""<div style='background: {theme['roast_bg']}; 
                             padding: 20px; border-radius: 15px; border: 2px solid #f39c12; 
                             margin: 10px 0; box-shadow: 0 0 15px #f39c12;'>
                    <h3 style='color: #f39c12; text-align: center; margin-bottom: 10px;'>🔥 Round {prev_round} Roast 🔥</h3>
                    <p style='color: {theme['text_primary']}; text-align: center; font-size: 1.1em; font-style: italic;'>"{roast_text}"</p>
                    </div>""",
                unsafe_allow_html=True
            )
        
        shot_html = "".join(
            f"<h2 style='color:{st.session_state.player_colors.get(p, '#FF0000')}; text-align:center;'>🍺 {p.upper()} NEEDS TO TAKE A SHOT! 🍺</h2>"
            for p in st.session_state.shot_players
        )
        
        st.markdown(
            f"""<div style='background: {theme['banner_bg']}; 
                         padding: 30px; border-radius: 15px; border: 3px solid #e94560; 
                         margin: 20px 0; box-shadow: 0 0 20px #e94560;'>
                {shot_html}
                </div>""",
            unsafe_allow_html=True
        )
        
        if st.button("✅ Acknowledged - Shots Taken!", type="primary"):
            st.session_state.shot_players = []
            if prev_round in st.session_state.round_roasts:
                del st.session_state.round_roasts[prev_round]
            st.rerun()
    
    # Show roast popup even if no shot players (when there's a pending roast)
    elif not st.session_state.shot_players:
        prev_round = st.session_state.current_round - 1
        if prev_round in st.session_state.round_roasts:
            theme = get_theme_colors()
            roast_text = st.session_state.round_roasts[prev_round]
            st.markdown(
                f"""<div style='background: {theme['roast_bg']};  
                             padding: 20px; border-radius: 15px; border: 2px solid #f39c12; 
                             margin: 10px 0; box-shadow: 0 0 15px #f39c12;'>
                    <h3 style='color: #f39c12; text-align: center; margin-bottom: 10px;'>🔥 Round {prev_round} Roast 🔥</h3>
                    <p style='color: {theme['text_primary']}; text-align: center; font-size: 1.1em; font-style: italic;'>"{roast_text}"</p>
                    </div>""",
                unsafe_allow_html=True
            )
            if st.button("😂 Nice one! Continue", type="primary"):
                del st.session_state.round_roasts[prev_round]
                st.rerun()

    if st.session_state.active_tab == 2:  # Scoreboard tab
        st.subheader("📊 Full Scoreboard")
        
        # Build scoreboard dataframe
        scoreboard_data = []
        running_totals = {player: 0 for player in st.session_state.players}
        
        # Only show completed rounds (not current round unless game is finished)
        game_finished = st.session_state.get('game_finished', False)
        max_round_to_show = st.session_state.current_round if game_finished else st.session_state.current_round - 1
        
        for round_num in range(1, max_round_to_show + 1):
            if round_num in st.session_state.game_data:
                row = {'Round': round_num}
                for player in st.session_state.players:
                    data = st.session_state.game_data[round_num].get(player, {'bid': None, 'tricks': None})
                    bid = data['bid']
                    tricks = data['tricks']
                    
                    if bid is not None and tricks is not None:
                        score = calculate_score(bid, tricks)
                        running_totals[player] += score
                        hit = "✓" if bid == tricks else "✗"
                        row[f"{player} Bid"] = bid
                        row[f"{player} Tricks"] = tricks
                        row[f"{player} Score"] = f"{score:+d} {hit}"
                        row[f"{player} Total"] = running_totals[player]
                    else:
                        row[f"{player} Bid"] = "-"
                        row[f"{player} Tricks"] = "-"
                        row[f"{player} Score"] = "-"
                        row[f"{player} Total"] = running_totals[player]
                
                scoreboard_data.append(row)
        
        if scoreboard_data:
            df = pd.DataFrame(scoreboard_data)
            # Use st.table for better theme compatibility (renders as HTML table)
            st.table(df)
        else:
            st.info("Complete at least one round to see the scoreboard.")
        
        # Score progression chart
        st.markdown("---")
        st.subheader("📈 Score Progression")
        
        # Build chart data - cumulative scores per round
        chart_data = {"Round": [0]}  # Start at round 0 with 0 points
        for player in st.session_state.players:
            chart_data[player] = [0]
        
        running_totals_chart = {player: 0 for player in st.session_state.players}
        for round_num in range(1, max_round_to_show + 1):
            if round_num in st.session_state.game_data:
                # Check if this round is complete (all players have bid and tricks)
                round_complete = all(
                    st.session_state.game_data[round_num].get(player, {}).get('bid') is not None and
                    st.session_state.game_data[round_num].get(player, {}).get('tricks') is not None
                    for player in st.session_state.players
                )
                
                if not round_complete:
                    continue  # Skip incomplete rounds
                
                chart_data["Round"].append(round_num)
                for player in st.session_state.players:
                    data = st.session_state.game_data[round_num].get(player, {'bid': None, 'tricks': None})
                    bid = data['bid']
                    tricks = data['tricks']
                    if bid is not None and tricks is not None:
                        running_totals_chart[player] += calculate_score(bid, tricks)
                    chart_data[player].append(running_totals_chart[player])
        
        if len(chart_data["Round"]) > 1:
            chart_df = pd.DataFrame(chart_data)
            chart_melted = chart_df.melt(id_vars=["Round"], var_name="Player", value_name="Score")
            
            color_scale = alt.Scale(
                domain=st.session_state.players,
                range=[st.session_state.player_colors.get(p, DEFAULT_COLORS[i % len(DEFAULT_COLORS)]) 
                       for i, p in enumerate(st.session_state.players)]
            )
            
            theme = get_theme_colors()
            chart = alt.Chart(chart_melted).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X("Round:Q", title="Round", axis=alt.Axis(tickMinStep=1, labelColor=theme['text_primary'], titleColor=theme['text_primary'], gridColor=theme['chart_grid'])),
                y=alt.Y("Score:Q", title="Total Score", axis=alt.Axis(labelColor=theme['text_primary'], titleColor=theme['text_primary'], gridColor=theme['chart_grid'])),
                color=alt.Color("Player:N", scale=color_scale, legend=alt.Legend(title="Players", labelColor=theme['text_primary'], titleColor=theme['text_primary'])),
                tooltip=["Round", "Player", "Score"]
            ).properties(height=400, background=theme['bg_primary']).configure_view(strokeWidth=0).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Complete at least one round to see the score progression chart.")
        
        # Final results - only show when game is properly finished
        if st.session_state.get('game_finished', False):
            if st.session_state.get('show_celebration', False):
                st.balloons()
                st.snow()
            
            if st.session_state.game_stats is None:
                st.session_state.game_stats = analyze_game_stats()
                st.session_state.show_celebration = False
            
            stats = st.session_state.game_stats
            analysis = stats['analysis']
            theme = get_theme_colors()
            
            winner = sorted_players[0][0]
            winner_color = st.session_state.player_colors.get(winner, "#FFD700")
            medals = ["🥇", "🥈", "🥉"] + [""] * 10
            
            results_html = "".join(
                f"<h1 style='color:{st.session_state.player_colors.get(p, '#FFFFFF')}; text-align:center; margin:10px 0;'>{medals[i]} {p} - {s} pts{' 👑' if i == 0 else ''}</h1>" if i == 0
                else f"<h3 style='color:{st.session_state.player_colors.get(p, '#FFFFFF')}; text-align:center; margin:5px 0;'>{medals[i]} {p} - {s} pts</h3>"
                for i, (p, s) in enumerate(sorted_players)
            )
            
            # Celebration popup
            st.markdown(
                f"""
                <div style='background: {theme['popup_bg']}; 
                            padding: 40px; border-radius: 20px; 
                            border: 4px solid {winner_color}; 
                            margin: 30px 0; 
                            box-shadow: 0 0 30px {winner_color}, 0 0 60px {winner_color}40;
                            text-align: center;'>
                    <h1 style='color: #FFD700; font-size: 3em; margin-bottom: 20px;'>
                        🎉🏆 GAME OVER! 🏆🎉
                    </h1>
                    <h2 style='color: {theme['text_primary']}; margin-bottom: 30px;'>
                        🧙 The Wizard Tournament Has Concluded! 🧙
                    </h2>
                    <div style='background: rgba(128,128,128,0.1); padding: 20px; border-radius: 15px; margin: 20px 0;'>
                        {results_html}
                    </div>
                    <p style='color: {theme['stat_text']}; font-size: 1.2em; margin-top: 20px;'>
                        🎊 Congratulations to all players! 🎊
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Game Statistics Section
            st.markdown("---")
            st.subheader("📊 Game Statistics & Awards")
            
            # Player stat cards
            stat_cols = st.columns(len(st.session_state.players))
            for i, (player, score) in enumerate(sorted_players):
                player_color = st.session_state.player_colors.get(player, "#808080")
                a = analysis[player]
                with stat_cols[i]:
                    st.markdown(
                        f"""
                        <div style='background: {theme['card_bg']}; 
                                    padding: 15px; border-radius: 15px; 
                                    border: 3px solid {player_color}; 
                                    margin: 5px 0;'>
                            <h3 style='color: {player_color}; text-align: center; margin: 0 0 10px 0;'>
                                {medals[i]} {player}
                            </h3>
                            <p style='color: {theme['text_primary']}; text-align: center; font-size: 1.5em; margin: 5px 0;'>
                                {score} pts
                            </p>
                            <hr style='border-color: {player_color}40;'>
                            <p style='color: {theme['stat_text']}; font-size: 0.9em; margin: 5px 0;'>
                                🎯 Accuracy: <b>{a['accuracy']}%</b> ({a['correct_bids']}/{a['total_rounds']})
                            </p>
                            <p style='color: {theme['stat_text']}; font-size: 0.9em; margin: 5px 0;'>
                                🔥 Best Round: R{a['best_round']} (+{a['best_round_score']})
                            </p>
                            <p style='color: {theme['stat_text']}; font-size: 0.9em; margin: 5px 0;'>
                                💀 Worst Round: R{a['worst_round']} ({a['worst_round_score']})
                            </p>
                            <p style='color: {theme['stat_text']}; font-size: 0.9em; margin: 5px 0;'>
                                📈 Best 3-Round: +{a['max_3round_jump']}
                            </p>
                            <p style='color: {theme['stat_text']}; font-size: 0.9em; margin: 5px 0;'>
                                📉 Worst 3-Round: {a['max_3round_drop']}
                            </p>
                            <p style='color: {theme['stat_text']}; font-size: 0.9em; margin: 5px 0;'>
                                🏆 Led {a['times_in_lead']} rounds
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Superlative Awards
            st.markdown("---")
            st.subheader("🏅 Game Awards")
            
            award_cols = st.columns(4)
            
            # Calculate awards
            best_accuracy = max(st.session_state.players, key=lambda p: analysis[p]['accuracy'])
            worst_accuracy = min(st.session_state.players, key=lambda p: analysis[p]['accuracy'])
            biggest_comeback = max(st.session_state.players, key=lambda p: analysis[p]['rank_change'])
            biggest_choke = min(st.session_state.players, key=lambda p: analysis[p]['rank_change'])
            hottest_streak = max(st.session_state.players, key=lambda p: analysis[p]['max_hot_streak'])
            coldest_streak = max(st.session_state.players, key=lambda p: analysis[p]['max_cold_streak'])
            best_jumper = max(st.session_state.players, key=lambda p: analysis[p]['max_3round_jump'])
            worst_dropper = min(st.session_state.players, key=lambda p: analysis[p]['max_3round_drop'])
            
            awards = [
                ("🎯 Sharpshooter", best_accuracy, f"{analysis[best_accuracy]['accuracy']}% accuracy"),
                ("🙈 Blind Bidder", worst_accuracy, f"{analysis[worst_accuracy]['accuracy']}% accuracy"),
                ("🚀 Rocket", best_jumper, f"+{analysis[best_jumper]['max_3round_jump']} pts in 3 rounds"),
                ("📉 Freefall", worst_dropper, f"{analysis[worst_dropper]['max_3round_drop']} pts in 3 rounds"),
                ("🔥 On Fire", hottest_streak, f"{analysis[hottest_streak]['max_hot_streak']} correct in a row"),
                ("❄️ Ice Cold", coldest_streak, f"{analysis[coldest_streak]['max_cold_streak']} misses in a row"),
                ("🦸 Comeback King", biggest_comeback, f"Climbed {analysis[biggest_comeback]['rank_change']} spots") if analysis[biggest_comeback]['rank_change'] > 0 else None,
                ("😱 Choke Artist", biggest_choke, f"Dropped {abs(analysis[biggest_choke]['rank_change'])} spots") if analysis[biggest_choke]['rank_change'] < 0 else None,
            ]
            
            # Filter out None awards and display
            awards = [a for a in awards if a is not None]
            for i, (title, player, stat) in enumerate(awards):
                player_color = st.session_state.player_colors.get(player, "#FFD700")
                with award_cols[i % 4]:
                    st.markdown(
                        f"""
                        <div style='background: {theme['roast_bg']}; 
                                    padding: 15px; border-radius: 10px; 
                                    border: 2px solid {player_color}; 
                                    margin: 5px 0; text-align: center;'>
                            <h4 style='color: #FFD700; margin: 0;'>{title}</h4>
                            <p style='color: {player_color}; font-size: 1.2em; margin: 5px 0; font-weight: bold;'>{player}</p>
                            <p style='color: {theme['text_primary']}; font-size: 0.9em; margin: 0;'>{stat}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # LLM Game Summary
            if st.session_state.enable_roasts and st.session_state.api_verified:
                st.markdown("---")
                st.subheader("🎙️ The Commentator's Recap")
                
                if st.session_state.game_summary is None:
                    if st.button("🎤 Generate Game Summary", type="primary", use_container_width=True):
                        with st.spinner("The commentator is reviewing the footage..."):
                            summary = generate_game_summary(stats)
                            if summary:
                                st.session_state.game_summary = summary
                            else:
                                st.session_state.game_summary = "The commentator lost their notes... but what a game that was!"
                        st.rerun()
                else:
                    st.info("🎙️ **The Commentator Says:**")
                    st.write(st.session_state.game_summary)
                    if st.button("🔄 Regenerate Summary"):
                        st.session_state.game_summary = None
                        st.rerun()
            
            # Play Again button
            st.markdown("---")
            st.subheader("🔁 Play Again?")
            play_again_col1, play_again_col2 = st.columns(2)
            with play_again_col1:
                if st.button("🔄 New Game (Same Players)", type="primary", use_container_width=True):
                    replay_game_with_same_players()
                    st.rerun()
            with play_again_col2:
                if st.button("🆕 New Game (New Players)", use_container_width=True):
                    reset_game()
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ for Wizard card game enthusiasts*")
