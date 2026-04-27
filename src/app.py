import streamlit as st
import os
import pandas as pd
import datetime
from utils import load_json, SALES_DATA_FILE, PROD_DATA_FILE, get_employees

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Centro de Controle | Farmácia Matéria Prima", page_icon="🏥", layout="wide")

# --- CUSTOM CSS FOR BEAUTIFICATION ---
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.2rem;
        color: #6B7280;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    /* Adds a subtle shadow and rounding to metrics */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER & LOGO ---
# We use columns to perfectly center the logo and make it nice and large
col_space1, col_logo, col_space3 = st.columns([1, 2, 1])

with col_logo:
    if os.path.exists("logo.png"):
        # use_container_width makes it automatically scale to look big and crisp
        st.image("logo.png", use_container_width=True)
    
    st.markdown('<p class="main-title">Sistema Central</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Centro de Controle e Gestão Operacional</p>', unsafe_allow_html=True)

st.divider()

# --- LIVE METRICS (The "Applications Running" Vibe) ---
st.markdown("### 📡 Status em Tempo Real (Hoje)")

# Safely load data to calculate today's metrics
today_str = datetime.date.today().isoformat()

sales_data = load_json(SALES_DATA_FILE, [])
prod_data = load_json(PROD_DATA_FILE, [])
emp_data = get_employees()

# Calculate totals
sales_today = sum(1 for r in sales_data if r.get('date') == today_str)
prod_today = sum(1 for r in prod_data if r.get('date') == today_str)
total_emps = len(emp_data)

# Display Metrics in a 4-column layout
m1, m2, m3, m4 = st.columns(4)
m1.metric("Erros de Vendas (Hoje)", sales_today)
m2.metric("Fórmulas Produzidas (Hoje)", prod_today)
m3.metric("Equipe Ativa (Cadastros)", total_emps)
m4.metric("Status do Servidor", "🟢 Online")

st.divider()

# --- NAVIGATION CARDS ---
st.markdown("### 🚀 Acesso Rápido aos Setores")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.info("#### 🛒 Vendas\nGerencie erros de vendas, visualize dashboards financeiros de prejuízo e consulte históricos completos de NRs e soluções aplicadas.")
    # st.page_link creates a clickable button that navigates directly to the page!
    st.page_link("pages/Vendas.py", label="Acessar Setor de Vendas", icon="↗️")

with c2:
    st.success("#### 🏭 Produção\nRegistre a produção diária de fórmulas, analise o desempenho e produção e registre erros no processo.")
    st.page_link("pages/Producao.py", label="Acessar Setor de Produção", icon="↗️")

with c3:
    st.warning("#### ⚙️ Configurações\nGerencie a equipe da farmácia, Adicione e edite funcionários novos e tipos de erros disponíveis para os setores.")
    st.page_link("pages/Configurar.py", label="Acessar Configurações", icon="↗️")
with c4:
    st.error("#### 🎯 Metas\nAcompanhe os descontos de premiação baseados nos erros cometidos.")
    st.page_link("pages/Metas.py", label="Acessar Metas", icon="↗️")

# --- FOOTER ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.caption("Sistema de Gestão v1.0 • Desenvolvido por Caetano Müller • O compartilhamento do codigo fonte não é permitido sem autorização prévia.")