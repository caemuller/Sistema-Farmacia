import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

# --- CONFIGURATION ---
DATA_FILE = "data_julia.json"
LOGO_FILE = "logo.png"

# --- HELPER: IMAGE ENCODING ---
def encode_image(image_file):
    """Encodes a local image file to base64 for Dash."""
    if os.path.exists(image_file):
        encoded = base64.b64encode(open(image_file, 'rb').read())
        return 'data:image/png;base64,{}'.format(encoded.decode())
    return None

# --- LOAD DATA ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['date', 'time', 'nr', 'tipos_erro', 'funcionario', 'valor', 'desconto', 'cobrado'])
    
    try:
        df = pd.read_json(DATA_FILE)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except ValueError:
        return pd.DataFrame(columns=['date', 'time', 'nr', 'tipos_erro', 'funcionario', 'valor', 'desconto', 'cobrado'])

# Initialize Data for Dropdowns
df_init = load_data()

# Handle empty data init for DatePicker
if not df_init.empty:
    min_date = df_init['date'].min().date()
    max_date = df_init['date'].max().date()
    unique_employees = sorted(df_init['funcionario'].unique().tolist())
else:
    min_date = pd.to_datetime('today').date()
    max_date = pd.to_datetime('today').date()
    unique_employees = []

# --- DASH APP ---
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.title = "Dashboard Financeiro de Erros"

# Get encoded logo
logo_src = encode_image(LOGO_FILE)

app.layout = html.Div(
    className="container",
    style={'font-family': 'Arial, sans-serif', 'backgroundColor': '#f4f6f9', 'padding': '20px', 'minHeight': '100vh'},
    children=[
        
        # --- LOGO & HEADER ---
        html.Div(style={'textAlign': 'center', 'marginBottom': '20px'}, children=[
            html.Img(src=logo_src, style={'height': '80px', 'marginBottom': '10px'}) if logo_src else None,
            html.H1("Dashboard de Custos de Erros", style={"color": "#333", "margin": "0"})
        ]),

        # --- Controls ---
        html.Div(
            className="row",
            style={"display": "flex", "justifyContent": "center", "gap": "20px", "marginBottom": "30px", "backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"},
            children=[
                html.Div(children=[
                    html.Label("Selecione o Período:", style={'fontWeight': 'bold', 'display': 'block'}),
                    dcc.DatePickerRange(
                        id='date_picker',
                        start_date=min_date,
                        end_date=max_date,
                        display_format='DD/MM/YYYY',
                        minimum_nights=0
                    )
                ]),
                html.Div(style={"width": "200px"}, children=[
                    html.Label("Agrupar Tempo por:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='time_agg',
                        options=[{"label": "Dia", "value": "D"}, {"label": "Semana", "value": "W"}, {"label": "Mês", "value": "M"}],
                        value="D",
                        clearable=False
                    )
                ]),
            ]
        ),

        # --- KPI Cards ---
        html.Div(id='kpi_cards', style={"display": "flex", "justifyContent": "space-around", "flexWrap": "wrap", "marginBottom": "30px"}),

        # --- Row 1: Cost over Time & Cost by Employee ---
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "30px"},
            children=[
                html.Div(style={'flex': '2', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}, children=[
                    dcc.Graph(id='cost_over_time_chart')
                ]),
                html.Div(style={'flex': '1', 'minWidth': '300px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}, children=[
                    dcc.Graph(id='cost_by_employee_chart')
                ])
            ]
        ),

        # --- Row 2: Interactive Individual Analysis ---
        html.Div(
            style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)', 'marginBottom': '30px'},
            children=[
                html.H3("Análise Individual: Detalhe de Erros por Funcionário", style={'color': '#333', 'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}),
                
                html.Div(style={'marginTop': '20px', 'marginBottom': '20px', 'width': '50%'}, children=[
                    html.Label("Selecione o Funcionário:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='employee_selector',
                        options=[{'label': emp, 'value': emp} for emp in unique_employees],
                        placeholder="Escolha um nome...",
                        value=unique_employees[0] if unique_employees else None
                    )
                ]),
                
                dcc.Graph(id='employee_detail_chart')
            ]
        )
    ]
)

@app.callback(
    [Output('kpi_cards', 'children'),
     Output('cost_over_time_chart', 'figure'),
     Output('cost_by_employee_chart', 'figure'),
     Output('employee_detail_chart', 'figure')], # New Output
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('time_agg', 'value'),
     Input('employee_selector', 'value')] # New Input
)
def update_dashboard(start_date, end_date, freq, selected_employee):
    # Reload data to get realtime updates
    df = load_data()
    
    empty_fig = go.Figure().update_layout(title="Sem dados")

    if df.empty:
        return [html.Div("Sem dados")], empty_fig, empty_fig, empty_fig

    # Filter by Date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask]

    if filtered_df.empty:
        return [html.Div("Sem dados neste período")], empty_fig, empty_fig, empty_fig

    # --- KPIs ---
    total_cost = filtered_df['valor'].sum()
    total_errors = len(filtered_df)
    avg_cost = filtered_df['valor'].mean()

    card_style = {
        "border": "1px solid #ddd", "padding": "20px", "borderRadius": "10px", 
        "textAlign": "center", "backgroundColor": "white", "minWidth": "200px",
        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)", "margin": "10px", "flex": "1"
    }

    kpi_html = [
        html.Div(style=card_style, children=[
            html.H3("Custo Total", style={"color": "#d9534f", "marginBottom": "5px"}),
            html.P(f"R$ {total_cost:,.2f}", style={"fontSize": "2em", "fontWeight": "bold", "color": "#333"})
        ]),
        html.Div(style=card_style, children=[
            html.H3("Quantidade de Erros", style={"color": "#f0ad4e", "marginBottom": "5px"}),
            html.P(f"{total_errors}", style={"fontSize": "2em", "fontWeight": "bold", "color": "#333"})
        ]),
        html.Div(style=card_style, children=[
            html.H3("Custo Médio", style={"color": "#5bc0de", "marginBottom": "5px"}),
            html.P(f"R$ {avg_cost:,.2f}", style={"fontSize": "2em", "fontWeight": "bold", "color": "#333"})
        ]),
    ]

    # --- 1. Cost Over Time ---
    cost_over_time = filtered_df.groupby(pd.Grouper(key='date', freq=freq))['valor'].sum().reset_index()
    fig_time = px.line(cost_over_time, x='date', y='valor', markers=True, title="Evolução do Prejuízo Financeiro")
    fig_time.update_layout(yaxis_title="Valor (R$)", xaxis_title="Data")
    fig_time.update_traces(line_color='#d9534f', line_width=3)

    # --- 2. Cost by Employee (Bar) ---
    cost_by_emp = filtered_df.groupby('funcionario')['valor'].sum().reset_index().sort_values('valor', ascending=True)
    fig_emp = px.bar(cost_by_emp, x='valor', y='funcionario', orientation='h', title="Prejuízo Total por Funcionário", text_auto='.2f')
    fig_emp.update_traces(marker_color='#337ab7', textfont_size=12, textposition="outside")
    fig_emp.update_layout(xaxis_title="Valor Total (R$)", yaxis_title=None)

    # --- 3. Individual Employee Detail (New Graph) ---
    if selected_employee:
        # Filter for the specific employee
        emp_df = filtered_df[filtered_df['funcionario'] == selected_employee].copy()
        
        if not emp_df.empty:
            # Important: Use explode because 'tipos_erro' is a list like ['A', 'B']
            # Explode creates a separate row for every error in the list
            emp_df_exploded = emp_df.explode('tipos_erro')
            
            # Count occurrences of each error type
            error_counts = emp_df_exploded['tipos_erro'].value_counts().reset_index()
            error_counts.columns = ['Tipo de Erro', 'Quantidade']
            
            fig_detail = px.bar(
                error_counts, 
                x='Tipo de Erro', 
                y='Quantidade', 
                title=f"Tipos de Erro Cometidos por: {selected_employee}",
                text_auto=True
            )
            fig_detail.update_traces(marker_color='#d9534f')
            fig_detail.update_layout(yaxis_title="Qtd Ocorrências")
        else:
            fig_detail = go.Figure().update_layout(title=f"Sem dados para {selected_employee} no período")
    else:
        fig_detail = go.Figure().update_layout(title="Selecione um funcionário")

    return kpi_html, fig_time, fig_emp, fig_detail

if __name__ == "__main__":
    print("Starting Financial Dashboard on Port 8052...")
    app.run(debug=True, host='127.0.0.1', port=8052)