import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from utils import get_employees, get_error_types, save_record, search_by_nr, load_json, SALES_DATA_FILE, SALES_ERROR_TYPES

st.set_page_config(page_title="Vendas", layout="wide")
st.title("🛒 Setor de Vendas")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Erros", "📝 Registrar Erro", "🔍 Consultar NR"])

# --- EMPLOYEES FILTER ---
all_employees = get_employees()
vendas_employees = [
    name for name, data in all_employees.items() 
    if data.get("setor", "Ambos") in ["Vendas", "Ambos"]
]

# =========================================================
# TAB 1 — DASHBOARD
# =========================================================
with tab1:
    st.subheader("📊 Dashboard Financeiro")

    df = pd.DataFrame(load_json(SALES_DATA_FILE, []))

    if df.empty:
        st.warning("Nenhum dado encontrado.")
        st.stop()

    # --- CLEANING ---
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Ensure tipos_erro is always a list
    if 'tipos_erro' in df.columns:
        df['tipos_erro'] = df['tipos_erro'].apply(
            lambda x: x if isinstance(x, list) else ([x] if pd.notna(x) else [])
        )
    else:
        df['tipos_erro'] = [[] for _ in range(len(df))]

    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
    if 'penalidade' not in df.columns:
        df['penalidade'] = 0

    df['penalidade'] = pd.to_numeric(df['penalidade'], errors='coerce').fillna(0)

    # --- FILTERS ---
    col1, col2, col3 = st.columns(3)

    start_date = col1.date_input("Data Início", df['date'].min())
    end_date = col2.date_input("Data Fim", df['date'].max())

    freq = col3.selectbox(
        "Agrupar por",
        ["D", "W", "M"],
        format_func=lambda x: {"D": "Dia", "W": "Semana", "M": "Mês"}[x]
    )

    employees = sorted(df['funcionario'].dropna().unique())
    selected_employees = st.multiselect(
        "Filtrar Funcionários",
        options=employees,
        default=employees
    )

    # Apply filters
    mask = (
        (df['date'].dt.date >= start_date) &
        (df['date'].dt.date <= end_date) &
        (df['funcionario'].isin(selected_employees))
    )
    filtered_df = df.loc[mask]

    if filtered_df.empty:
        st.warning("Sem dados no período selecionado.")
        st.stop()

    # =========================================================
    # KPIs
    # =========================================================
    total_cost = filtered_df['valor'].sum()
    total_errors = len(filtered_df)
    avg_cost = filtered_df['valor'].mean()
    total_penalty = filtered_df['penalidade'].sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Custo Total", f"R$ {total_cost:,.2f}")
    k2.metric("📉 Ocorrências", total_errors)
    k3.metric("📊 Custo Médio", f"R$ {avg_cost:,.2f}")
    k4.metric("⚠️ Penalidade Total (%)", f"{total_penalty:.0f}")

    # =========================================================
    # GRAPHS ROW 1
    # =========================================================
    c1, c2 = st.columns(2)

    # --- TIME SERIES ---
    cost_over_time = filtered_df.groupby(pd.Grouper(key='date', freq=freq))['valor'].sum().reset_index()

    fig_time = px.line(
        cost_over_time,
        x='date',
        y='valor',
        markers=True,
        title="Evolução do Prejuízo"
    )
    fig_time.update_traces(line_width=3)

    c1.plotly_chart(fig_time, use_container_width=True)

    # --- COST BY EMPLOYEE ---
    cost_by_emp = (
        filtered_df.groupby('funcionario')['valor']
        .sum()
        .reset_index()
        .sort_values('valor')
    )

    fig_emp = px.bar(
        cost_by_emp,
        x='valor',
        y='funcionario',
        orientation='h',
        title="Prejuízo por Funcionário",
        text_auto='.2f'
    )

    c2.plotly_chart(fig_emp, use_container_width=True)

    # =========================================================
    # GRAPHS ROW 2 — RANKING + ERROR DISTRIBUTION
    # =========================================================
    c3, c4 = st.columns(2)

    # --- TOP OFFENDERS ---
    top_offenders = cost_by_emp.sort_values('valor', ascending=False).head(5)

    fig_top = px.bar(
        top_offenders,
        x='valor',
        y='funcionario',
        orientation='h',
        title="Top 5 Maiores Prejuízos",
        text_auto=True
    )

    c3.plotly_chart(fig_top, use_container_width=True)

    # --- ERROR TYPE DISTRIBUTION ---
    exploded = filtered_df.explode('tipos_erro')
    error_dist = exploded['tipos_erro'].value_counts().reset_index()
    error_dist.columns = ['Erro', 'Quantidade']

    fig_err = px.pie(
        error_dist,
        names='Erro',
        values='Quantidade',
        title="Distribuição de Tipos de Erro"
    )

    c4.plotly_chart(fig_err, use_container_width=True)

    # =========================================================
    # INDIVIDUAL ANALYSIS
    # =========================================================
    st.markdown("---")
    st.subheader("🔍 Análise Individual")

    selected_employee = st.selectbox(
        "Selecionar Funcionário",
        options=employees
    )

    emp_df = filtered_df[filtered_df['funcionario'] == selected_employee]

    if not emp_df.empty:
        emp_df = emp_df.explode('tipos_erro')

        error_counts = emp_df['tipos_erro'].value_counts().reset_index()
        error_counts.columns = ['Erro', 'Quantidade']

        fig_detail = px.bar(
            error_counts,
            x='Erro',
            y='Quantidade',
            title=f"Erros de {selected_employee}",
            text_auto=True
        )

        st.plotly_chart(fig_detail, use_container_width=True)

        # EXTRA: COST BY ERROR TYPE
        cost_by_error = emp_df.groupby('tipos_erro')['valor'].sum().reset_index()

        fig_cost_error = px.bar(
            cost_by_error,
            x='tipos_erro',
            y='valor',
            title=f"Custo por Tipo de Erro ({selected_employee})",
            text_auto=True
        )

        st.plotly_chart(fig_cost_error, use_container_width=True)

    else:
        st.info("Sem dados para esse funcionário.")

# =========================================================
# TAB 2 — REGISTRAR ERRO
# =========================================================
with tab2:
    with st.form("form_erro_venda", clear_on_submit=True):
        st.subheader("📝 Registrar Novo Erro")
        
        col1, col2, col3, col4 = st.columns(4)
        data_erro = col1.date_input("Data", datetime.date.today())
        nr = col2.text_input("NR")
        valor = col3.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        penalidade = col4.number_input("Penalidade (%)", 0, 100, step=5)

        funcionario = st.selectbox("Funcionário", [""] + vendas_employees)

        tipos = get_error_types(SALES_ERROR_TYPES)
        erros = st.multiselect("Tipos de Erro", tipos)

        st.markdown("### Detalhes")
        c1, c2, c3 = st.columns(3)

        desconto = c1.checkbox("Desconto")
        cobrado = c1.checkbox("Cobrado")
        acrescimo = c2.checkbox("Acréscimo")
        credito = c2.checkbox("Crédito")
        reaproveitamento = c3.checkbox("Reaproveitamento")
        produto_refeito = c3.checkbox("Produto Refeito")
        nao_mudou = c3.checkbox("Não mudou valor")

        obs = st.text_area("Observações")

        if st.form_submit_button("Salvar"):
            if not nr or not funcionario or not erros:
                st.error("Preencha os campos obrigatórios.")
            else:
                record = {
                    "date": data_erro.isoformat(),
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "nr": nr,
                    "funcionario": funcionario,
                    "valor": valor,
                    "tipos_erro": erros,
                    "penalidade": penalidade,
                    "desconto": desconto,
                    "cobrado": cobrado,
                    "acrescimo": acrescimo,
                    "deixado_credito": credito,
                    "reaproveitamento": reaproveitamento,
                    "produto_refeito": produto_refeito,
                    "nao_mudou_valor": nao_mudou,
                    "observacoes": obs
                }

                save_record(SALES_DATA_FILE, record)
                st.success("Erro registrado!")

# =========================================================
# TAB 3 — CONSULTA
# =========================================================
with tab3:
    st.subheader("🔍 Buscar por NR")

    busca = st.text_input("Digite o NR")

    if st.button("Buscar"):
        results = search_by_nr(SALES_DATA_FILE, busca)

        if results:
            for r in results:
                st.json(r)
        else:
            st.warning("NR não encontrado.")