import streamlit as st
import pandas as pd
from utils import get_employees, add_employee, remove_employee, get_error_types, add_error_type, remove_error_type, SALES_ERROR_TYPES, PROD_ERROR_TYPES

st.set_page_config(page_title="Configurações", layout="wide")
st.title("⚙️ Configurações do Sistema")

# --- FUNCIONÁRIOS ---
st.header("👥 Gerenciar Funcionários")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Adicionar")
    with st.form("add_emp"):
        nome = st.text_input("Nome")
        setor = st.selectbox("Setor de Atuação", ["Ambos", "Produção", "Vendas"])
        is_farma = st.checkbox("É Farmacêutico?")
        if st.form_submit_button("Adicionar"):
            if nome:
                ok, msg = add_employee(nome, is_farma, setor)
                if ok: 
                    st.success(msg)
                    st.rerun()
                else: 
                    st.error(msg)

with col2:
    st.subheader("Remover")
    
    # 1. We put the filter OUTSIDE the form so it reacts instantly when changed
    filtro_setor = st.selectbox("Filtrar lista por setor:", ["Todos", "Produção", "Vendas", "Ambos"])
    
    # 2. Get the data and apply the filter
    emp_data = get_employees()
    if filtro_setor == "Todos":
        emp_list_filtered = list(emp_data.keys())
    else:
        emp_list_filtered = [
            name for name, v in emp_data.items() 
            if v.get("setor", "Ambos") == filtro_setor
        ]
        
    # 3. Build the form with the filtered list
    with st.form("rem_emp"):
        nome_rem = st.selectbox("Selecione o Funcionário", options=[""] + emp_list_filtered)
        if st.form_submit_button("Remover"):
            if nome_rem:
                ok, msg = remove_employee(nome_rem)
                if ok: 
                    st.success(msg)
                    st.rerun()

# Display current employees with their sectors
st.write("Lista Atual:")
if emp_data: # Uses the un-filtered dictionary so you see everyone in the table
    df_emps = pd.DataFrame([
        {"Nome": k, "Cargo": v.get('role', 'Geral'), "Setor": v.get('setor', 'Ambos')} 
        for k, v in emp_data.items()
    ])
    st.dataframe(df_emps, hide_index=True, use_container_width=True)
else:
    st.info("Nenhum funcionário cadastrado.")

st.divider()

# --- TIPOS DE ERRO ---
st.header("⚠️ Gerenciar Tipos de Erros")
tab1, tab2 = st.tabs(["Erros de Vendas", "Erros de Produção"])

def gerenciar_erros(file_path):
    c1, c2 = st.columns(2)
    with c1:
        with st.form(f"add_err_{file_path}"):
            novo_erro = st.text_input("Novo Tipo de Erro")
            if st.form_submit_button("Adicionar"):
                ok, msg = add_error_type(file_path, novo_erro)
                if ok: 
                    st.success(msg)
                    st.rerun()
    with c2:
        with st.form(f"rem_err_{file_path}"):
            lista_erros = get_error_types(file_path)
            erro_rem = st.selectbox("Remover", options=[""] + lista_erros)
            if st.form_submit_button("Remover"):
                ok, msg = remove_error_type(file_path, erro_rem)
                if ok: 
                    st.success(msg)
                    st.rerun()
    st.write("Tipos Atuais:", get_error_types(file_path))

with tab1:
    gerenciar_erros(SALES_ERROR_TYPES)

with tab2:
    gerenciar_erros(PROD_ERROR_TYPES)