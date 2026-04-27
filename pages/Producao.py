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
# --- TAB 1: DASHBOARD (UPGRADED VERSION) ---
with tab1:
    st.subheader("📊 Dashboard de Produção")

    df = pd.DataFrame(load_json(PROD_DATA_FILE, []))

    if df.empty:
        st.warning("Nenhum dado de produção encontrado.")
        st.stop()

    # =========================
    # SAFE PREPROCESSING
    # =========================
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    bool_cols = [
        'refeito_pm', 'refeito_exc',
        'estoque_usado', 'estoque_feito',
        'pm_mais_20'
    ]

    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
        else:
            df[col] = False

    # =========================
    # FILTER BY DATE
    # =========================
    col1, col2 = st.columns(2)

    start_date = col1.date_input("📅 Início", df['date'].min().date())
    end_date = col2.date_input("📅 Fim", df['date'].max().date())

    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    filtered_df = df.loc[mask].copy()

    if filtered_df.empty:
        st.warning("Nenhum dado no período selecionado.")
        st.stop()

    # =========================
    # DERIVED GROUPS
    # =========================
    solids = ['Cápsulas', 'Sub-lingual/oleosas', 'Sachês']
    semi = ['Semi-Sólidos', 'Líquidos Orais']

    df_solids = filtered_df[filtered_df['tipo_formula'].isin(solids)]
    df_semi = filtered_df[filtered_df['tipo_formula'].isin(semi)]

    # =========================
    # KPIs (INTELLIGENT LAYER)
    # =========================
    total = len(filtered_df)
    solids_total = len(df_solids)
    semi_total = len(df_semi)

    estoque_rate = (
        filtered_df['estoque_feito'].mean() * 100
        if 'estoque_feito' in filtered_df else 0
    )

    refeito_rate = (
        (filtered_df['refeito_pm'].sum() + filtered_df['refeito_exc'].sum()) / total * 100
    )

    pm20_total = filtered_df['pm_mais_20'].sum()

   # =========================
    # PROPER TURNO FROM TIME FIELD
    # =========================

    filtered_df = filtered_df.copy()

    filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')

    def get_turno(row):
        # 1. if explicit turno exists and is valid
        if 'turno' in row and str(row.get('turno')).lower() in ['manha', 'tarde']:
            return str(row['turno']).lower()

        # 2. USE TIME FIELD (THIS IS YOUR SOURCE OF TRUTH)
        if pd.notnull(row.get('time')):
            try:
                hour = int(str(row['time']).split(':')[0])
                return 'manha' if hour < 12 else 'tarde'
            except:
                pass

        # 3. last fallback (never ideal)
        return 'desconhecido'

    filtered_df['turno'] = filtered_df.apply(get_turno, axis=1)

    # clean groups
    manha_df = filtered_df[filtered_df['turno'] == 'manha']
    tarde_df = filtered_df[filtered_df['turno'] == 'tarde']

    manha = len(manha_df)
    tarde = len(tarde_df)

    # =========================
    # KPI UI
    # =========================
    st.divider()
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("📦 Total Fórmulas", total)
    c2.metric("🌞 Manhã", manha)
    c3.metric("🌙 Tarde", tarde)
    c4.metric("🧪 Estoque Feito %", f"{estoque_rate:.1f}%")
    c5.metric("⚠️ Refeito %", f"{refeito_rate:.1f}%")

    c6, c7, c8 = st.columns(3)
    c6.metric("💊 Sólidos", solids_total)
    c7.metric("💧 Semi/Líquidos", semi_total)
    c8.metric("📈 PM +20", pm20_total)

    st.divider()

    # =========================
    # CHARTS
    # =========================

    # 1. Tipo de fórmula
    fig_pie = px.pie(
        filtered_df,
        names='tipo_formula',
        title="📊 Distribuição por Tipo de Fórmula",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    colA, colB, colC = st.columns(3)

    # 2. Produção por pesagem/manipulação/PM
    prod = filtered_df.melt(
        id_vars=['date'],
        value_vars=['funcionario_pesagem', 'funcionario_manipulacao', 'funcionario_pm'],
        var_name='etapa',
        value_name='funcionario'
    )

    prod_counts = prod['funcionario'].value_counts().reset_index()
    prod_counts.columns = ['Funcionário', 'Produções']

    fig_prod = px.bar(
        prod_counts,
        x='Funcionário',
        y='Produções',
        title="👷 Produção por Funcionário",
        text_auto=True
    )

    colA.plotly_chart(fig_prod, use_container_width=True)

    # 3. Pesagem
    pesagem = filtered_df['funcionario_pesagem'].value_counts().reset_index()
    pesagem.columns = ['Funcionário', 'Qtd']

    fig_pes = px.bar(pesagem, x='Funcionário', y='Qtd', title="⚖️ Pesagem", text_auto=True)
    colB.plotly_chart(fig_pes, use_container_width=True)

    # 4. Manipulação
    manip = filtered_df['funcionario_manipulacao'].value_counts().reset_index()
    manip.columns = ['Funcionário', 'Qtd']

    fig_man = px.bar(manip, x='Funcionário', y='Qtd', title="🧪 Manipulação", text_auto=True)
    colC.plotly_chart(fig_man, use_container_width=True)

    st.divider()

    # =========================
    # REWORK / QUALITY
    # =========================

    colD, colE, colF = st.columns(3)

    re_pm = filtered_df[filtered_df['refeito_pm'] == True]['funcionario_manipulacao'].value_counts().reset_index()
    re_pm.columns = ['Funcionário', 'Qtd']
    fig_repm = px.bar(re_pm, x='Funcionário', y='Qtd', title="🔁 Refeito PM", text_auto=True)
    colD.plotly_chart(fig_repm, use_container_width=True)

    re_exc = filtered_df[filtered_df['refeito_exc'] == True]['funcionario_pesagem'].value_counts().reset_index()
    re_exc.columns = ['Funcionário', 'Qtd']
    fig_reexc = px.bar(re_exc, x='Funcionário', y='Qtd', title="⚠️ Refeito EXC", text_auto=True)
    colE.plotly_chart(fig_reexc, use_container_width=True)

    pm20 = filtered_df[filtered_df['pm_mais_20'] == True]['funcionario_manipulacao'].value_counts().reset_index()
    pm20.columns = ['Funcionário', 'Qtd']
    fig_pm20 = px.bar(pm20, x='Funcionário', y='Qtd', title="📈 PM +20", text_auto=True)
    colF.plotly_chart(fig_pm20, use_container_width=True)

    st.divider()

    # =========================
    # TIMELINE INSIGHTS
    # =========================
    freq = st.selectbox("📅 Agrupar por:", ["D", "W", "M"], format_func=lambda x: {"D": "Dia", "W": "Semana", "M": "Mês"}[x])

    timeline = filtered_df.groupby(pd.Grouper(key='date', freq=freq)).size().reset_index(name='count')

    fig_time = px.line(
        timeline,
        x='date',
        y='count',
        markers=True,
        title="📈 Produção ao Longo do Tempo"
    )

    st.plotly_chart(fig_time, use_container_width=True)

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