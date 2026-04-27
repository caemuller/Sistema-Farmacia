import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from utils import load_json, SALES_DATA_FILE, PROD_ERROR_DATA, get_employees

st.set_page_config(page_title="Metas e Premiações", layout="wide")
st.title("🎯 Metas e Controle de Premiações")
st.markdown("Acompanhe o impacto dos erros registrados na meta de premiação da equipe. Todo funcionário inicia o mês com **100%** de atingimento.")

# --- FILTROS DE DATA ---
st.subheader("Filtro de Período")
col1, col2 = st.columns(2)
hoje = datetime.date.today()
start_date = col1.date_input("Data Início", datetime.date(hoje.year, hoje.month, 1))
end_date = col2.date_input("Data Fim", hoje)

# --- CARREGAR E PROCESSAR DADOS ---
# Carrega os erros de ambos os setores
erros_vendas = load_json(SALES_DATA_FILE, [])
erros_prod = load_json(PROD_ERROR_DATA, [])

# Unifica as listas padronizando os campos importantes
erros_unificados = []
for erro in erros_vendas:
    erros_unificados.append({
        "Data": erro.get("date"),
        "Setor_Erro": "Vendas",
        "Funcionario": erro.get("funcionario", "Desconhecido"),
        "Penalidade": erro.get("penalidade", 0), # Usa 0 se o erro for antigo e não tiver o campo
        "Detalhe": str(erro.get("tipos_erro", []))
    })

for erro in erros_prod:
    erros_unificados.append({
        "Data": erro.get("date"),
        "Setor_Erro": "Produção",
        "Funcionario": erro.get("funcionario", "Desconhecido"),
        "Penalidade": erro.get("penalidade", 0),
        "Detalhe": str(erro.get("tipos_erro", []))
    })

df_erros = pd.DataFrame(erros_unificados)

# Verifica se há dados no período
if df_erros.empty:
    st.info("Nenhum erro registrado no sistema ainda.")
else:
    df_erros['Data'] = pd.to_datetime(df_erros['Data'])
    mask = (df_erros['Data'].dt.date >= start_date) & (df_erros['Data'].dt.date <= end_date)
    df_filtrado = df_erros.loc[mask]

    if df_filtrado.empty:
        st.success("🎉 Nenhum erro com penalidade registrado neste período!")
    else:
        # Agrupa os dados por funcionário
        df_resumo = df_filtrado.groupby('Funcionario').agg(
            Total_Erros=('Funcionario', 'count'),
            Penalidade_Acumulada=('Penalidade', 'sum')
        ).reset_index()

        # Calcula a meta restante (Mínimo de 0%)
        df_resumo['Premiação Restante (%)'] = 100 - df_resumo['Penalidade_Acumulada']
        df_resumo['Premiação Restante (%)'] = df_resumo['Premiação Restante (%)'].apply(lambda x: max(0, x))

        # Adiciona funcionários que não erraram (para justiça)
        todos_funcs = list(get_employees().keys())
        funcs_sem_erro = [f for f in todos_funcs if f not in df_resumo['Funcionario'].values]
        df_sem_erro = pd.DataFrame({
            'Funcionario': funcs_sem_erro,
            'Total_Erros': 0,
            'Penalidade_Acumulada': 0,
            'Premiação Restante (%)': 100
        })
        
        # Junta tudo e ordena para mostrar quem perdeu mais primeiro
        df_final = pd.concat([df_resumo, df_sem_erro], ignore_index=True)
        df_final = df_final.sort_values(by='Premiação Restante (%)', ascending=True)

        st.divider()

        # --- VISUALIZAÇÃO ---
        c1, c2 = st.columns([2, 1])

        with c1:
            st.subheader("📊 Tabela de Desempenho")
            # Usando data_editor para uma tabela nativa estilizada com barra de progresso
            st.dataframe(
                df_final,
                column_config={
                    "Premiação Restante (%)": st.column_config.ProgressColumn(
                        "Premiação Restante (%)",
                        help="Meta atual do funcionário no período",
                        format="%f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Penalidade_Acumulada": st.column_config.NumberColumn(
                        "Penalidade Total (%)",
                        format="-%d%%"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

        with c2:
            st.subheader("📉 Impacto por Setor")
            impacto_setor = df_filtrado.groupby('Setor_Erro')['Penalidade'].sum().reset_index()
            fig = px.pie(impacto_setor, values='Penalidade', names='Setor_Erro', hole=0.4, title='Penalidades Aplicadas por Setor')
            st.plotly_chart(fig, use_container_width=True)

        # --- EXTRATO DETALHADO ---
        st.divider()
        st.subheader("🧾 Extrato Detalhado de Penalidades")
        st.markdown("Histórico de todos os erros que geraram dedução neste período.")
        
        # Mostra apenas erros que tiveram penalidade > 0
        df_extrato = df_filtrado[df_filtrado['Penalidade'] > 0].copy()
        if not df_extrato.empty:
            df_extrato['Data'] = df_extrato['Data'].dt.strftime('%d/%m/%Y')
            df_extrato = df_extrato[['Data', 'Funcionario', 'Setor_Erro', 'Detalhe', 'Penalidade']].sort_values('Data', ascending=False)
            st.dataframe(df_extrato, hide_index=True, use_container_width=True)
        else:
            st.write("Nenhum erro com penalidade atrelada neste período.")