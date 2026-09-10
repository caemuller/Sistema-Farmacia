import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
from utils import get_employees, get_error_types, save_record, search_by_nr, load_json, PROD_DATA_FILE, PROD_ERROR_DATA, PROD_ERROR_TYPES

st.set_page_config(page_title="Produção", layout="wide")
st.title("🏭 Setor de Produção")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard de Fórmulas", 
    "📉 Dashboard de Erros", 
    "💊 Registrar Fórmula", 
    "⚠️ Registrar Erro", 
    "🔍 Consultar NR"
])

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

# =========================================================
# TAB 1: DASHBOARD DE FÓRMULAS
# =========================================================
with tab1:
    st.subheader("📊 Dashboard de Produção")
    st.info(f"🔍 DEBUG: Procurando arquivo no caminho exato: {os.path.abspath(PROD_DATA_FILE)}")

    df = pd.DataFrame(load_json(PROD_DATA_FILE, []))

    if df.empty:
        st.warning("Nenhum dado de produção encontrado.")
    else:
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

        col1, col2 = st.columns(2)
        start_date = col1.date_input("📅 Início", df['date'].min().date())
        end_date = col2.date_input("📅 Fim", df['date'].max().date())

        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
        filtered_df = df.loc[mask].copy()

        if filtered_df.empty:
            st.warning("Nenhum dado no período selecionado.")
        else:
            solids = ['Cápsulas', 'Sub-lingual/oleosas', 'Sachês']
            semi = ['Semi-Sólidos', 'Líquidos Orais']

            df_solids = filtered_df[filtered_df['tipo_formula'].isin(solids)]
            df_semi = filtered_df[filtered_df['tipo_formula'].isin(semi)]

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

            def get_turno(row):
                if 'turno' in row and str(row.get('turno')).lower() in ['manha', 'tarde']:
                    return str(row['turno']).lower()
                if pd.notnull(row.get('time')):
                    try:
                        hour = int(str(row['time']).split(':')[0])
                        return 'manha' if hour < 12 else 'tarde'
                    except:
                        pass
                return 'desconhecido'

            filtered_df['turno'] = filtered_df.apply(get_turno, axis=1)

            manha_df = filtered_df[filtered_df['turno'] == 'manha']
            tarde_df = filtered_df[filtered_df['turno'] == 'tarde']

            manha = len(manha_df)
            tarde = len(tarde_df)

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

            fig_pie = px.pie(
                filtered_df,
                names='tipo_formula',
                title="📊 Distribuição por Tipo de Fórmula",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            colA, colB, colC = st.columns(3)

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
                title="👷 Produção Geral por Funcionário",
                text_auto=True
            )
            colA.plotly_chart(fig_prod, use_container_width=True)

            pesagem = filtered_df['funcionario_pesagem'].value_counts().reset_index()
            pesagem.columns = ['Funcionário', 'Qtd']
            fig_pes = px.bar(pesagem, x='Funcionário', y='Qtd', title="⚖️ Pesagem", text_auto=True)
            colB.plotly_chart(fig_pes, use_container_width=True)

            manip = filtered_df['funcionario_manipulacao'].value_counts().reset_index()
            manip.columns = ['Funcionário', 'Qtd']
            fig_man = px.bar(manip, x='Funcionário', y='Qtd', title="🧪 Manipulação", text_auto=True)
            colC.plotly_chart(fig_man, use_container_width=True)

            st.divider()

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
            
            # Gráfico de evolução temporal GERAL
            st.subheader("📈 Evolução da Produção Geral")
            freq = st.selectbox("📅 Agrupar timeline por:", ["D", "W", "M"], format_func=lambda x: {"D": "Dia", "W": "Semana", "M": "Mês"}[x])
            timeline = filtered_df.groupby(pd.Grouper(key='date', freq=freq)).size().reset_index(name='count')
            fig_time = px.line(timeline, x='date', y='count', markers=True, title="Fórmulas Produzidas (Todos os Setores)")
            st.plotly_chart(fig_time, use_container_width=True)

            # =========================================================
            # NOVO: ANÁLISE INDIVIDUAL DE DESEMPENHO NO TEMPO
            # =========================================================
            st.divider()
            st.subheader("🔍 Análise de Desempenho Individual")
            st.markdown("Veja quantas pesagens, manipulações ou PMs um funcionário específico fez ao longo do período.")
            
            # Pegar lista única de todos que trabalharam neste período
            all_prod_ativos = pd.unique(filtered_df[['funcionario_pesagem', 'funcionario_manipulacao', 'funcionario_pm']].values.ravel('K'))
            all_prod_ativos = [e for e in all_prod_ativos if pd.notna(e) and e != ""]
            
            selected_emp_prod = st.selectbox(
                "Selecionar Funcionário para ver evolução:", 
                options=sorted(all_prod_ativos), 
                key="timeline_individual"
            )
            
            if selected_emp_prod:
                # Filtrar as datas que o funcionário atuou em cada etapa e taguear
                df_pes = filtered_df[filtered_df['funcionario_pesagem'] == selected_emp_prod][['date']].copy()
                df_pes['Atividade'] = 'Pesagem'
                
                df_man = filtered_df[filtered_df['funcionario_manipulacao'] == selected_emp_prod][['date']].copy()
                df_man['Atividade'] = 'Manipulação'
                
                df_pm = filtered_df[filtered_df['funcionario_pm'] == selected_emp_prod][['date']].copy()
                df_pm['Atividade'] = 'PM'
                
                # Unir tudo
                df_emp_all = pd.concat([df_pes, df_man, df_pm])
                
                if not df_emp_all.empty:
                    # Agrupar por data (usando a frequência escolhida acima) e por atividade
                    emp_timeline = df_emp_all.groupby([pd.Grouper(key='date', freq=freq), 'Atividade']).size().reset_index(name='Quantidade')
                    
                    fig_emp_time = px.line(
                        emp_timeline,
                        x='date', 
                        y='Quantidade', 
                        color='Atividade', 
                        markers=True,
                        title=f"Desempenho ao longo do tempo: {selected_emp_prod}"
                    )
                    # Forçar o eixo Y a começar no 0
                    fig_emp_time.update_layout(yaxis_rangemode="tozero")
                    st.plotly_chart(fig_emp_time, use_container_width=True)
                else:
                    st.info(f"{selected_emp_prod} não teve registros no período selecionado.")

# =========================================================
# TAB 2: DASHBOARD DE ERROS (NOVO PARA A KAU)
# =========================================================
with tab2:
    st.subheader("📉 Dashboard de Erros e Prejuízos")

    df_erros = pd.DataFrame(load_json(PROD_ERROR_DATA, []))

    if df_erros.empty:
        st.success("🎉 Nenhum erro de produção registrado ainda!")
    else:
        df_erros['date'] = pd.to_datetime(df_erros['date'], errors='coerce')

        if 'tipos_erro' in df_erros.columns:
            df_erros['tipos_erro'] = df_erros['tipos_erro'].apply(
                lambda x: x if isinstance(x, list) else ([x] if pd.notna(x) else [])
            )
        else:
            df_erros['tipos_erro'] = [[] for _ in range(len(df_erros))]

        df_erros['custo'] = pd.to_numeric(df_erros.get('custo', 0), errors='coerce').fillna(0)
        df_erros['penalidade'] = pd.to_numeric(df_erros.get('penalidade', 0), errors='coerce').fillna(0)

        # Filtros
        col1, col2 = st.columns(2)
        start_date_err = col1.date_input("Data Início", df_erros['date'].min().date(), key="start_err_prod")
        end_date_err = col2.date_input("Data Fim", df_erros['date'].max().date(), key="end_err_prod")

        employees_err = sorted(df_erros['funcionario'].dropna().unique())
        selected_employees_err = st.multiselect(
            "Filtrar Colaboradores",
            options=employees_err,
            default=employees_err,
            key="emp_err_prod"
        )

        mask_err = (
            (df_erros['date'].dt.date >= start_date_err) &
            (df_erros['date'].dt.date <= end_date_err) &
            (df_erros['funcionario'].isin(selected_employees_err))
        )
        filtered_erros = df_erros.loc[mask_err]

        if filtered_erros.empty:
            st.warning("Sem dados de erros no período selecionado.")
        else:
            total_custo = filtered_erros['custo'].sum()
            total_ocorrencias = len(filtered_erros)
            total_penalidade = filtered_erros['penalidade'].sum()

            k1, k2, k3 = st.columns(3)
            k1.metric("💰 Custo Estimado Total", f"R$ {total_custo:,.2f}")
            k2.metric("📉 Ocorrências Registradas", total_ocorrencias)
            k3.metric("⚠️ Penalidade Total Aplicada (%)", f"{total_penalidade:.0f}")

            c1, c2 = st.columns(2)

            # Custo por funcionário
            custo_by_emp = filtered_erros.groupby('funcionario')['custo'].sum().reset_index().sort_values('custo', ascending=True)
            fig_custo_emp = px.bar(
                custo_by_emp, x='custo', y='funcionario', orientation='h',
                title="Custo de Erros por Colaborador", text_auto='.2f'
            )
            c1.plotly_chart(fig_custo_emp, width="stretch")

            # Distribuição de Erros
            exploded_err = filtered_erros.explode('tipos_erro')
            error_dist = exploded_err['tipos_erro'].value_counts().reset_index()
            error_dist.columns = ['Erro', 'Quantidade']
            fig_err_dist = px.pie(
                error_dist, names='Erro', values='Quantidade',
                title="Distribuição de Tipos de Erro", hole=0.3
            )
            c2.plotly_chart(fig_err_dist, width="stretch")

            # Tabela de Detalhamento Individual
            st.divider()
            st.subheader("🔍 Análise Individual e Detalhamento de Erros")
            
            selected_employee_detail = st.selectbox(
                "Selecionar Colaborador para expandir Histórico",
                options=employees_err,
                key="drill_err_prod"
            )

            raw_emp_df = filtered_erros[filtered_erros['funcionario'] == selected_employee_detail].copy()

            if not raw_emp_df.empty:
                unique_errors = sorted(list(set([err for sublist in raw_emp_df['tipos_erro'] for err in sublist])))
                
                col_f1, col_f2 = st.columns(2)
                search_nr = col_f1.text_input(f"🔍 Filtrar NR (ex: 382872):", key="search_nr_err_prod")
                filter_errors = col_f2.multiselect(f"⚠️ Filtrar tipos de erro de {selected_employee_detail}:", options=unique_errors, key="filter_tipo_err_prod")

                display_df = raw_emp_df[['date', 'nr', 'tipos_erro', 'custo', 'penalidade', 'observacoes']].copy()

                if search_nr:
                    display_df = display_df[display_df['nr'].astype(str).str.contains(search_nr, na=False)]
                
                if filter_errors:
                    display_df = display_df[display_df['tipos_erro'].apply(lambda x: any(err in x for err in filter_errors))]

                display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')
                display_df['tipos_erro'] = display_df['tipos_erro'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
                display_df['custo'] = display_df['custo'].apply(lambda x: f"R$ {x:,.2f}")
                display_df['observacoes'] = display_df['observacoes'].fillna("-")

                display_df.columns = ["Data", "NR", "Tipos de Erro", "Custo Estimado", "Penalidade (%)", "Observações"]
                
                st.dataframe(display_df, width="stretch", hide_index=True)
                st.caption(f"**Total de Ocorrências exibidas para {selected_employee_detail}:** {len(display_df)}")

# =========================================================
# TAB 3: REGISTRAR FÓRMULA
# =========================================================
with tab3:
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

# =========================================================
# TAB 4: REGISTRAR ERRO DE PRODUÇÃO
# =========================================================
with tab4:
    st.info("Registre quebras, perdas de insumos, ou erros de maquinário do setor de produção.")
    with st.form("form_erro_producao", clear_on_submit=True):
        
        col_dt, col_nr = st.columns(2)
        data_erro = col_dt.date_input("Data do Erro", datetime.date.today(), format="DD/MM/YYYY")
        nr_erro = col_nr.text_input("NR (se aplicável)")
        
        func_erro = st.selectbox("Funcionário Envolvido", options=[""] + prod_employees)
        
        tipos_prod = get_error_types(PROD_ERROR_TYPES)
        tipos_erro_prod = st.multiselect("Tipos de Erro de Produção", options=tipos_prod)
        
        custo = st.number_input("Custo Estimado (R$)", min_value=0.0)
        penalidade = st.number_input("Penalidade na Meta (%)", min_value=0, max_value=100, step=5)
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

# =========================================================
# TAB 5: CONSULTAR NR
# =========================================================
with tab5:
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
