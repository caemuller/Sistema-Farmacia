import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from utils import get_employees, get_error_types, save_record, search_by_nr, load_json, SALES_DATA_FILE, SALES_ERROR_TYPES

st.set_page_config(page_title="Vendas", layout="wide")
st.title("🛒 Setor de Vendas")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Erros", "📝 Registrar Erro", "🔍 Consultar NR"])

# Filter employees for Sales
all_employees = get_employees()
# Get only employees assigned to Vendas or Ambos
vendas_employees = [
    name for name, data in all_employees.items() 
    if data.get("setor", "Ambos") in ["Vendas", "Ambos"]
]

# --- TAB 1: DASHBOARD ---
with tab1:
    st.subheader("Dashboard Financeiro de Erros")
    df = pd.DataFrame(load_json(SALES_DATA_FILE, []))
    
    if df.empty:
        st.warning("Nenhum dado de vendas encontrado.")
    else:
        df['date'] = pd.to_datetime(df['date'])
        
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Data Início", df['date'].min())
        end_date = col2.date_input("Data Fim", df['date'].max())
        freq = st.selectbox("Agrupar por:", options=["D", "W", "M"], format_func=lambda x: "Dia" if x=="D" else "Semana" if x=="W" else "Mês")
        
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        filtered_df = df.loc[mask]

        if not filtered_df.empty:
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Custo Total", f"R$ {filtered_df['valor'].sum():,.2f}")
            kpi2.metric("Quantidade de Erros", len(filtered_df))
            kpi3.metric("Custo Médio", f"R$ {filtered_df['valor'].mean():,.2f}")

            c1, c2 = st.columns(2)
            cost_over_time = filtered_df.groupby(pd.Grouper(key='date', freq=freq))['valor'].sum().reset_index()
            fig_time = px.line(cost_over_time, x='date', y='valor', markers=True, title="Evolução do Prejuízo")
            c1.plotly_chart(fig_time, use_container_width=True)

            cost_by_emp = filtered_df.groupby('funcionario')['valor'].sum().reset_index().sort_values('valor')
            fig_emp = px.bar(cost_by_emp, x='valor', y='funcionario', orientation='h', title="Prejuízo por Funcionário")
            c2.plotly_chart(fig_emp, use_container_width=True)

# --- TAB 2: REGISTRAR ERRO ---
with tab2:
    with st.form("form_erro_venda", clear_on_submit=True):
        st.subheader("Registrar Novo Erro")
        
        col1, col2, col3 = st.columns(3)
        data_erro = col1.date_input("Data do Erro", datetime.date.today(), format="DD/MM/YYYY")
        nr = col2.text_input("NR do Pedido")
        valor = col3.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        
        # Uses filtered sales employees
        funcionario = st.selectbox("Funcionário Envolvido", options=[""] + vendas_employees)
        
        tipos = get_error_types(SALES_ERROR_TYPES)
        erros_selecionados = st.multiselect("Tipos de Erro", options=tipos)
        
        st.write("Detalhes / Solução:")
        chk1, chk2, chk3 = st.columns(3)
        desconto = chk1.checkbox("Desconto")
        cobrado = chk1.checkbox("Cobrado")
        acrescimo = chk2.checkbox("Acréscimo")
        deixado_credito = chk2.checkbox("Deixado de Crédito")
        reaproveitamento = chk3.checkbox("Reaproveitamento")
        produto_refeito = chk3.checkbox("Produto Refeito")
        nao_mudou_valor = chk3.checkbox("Não mudou valor")
        
        obs = st.text_area("Observações")
        
        if st.form_submit_button("Salvar Erro"):
            if not nr or not funcionario or not erros_selecionados:
                st.error("Preencha NR, Funcionário e Tipo de Erro.")
            else:
                record = {
                    "date": data_erro.isoformat(),
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "nr": nr, "tipos_erro": erros_selecionados, "funcionario": funcionario, "valor": valor,
                    "desconto": desconto, "cobrado": cobrado, "acrescimo": acrescimo,
                    "deixado_credito": deixado_credito, "reaproveitamento": reaproveitamento,
                    "produto_refeito": produto_refeito, "nao_mudou_valor": nao_mudou_valor, "observacoes": obs
                }
                save_record(SALES_DATA_FILE, record)
                st.success("Erro registrado!")

# --- TAB 3: CONSULTAR NR ---
with tab3:
    busca_nr = st.text_input("Digite o NR para buscar (Vendas):")
    if st.button("Buscar"):
        resultados = search_by_nr(SALES_DATA_FILE, busca_nr)
        if resultados:
            for r in resultados:
                st.json(r)
        else:
            st.warning("NR não encontrado.")