import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from utils import get_employees, get_error_types, save_record, search_by_nr, load_json, PROD_DATA_FILE, PROD_ERROR_DATA, PROD_ERROR_TYPES

st.set_page_config(page_title="Produção", layout="wide")
st.title("🏭 Setor de Produção")

# Added the 4th Tab for Searching NR
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard de Fórmulas", "💊 Registrar Fórmula", "⚠️ Registrar Erro", "🔍 Consultar NR"])

# Filter employees for Production
all_employees = get_employees()
prod_employees = [
    name for name, data in all_employees.items() 
    if data.get("setor", "Ambos") in ["Produção", "Ambos"]
]

# Filter pharmacists explicitly inside the production list
farmaceuticos_prod = [
    name for name in prod_employees 
    if all_employees[name].get("role") == "Farmaceutico"
]

# --- TAB 1: DASHBOARD ---
with tab1:
    df = pd.DataFrame(load_json(PROD_DATA_FILE, []))
    if df.empty:
        st.warning("Nenhum dado de produção encontrado.")
    else:
        df['date'] = pd.to_datetime(df['date'])
        
        c1, c2 = st.columns(2)
        start_date = c1.date_input("Início", df['date'].min(), key='d1')
        end_date = c2.date_input("Fim", df['date'].max(), key='d2')
        
        filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        
        if not filtered_df.empty:
            k1, k2, k3 = st.columns(3)
            k1.metric("Total de Fórmulas", len(filtered_df))
            
            if 'turno' in filtered_df.columns:
                k2.metric("Manhã", len(filtered_df[filtered_df['turno'] == 'manha']))
                k3.metric("Tarde", len(filtered_df[filtered_df['turno'] == 'tarde']))

            st.divider()
            
            formula_counts = filtered_df['tipo_formula'].value_counts().reset_index()
            formula_counts.columns = ['tipo_formula', 'count']
            fig_pie = px.pie(formula_counts, values='count', names='tipo_formula', title='Distribuição por Tipo', hole=.4)
            st.plotly_chart(fig_pie, use_container_width=True)

            colA, colB = st.columns(2)
            weighing_counts = filtered_df['funcionario_pesagem'].value_counts().reset_index()
            weighing_counts.columns = ['Funcionário', 'Contagem']
            fig_weighing = px.bar(weighing_counts, x='Funcionário', y='Contagem', title='Pesagem')
            colA.plotly_chart(fig_weighing, use_container_width=True)

            handling_counts = filtered_df['funcionario_manipulacao'].value_counts().reset_index()
            handling_counts.columns = ['Funcionário', 'Contagem']
            fig_handling = px.bar(handling_counts, x='Funcionário', y='Contagem', title='Manipulação')
            colB.plotly_chart(fig_handling, use_container_width=True)

# --- TAB 2: REGISTRAR FÓRMULA ---
with tab2:
    with st.form("form_formula", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        data_form = col1.date_input("Data da Produção", datetime.date.today(), format="DD/MM/YYYY")
        turno = col2.selectbox("Turno", ["manha", "tarde"])
        nr_form = col3.text_input("NR da Fórmula")

        tipo = st.selectbox("Tipo de Fórmula", ["Cápsulas", "Sachês", "Sub-Lingual/Cápsulas Oleosas", "Semi-Sólidos", "Líquidos Orais"])
        
        c_func1, c_func2, c_func3 = st.columns(3)
        
        pesagem = c_func1.selectbox("Funcionário Pesagem (Farmacêuticos)", options=[""] + farmaceuticos_prod)
        manipulacao = c_func2.selectbox("Funcionário Manipulação", options=[""] + prod_employees)
        pm = c_func3.selectbox("Funcionário PM", options=[""] + prod_employees)

        st.write("Métricas Opcionais:")
        ch1, ch2, ch3 = st.columns(3)
        ref_pm = ch1.checkbox("Refeito PM")
        ref_exc = ch1.checkbox("Refeito EXC")
        est_usado = ch2.checkbox("Estoque Usado")
        est_feito = ch2.checkbox("Estoque Feito")
        pm_20 = ch3.checkbox("PM +20")

        if st.form_submit_button("Salvar Fórmula"):
            if not nr_form or not pesagem or not manipulacao:
                st.error("Preencha NR, Pesagem e Manipulação.")
            else:
                formula_data = {
                    "date": data_form.isoformat(), "nr": nr_form, "turno": turno,
                    "tipo_formula": tipo, "funcionario_pesagem": pesagem,
                    "funcionario_manipulacao": manipulacao, "funcionario_pm": pm,
                    "refeito_pm": ref_pm, "refeito_exc": ref_exc, "estoque_usado": est_usado,
                    "estoque_feito": est_feito, "pm_mais_20": pm_20
                }
                save_record(PROD_DATA_FILE, formula_data)
                st.success("Fórmula registrada!")

# --- TAB 3: REGISTRAR ERRO DE PRODUÇÃO ---
with tab3:
    st.info("Registre quebras, perdas de insumos, ou erros de maquinário do setor de produção.")
    with st.form("form_erro_producao", clear_on_submit=True):
        
        col_dt, col_nr = st.columns(2)
        data_erro = col_dt.date_input("Data do Erro", datetime.date.today(), format="DD/MM/YYYY")
        nr_erro = col_nr.text_input("NR (se aplicável)")
        
        func_erro = st.selectbox("Funcionário Envolvido", options=[""] + prod_employees)
        
        tipos_prod = get_error_types(PROD_ERROR_TYPES)
        tipos_erro_prod = st.multiselect("Tipos de Erro de Produção", options=tipos_prod)
        
        custo = st.number_input("Custo Estimado (R$)", min_value=0.0)
        penalidade = st.number_input("Penalidade na Meta (%)", min_value=0, max_value=100, step=5) # NOVO CAMPO
        obs_erro = st.text_area("Descreva o que aconteceu")
        
        if st.form_submit_button("Salvar Erro de Produção"):
            if not tipos_erro_prod:
                st.error("Selecione o tipo do erro.")
            else:
                record = {
                    "date": data_erro.isoformat(),
                    "nr": nr_erro, "funcionario": func_erro, "tipos_erro": tipos_erro_prod,
                    "custo": custo, "penalidade": penalidade, "observacoes": obs_erro
                }
                save_record(PROD_ERROR_DATA, record)
                st.success("Erro de produção registrado!")

# --- TAB 4: CONSULTAR NR (NEW) ---
with tab4:
    busca_nr = st.text_input("Digite o NR para buscar na Produção:")
    if st.button("Buscar NR"):
        formulas_encontradas = search_by_nr(PROD_DATA_FILE, busca_nr)
        erros_encontrados = search_by_nr(PROD_ERROR_DATA, busca_nr)
        
        if not formulas_encontradas and not erros_encontrados:
            st.warning(f"Nenhum registro (Fórmula ou Erro) encontrado para o NR: {busca_nr}")
        else:
            if formulas_encontradas:
                st.subheader("💊 Histórico de Produção")
                for f in formulas_encontradas:
                    st.json(f)
                    
            if erros_encontrados:
                st.subheader("⚠️ Histórico de Erros Associados")
                for e in erros_encontrados:
                    st.json(e)