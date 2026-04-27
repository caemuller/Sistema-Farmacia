import streamlit as st
import os

st.set_page_config(page_title="Gestão de Farmácia", page_icon="🏥", layout="centered")

if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("🏥 Sistema Central de Gestão")
st.markdown("""
Bem-vindo ao sistema de gestão unificado. 
Utilize o menu lateral esquerdo para navegar entre os setores:
* **🛒 Vendas:** Registrar e visualizar dashboards de erros de vendas.
* **🏭 Produção:** Registrar fórmulas, analisar produção e reportar erros produtivos.
* **⚙️ Configurações:** Gerenciar funcionários e tipos de erros do sistema.
""")

st.info("👈 Abra a barra lateral para começar.")