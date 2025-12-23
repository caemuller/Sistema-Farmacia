import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import os

# --- LOAD DATA ---
DATA_FILE = "data_julia.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['date', 'time', 'nr', 'tipo_erro', 'funcionario', 'valor', 'desconto', 'cobrado'])
    
    try:
        df = pd.read_json(DATA_FILE)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except ValueError:
        return pd.DataFrame(columns=['date', 'time', 'nr', 'tipo_erro', 'funcionario', 'valor', 'desconto', 'cobrado'])

# Initialize Data
df = load_data()

# Handle empty data init
if not df.empty:
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
else:
    min_date = pd.to_datetime('today').date()
    max_date = pd.to_datetime('today').date()

# --- DASH APP ---
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.title = "Dashboard Financeiro de Erros"

app.layout = html.Div(
    className="container",
    style={'font-family': 'Arial, sans-serif', 'backgroundColor': '#f4f6f9', 'padding': '20px', 'minHeight': '100vh'},
    children=[
        html.H1("Dashboard de Custos de Erros", style={"textAlign": "center", "color": "#d9534f", "marginBottom": "30px"}),

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

        # --- Row 2: Breakdown by Type & Status ---
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "30px"},
            children=[
                html.Div(style={'flex': '1', 'minWidth': '300px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}, children=[
                    dcc.Graph(id='cost_by_type_chart')
                ]),
                html.Div(style={'flex': '1', 'minWidth': '300px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'}, children=[
                    dcc.Graph(id='status_pie_chart')
                ])
            ]
        )
    ]
)

@app.callback(
    [Output('kpi_cards', 'children'),
     Output('cost_over_time_chart', 'figure'),
     Output('cost_by_employee_chart', 'figure'),
     Output('cost_by_type_chart', 'figure'),
     Output('status_pie_chart', 'figure')],
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('time_agg', 'value')]
)
def update_dashboard(start_date, end_date, freq):
    # Reload data to get realtime updates
    df = load_data()
    
    if df.empty:
        empty_fig = go.Figure().update_layout(title="Sem dados")
        return [html.Div("Sem dados")], empty_fig, empty_fig, empty_fig, empty_fig

    # Filter by Date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask]

    if filtered_df.empty:
        empty_fig = go.Figure().update_layout(title="Sem dados neste período")
        return [html.Div("Sem dados")], empty_fig, empty_fig, empty_fig, empty_fig

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
    # Group by Frequency
    cost_over_time = filtered_df.groupby(pd.Grouper(key='date', freq=freq))['valor'].sum().reset_index()
    fig_time = px.line(cost_over_time, x='date', y='valor', markers=True, title="Evolução do Prejuízo Financeiro")
    fig_time.update_layout(yaxis_title="Valor (R$)", xaxis_title="Data")
    fig_time.update_traces(line_color='#d9534f', line_width=3)

    # --- 2. Cost by Employee (Bar) ---
    cost_by_emp = filtered_df.groupby('funcionario')['valor'].sum().reset_index().sort_values('valor', ascending=True)
    fig_emp = px.bar(cost_by_emp, x='valor', y='funcionario', orientation='h', title="Prejuízo por Funcionário", text_auto='.2f')
    fig_emp.update_traces(marker_color='#337ab7', textfont_size=12, textangle=0, textposition="outside")
    fig_emp.update_layout(xaxis_title="Valor Total (R$)", yaxis_title=None)

    # --- 3. Cost by Error Type (Bar) ---
    cost_by_type = filtered_df.groupby('tipo_erro')['valor'].sum().reset_index().sort_values('valor', ascending=False)
    fig_type = px.bar(cost_by_type, x='tipo_erro', y='valor', title="Custo por Tipo de Erro", text_auto='.2f')
    fig_type.update_traces(marker_color='#5cb85c')
    fig_type.update_layout(yaxis_title="Valor (R$)", xaxis_title=None)

    # --- 4. Status Pie Chart (Cobrado vs Desconto vs Pendente) ---
    # We create categories based on booleans
    def get_status(row):
        if row['cobrado']: return 'Cobrado'
        if row['desconto']: return 'Desconto'
        return 'Pendente/Prejuízo'
    
    status_df = filtered_df.copy()
    status_df['status'] = status_df.apply(get_status, axis=1)
    
    status_counts = status_df.groupby('status')['valor'].sum().reset_index()
    fig_status = px.pie(status_counts, values='valor', names='status', title='Distribuição do Custo (Status)', hole=0.4)
    fig_status.update_traces(textinfo='percent+label')

    return kpi_html, fig_time, fig_emp, fig_type, fig_status

if __name__ == "__main__":
    # Using a different port (8052) to avoid conflict with the other dashboard
    print("Starting Financial Dashboard on Port 8052...")
    app.run(debug=True, host='127.0.0.1', port=8052)