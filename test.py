import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# Load and preprocess the data
df = pd.read_json("fake_data.json")
df['date'] = pd.to_datetime(df['date'])

# Initialize the Dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.title = "Painel de Produção de Fórmulas"

# Layout
app.layout = html.Div(
    className="container",
    style={'font-family': 'Arial, sans-serif'},
    children=[
        html.H1("Painel de Produção de Fórmulas", style={"textAlign": "center", "color": "#0056b3"}),

        html.Div(
            className="row",
            style={"margin-top": "20px", "display": "flex", "justify-content": "center", "gap": "20px"},
            children=[
                html.Div(
                    style={"width": "300px"},
                    children=[
                        html.Label("Selecione o Período:", style={'font-weight': 'bold'}),
                        dcc.DatePickerRange(
                            id='date_range_picker',
                            start_date=df['date'].min().date(),
                            end_date=df['date'].max().date(),
                            display_format='DD/MM/YYYY'
                        )
                    ]
                ),
                html.Div(
                    style={"width": "300px"},
                    children=[
                        html.Label("Agrupar por:", style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='time_filter',
                            options=[
                                {"label": "Dia", "value": "D"},
                                {"label": "Semana", "value": "W"},
                                {"label": "Mês", "value": "M"},
                            ],
                            value="D",
                            clearable=False
                        )
                    ]
                ),
            ]
        ),
        
        html.Div(id='kpi_cards', className="row", style={"margin-top": "20px", "display": "flex", "justify-content": "space-around", "flex-wrap": "wrap"}),

        html.Div(
            className="row",
            style={"margin-top": "40px", "display": "flex", "flex-wrap": "wrap"},
            children=[
                html.Div(
                    className="col-12 col-md-6",
                    children=[
                        dcc.Graph(id='tipo_formula_pie')
                    ]
                ),
                html.Div(
                    className="col-12 col-md-6",
                    children=[
                        dcc.Graph(id='employee_counts')
                    ]
                )
            ]
        ),
        
        html.Div(
            className="row",
            style={"margin-top": "40px", "display": "flex", "flex-wrap": "wrap", "gap": "20px"},
            children=[
                html.Div(className="col-12 col-md-4", children=[dcc.Graph(id='weighing_employee_bar')]),
                html.Div(className="col-12 col-md-4", children=[dcc.Graph(id='handling_employee_bar')]),
                html.Div(className="col-12 col-md-4", children=[dcc.Graph(id='pm_employee_bar')])
            ]
        ),
        
        html.Div(
            className="row",
            style={"margin-top": "40px", "display": "flex", "flex-wrap": "wrap", "gap": "20px"},
            children=[
                html.Div(className="col-12 col-md-4", children=[dcc.Graph(id='stock_made_employee_bar')]),
                html.Div(className="col-12 col-md-4", children=[dcc.Graph(id='exc_reworked_weighing_bar')]),
                html.Div(className="col-12 col-md-4", children=[dcc.Graph(id='pm_reworked_handling_bar')])
            ]
        ),

        html.Div(
            className="row",
            style={"margin-top": "40px", "display": "flex", "flex-wrap": "wrap"},
            children=[
                html.Div(className="col-12 col-md-6", children=[dcc.Graph(id='formulas_over_time')]),
                html.Div(className="col-12 col-md-6", children=[dcc.Graph(id='stock_over_time')])
            ]
        ),
    ]
)

# Callback to update all components
@app.callback(
    [Output('kpi_cards', 'children'),
     Output('tipo_formula_pie', 'figure'),
     Output('employee_counts', 'figure'),
     Output('weighing_employee_bar', 'figure'),
     Output('handling_employee_bar', 'figure'),
     Output('pm_employee_bar', 'figure'),
     Output('stock_made_employee_bar', 'figure'),
     Output('exc_reworked_weighing_bar', 'figure'),
     Output('pm_reworked_handling_bar', 'figure'),
     Output('formulas_over_time', 'figure'),
     Output('stock_over_time', 'figure')],
    [Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date'),
     Input('time_filter', 'value')]
)
def update_dashboard(start_date, end_date, time_freq):
    # Filter dataframe based on date range
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Handle case with no data
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Nenhum dado encontrado para o período selecionado.")
        return (
            [html.Div("Nenhum dado encontrado para o período selecionado.", style={"textAlign": "center", "color": "red"})],
            empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
        )

    # --- KPIs for exceptions ---
    total_refeito_pm = filtered_df['refeito_pm'].sum()
    total_refeito_exc = filtered_df['refeito_exc'].sum()
    total_estoque_usado = filtered_df['estoque_usado'].sum()
    total_estoque_feito = filtered_df['estoque_feito'].sum()
    
    kpi_cards = [
        html.Div(className="kpi-card", style={"border": "1px solid #ddd", "padding": "20px", "border-radius": "5px", "text-align": "center", "background-color": "#f9f9f9", "min-width": "180px", "margin": "10px"},
                 children=[html.H3("Refeito PM", style={"color": "#dc3545", "font-size": "1.2em"}),
                           html.P(f"{total_refeito_pm}", style={"font-size": "2em", "font-weight": "bold", "color": "#dc3545"})]),
        html.Div(className="kpi-card", style={"border": "1px solid #ddd", "padding": "20px", "border-radius": "5px", "text-align": "center", "background-color": "#f9f9f9", "min-width": "180px", "margin": "10px"},
                 children=[html.H3("Refeito EXC", style={"color": "#ffc107", "font-size": "1.2em"}),
                           html.P(f"{total_refeito_exc}", style={"font-size": "2em", "font-weight": "bold", "color": "#ffc107"})]),
        html.Div(className="kpi-card", style={"border": "1px solid #ddd", "padding": "20px", "border-radius": "5px", "text-align": "center", "background-color": "#f9f9f9", "min-width": "180px", "margin": "10px"},
                 children=[html.H3("Estoque Usado", style={"color": "#28a745", "font-size": "1.2em"}),
                           html.P(f"{total_estoque_usado}", style={"font-size": "2em", "font-weight": "bold", "color": "#28a745"})]),
        html.Div(className="kpi-card", style={"border": "1px solid #ddd", "padding": "20px", "border-radius": "5px", "text-align": "center", "background-color": "#f9f9f9", "min-width": "180px", "margin": "10px"},
                 children=[html.H3("Estoque Feito", style={"color": "#17a2b8", "font-size": "1.2em"}),
                           html.P(f"{total_estoque_feito}", style={"font-size": "2em", "font-weight": "bold", "color": "#17a2b8"})])
    ]

    # --- Formula Type Pie Chart ---
    formula_counts = filtered_df['tipo_formula'].value_counts().reset_index()
    formula_counts.columns = ['tipo_formula', 'count']
    tipo_formula_pie = px.pie(
        formula_counts,
        values='count',
        names='tipo_formula',
        title='Distribuição de Fórmulas por Tipo',
        labels={'tipo_formula': 'Tipo de Fórmula', 'count': 'Contagem'},
        hole=.4
    )
    tipo_formula_pie.update_traces(textposition='inside', textinfo='percent+label')

    # --- Overall Employee Counts ---
    employee_melted = filtered_df.melt(
        id_vars=['date'],
        value_vars=['funcionario_pesagem', 'funcionario_manipulacao', 'funcionario_pm'],
        var_name='role',
        value_name='employee'
    )
    overall_employee_counts = employee_melted.groupby('employee').size().reset_index(name='count').sort_values('count', ascending=False)
    overall_employee_fig = px.bar(
        overall_employee_counts,
        x='employee',
        y='count',
        color='employee',
        title="Contagem Total de Fórmulas por Funcionário",
        labels={'employee': 'Funcionário', 'count': 'Contagem'},
        text_auto=True
    )

    # --- Individual Employee Role Bar Charts ---
    weighing_counts = filtered_df['funcionario_pesagem'].value_counts().reset_index()
    weighing_counts.columns = ['Funcionário', 'Contagem']
    weighing_fig = px.bar(weighing_counts, x='Funcionário', y='Contagem', title='Fórmulas Pesadas por Funcionário', text_auto=True)
    weighing_fig.update_layout(xaxis_title="Funcionário", yaxis_title="Contagem")

    handling_counts = filtered_df['funcionario_manipulacao'].value_counts().reset_index()
    handling_counts.columns = ['Funcionário', 'Contagem']
    handling_fig = px.bar(handling_counts, x='Funcionário', y='Contagem', title='Fórmulas Manipuladas por Funcionário', text_auto=True)
    handling_fig.update_layout(xaxis_title="Funcionário", yaxis_title="Contagem")

    pm_counts = filtered_df['funcionario_pm'].value_counts().reset_index()
    pm_counts.columns = ['Funcionário', 'Contagem']
    pm_fig = px.bar(pm_counts, x='Funcionário', y='Contagem', title='Fórmulas Verificadas (PM) por Funcionário', text_auto=True)
    pm_fig.update_layout(xaxis_title="Funcionário", yaxis_title="Contagem")
    
    # --- NEW GRAPHS ---
    
    # Estoque Feito por Funcionário
    stock_made_df = filtered_df[filtered_df['estoque_feito'] > 0]
    stock_made_counts = stock_made_df['funcionario_manipulacao'].value_counts().reset_index()
    stock_made_counts.columns = ['Funcionário', 'Contagem']
    stock_made_fig = px.bar(stock_made_counts, x='Funcionário', y='Contagem', title='Estoque Feito por Funcionário', text_auto=True)
    stock_made_fig.update_layout(xaxis_title="Funcionário", yaxis_title="Contagem")

    # Refeito EXC por Funcionário de Pesagem
    exc_reworked_df = filtered_df[filtered_df['refeito_exc'] > 0]
    exc_reworked_counts = exc_reworked_df['funcionario_pesagem'].value_counts().reset_index()
    exc_reworked_counts.columns = ['Funcionário', 'Contagem']
    exc_reworked_fig = px.bar(exc_reworked_counts, x='Funcionário', y='Contagem', title='Refeito EXC por Funcionário de Pesagem', text_auto=True)
    exc_reworked_fig.update_layout(xaxis_title="Funcionário", yaxis_title="Contagem")

    # Refeito PM por Funcionário de Manipulação
    pm_reworked_df = filtered_df[filtered_df['refeito_pm'] > 0]
    pm_reworked_counts = pm_reworked_df['funcionario_manipulacao'].value_counts().reset_index()
    pm_reworked_counts.columns = ['Funcionário', 'Contagem']
    pm_reworked_fig = px.bar(pm_reworked_counts, x='Funcionário', y='Contagem', title='Refeito PM por Funcionário de Manipulação', text_auto=True)
    pm_reworked_fig.update_layout(xaxis_title="Funcionário", yaxis_title="Contagem")

    # Formulas over Time
    formulas_over_time_df = filtered_df.groupby(pd.Grouper(key='date', freq=time_freq)).size().reset_index(name='count')
    formulas_over_time_fig = px.line(formulas_over_time_df, x='date', y='count', markers=True, title='Fórmulas Feitas ao Longo do Tempo')
    formulas_over_time_fig.update_layout(xaxis_title="Data", yaxis_title="Número de Fórmulas", hovermode="x unified")

    # Stock Made and Used over Time
    stock_over_time_df = filtered_df.groupby(pd.Grouper(key='date', freq=time_freq)).agg({
        'estoque_feito': 'sum',
        'estoque_usado': 'sum'
    }).reset_index()
    stock_over_time_fig = go.Figure()
    stock_over_time_fig.add_trace(go.Scatter(x=stock_over_time_df['date'], y=stock_over_time_df['estoque_feito'], mode='lines+markers', name='Estoque Feito'))
    stock_over_time_fig.add_trace(go.Scatter(x=stock_over_time_df['date'], y=stock_over_time_df['estoque_usado'], mode='lines+markers', name='Estoque Usado'))
    stock_over_time_fig.update_layout(title='Estoque Feito e Usado ao Longo do Tempo', xaxis_title='Data', yaxis_title='Contagem', hovermode="x unified")


    return (kpi_cards, tipo_formula_pie, overall_employee_fig, weighing_fig, handling_fig, pm_fig, 
            stock_made_fig, exc_reworked_fig, pm_reworked_fig, formulas_over_time_fig, stock_over_time_fig)

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')