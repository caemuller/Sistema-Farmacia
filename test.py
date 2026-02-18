import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

print("--- STARTING APP ---")

# --- LOAD DATA SECTION ---
try:
    print("Attempting to load formulas.json...")
    df = pd.read_json("formulas.json")
    
    # Check if data loaded
    print(f"Data loaded successfully! Found {len(df)} rows.")

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # 1. Handle "horario" vs "time" (Still needed for timeline charts or fallback)
    if 'horario' in df.columns:
        print("Using 'horario' column for time logic.")
        def get_hour(t):
            try:
                return int(str(t).split(':')[0])
            except:
                return 0
        df['hour_int'] = df['horario'].apply(get_hour)
    
    elif 'time' in df.columns:
        print("Using 'time' column for time logic.")
        def get_hour(t):
            try:
                return int(str(t).split(':')[0])
            except:
                return 0
        df['hour_int'] = df['time'].apply(get_hour)
        
    else:
        print("Warning: No time column found. Defaulting to 0.")
        df['hour_int'] = 0

except ValueError as e:
    print(f"Error reading JSON: {e}")
    print("Creating DUMMY data instead.")
    # Dummy data fallback with specific categories for testing
    data = {
        'date': pd.date_range(start='2025-05-20', periods=10, freq='D'),
        'horario': ['09:00', '13:00', '10:00', '14:00', '11:00', '09:30', '15:00', '08:00', '16:00', '10:00'],
        # NEW: Adding turno to dummy data to test the logic
        'turno': ['manha', 'tarde', 'manha', 'tarde', 'manha', 'manha', 'tarde', 'manha', 'tarde', 'manha'],
        'nr': range(1, 11),
        'funcionario_pesagem': ['Ana', 'Bob', 'Ana', 'Bob', 'Ana', 'Bob', 'Ana', 'Bob', 'Ana', 'Bob'],
        'funcionario_manipulacao': ['Bob', 'Ana', 'Bob', 'Ana', 'Bob', 'Ana', 'Bob', 'Ana', 'Bob', 'Ana'],
        'funcionario_pm': ['Carlos'] * 10,
        'tipo_formula': ['Cápsulas', 'Semi-sólidos', 'Sub-lingual/oleosas', 'Líquidos orais', 'Cápsulas', 
                         'Semi-sólidos', 'Sub-lingual/oleosas', 'Líquidos orais', 'Cápsulas', 'Semi-sólidos'],
        'refeito_pm': [False] * 10,
        'refeito_exc': [False] * 10,
        'estoque_usado': [1] * 10,
        'estoque_feito': [0] * 10,
        'pm_mais_20': [False] * 10
    }
    df = pd.DataFrame(data)
    df['hour_int'] = df['horario'].apply(lambda x: int(x.split(':')[0]))

# --- DASH APP ---
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.title = "Painel de Produção de Fórmulas"

# Calculate Min/Max dates safely for the layout
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# Layout
app.layout = html.Div(
    className="container",
    style={'font-family': 'Arial, sans-serif', 'backgroundColor': '#f4f6f9', 'padding': '20px'},
    children=[
        html.H1("Painel de Produção de Fórmulas", style={"textAlign": "center", "color": "#0056b3", "marginBottom": "30px"}),

        # --- Controls Row ---
        html.Div(
            className="row",
            style={"display": "flex", "justifyContent": "center", "gap": "20px", "marginBottom": "30px", "backgroundColor": "white", "padding": "20px", "borderRadius": "10px", "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"},
            children=[
                html.Div(
                    children=[
                        html.Label("Selecione o Período:", style={'fontWeight': 'bold', 'display': 'block'}),
                        dcc.DatePickerRange(
                            id='date_range_picker',
                            start_date=min_date,
                            end_date=max_date,
                            display_format='DD/MM/YYYY',
                            minimum_nights=0,
                        )
                    ]
                ),
                html.Div(
                    style={"width": "200px"},
                    children=[
                        html.Label("Agrupar por:", style={'fontWeight': 'bold'}),
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
        
        # --- KPI Cards Section ---
        html.Div(id='kpi_cards', style={"marginBottom": "30px"}),

        # --- Main Comparison Row ---
        html.Div(
            className="row",
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "30px"},
            children=[
                html.Div(
                    className="col-12 col-md-8",
                    style={'flex': '2', 'minWidth': '400px'},
                    children=[
                        html.Div(
                            style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'},
                            children=[dcc.Graph(id='production_employee_counts')]
                        )
                    ]
                ),
                html.Div(
                    className="col-12 col-md-4",
                    style={'flex': '1', 'minWidth': '300px'},
                    children=[
                        html.Div(
                            style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'},
                            children=[dcc.Graph(id='pm_distinct_bar')]
                        )
                    ]
                )
            ]
        ),

        html.Div(
            className="row",
            style={"display": "flex", "flexWrap": "wrap", "marginBottom": "30px"},
            children=[
                html.Div(
                    className="col-12",
                    style={'width': '100%', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'},
                    children=[dcc.Graph(id='tipo_formula_pie')]
                ),
            ]
        ),
        
        # --- Detailed Metrics Row 1 ---
        html.Div(
            className="row",
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "30px"},
            children=[
                html.Div(className="col-12 col-md-4", style={'flex': '1'}, children=[
                    html.Div(style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px'}, children=[dcc.Graph(id='weighing_employee_bar')])
                ]),
                html.Div(className="col-12 col-md-4", style={'flex': '1'}, children=[
                    html.Div(style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px'}, children=[dcc.Graph(id='handling_employee_bar')])
                ]),
                html.Div(className="col-12 col-md-4", style={'flex': '1'}, children=[
                    html.Div(style={'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px'}, children=[dcc.Graph(id='pm_employee_bar')])
                ]),
            ]
        ),
        
        # --- Detailed Metrics Row 2 ---
        html.Div(
            className="row",
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "30px"},
            children=[
                html.Div(className="col-12 col-md-4", style={'flex': '1'}, children=[dcc.Graph(id='stock_made_employee_bar')]),
                html.Div(className="col-12 col-md-4", style={'flex': '1'}, children=[dcc.Graph(id='exc_reworked_weighing_bar')]),
                html.Div(className="col-12 col-md-4", style={'flex': '1'}, children=[dcc.Graph(id='pm_reworked_handling_bar')])
            ]
        ),

        # --- Timeline Row ---
        html.Div(
            className="row",
            style={"display": "flex", "flexWrap": "wrap", "marginBottom": "30px"},
            children=[
                html.Div(className="col-12 col-md-6", style={'width': '50%'}, children=[dcc.Graph(id='formulas_over_time')]),
                html.Div(className="col-12 col-md-6", style={'width': '50%'}, children=[dcc.Graph(id='stock_over_time')])
            ]
        ),
        
        # --- Bottom Row ---
        html.Div(
            className="row",
            style={"display": "flex", "flexWrap": "wrap"},
            children=[
                html.Div(className="col-12 col-md-6", children=[dcc.Graph(id='pm_mais_20_handling_bar')]),
            ]
        ),
    ]
)

# Callback
@app.callback(
    [Output('kpi_cards', 'children'),
     Output('tipo_formula_pie', 'figure'),
     Output('production_employee_counts', 'figure'),
     Output('pm_distinct_bar', 'figure'),
     Output('weighing_employee_bar', 'figure'),
     Output('handling_employee_bar', 'figure'),
     Output('pm_employee_bar', 'figure'),
     Output('stock_made_employee_bar', 'figure'),
     Output('exc_reworked_weighing_bar', 'figure'),
     Output('pm_reworked_handling_bar', 'figure'),
     Output('formulas_over_time', 'figure'),
     Output('stock_over_time', 'figure'),
     Output('pm_mais_20_handling_bar', 'figure')],
    [Input('date_range_picker', 'start_date'),
     Input('date_range_picker', 'end_date'),
     Input('time_filter', 'value')]
)
def update_dashboard(start_date, end_date, time_freq):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Nenhum dado encontrado.")
        return (
            [html.Div("Nenhum dado encontrado.", style={"textAlign": "center", "color": "red"})],
            empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
        )

    # ==========================
    # KPI LOGIC (MODIFIED FOR TURNO)
    # ==========================
    
    # 1. General Totals
    total_formulas = len(filtered_df)

    # 2. Category Definitions
    solids_types = ['Cápsulas', 'Sub-lingual/oleosas', 'Capsula',"Sub-Lingual/Cápsulas Oleosas", "Sachês"] 
    semi_solids_types = ['Semi-Sólidos',"Líquidos Orais", 'Líquidos orais', 'Semi-solidos', 'Liquidos orais', 'Creme', 'Xarope']

    # 3. Filter Dataframes
    df_solids = filtered_df[filtered_df['tipo_formula'].isin(solids_types)]
    df_semi = filtered_df[filtered_df['tipo_formula'].isin(semi_solids_types)]

    solids_total = len(df_solids)
    semi_total = len(df_semi)

    # ---------------------------------------------------------
    # CONDITIONAL LOGIC: TURNO vs TIMESTAMP
    # ---------------------------------------------------------
    if 'turno' in filtered_df.columns:
        # Use explicit flags if the column exists
        formulas_morning = len(filtered_df[filtered_df['turno'] == 'manha'])
        formulas_afternoon = len(filtered_df[filtered_df['turno'] == 'tarde'])
        
        solids_am = len(df_solids[df_solids['turno'] == 'manha'])
        solids_pm = len(df_solids[df_solids['turno'] == 'tarde'])
        
        semi_am = len(df_semi[df_semi['turno'] == 'manha'])
        semi_pm = len(df_semi[df_semi['turno'] == 'tarde'])
    else:
        # Fallback to Old Logic (Time < 12)
        formulas_morning = len(filtered_df[filtered_df['hour_int'] < 12])
        formulas_afternoon = len(filtered_df[filtered_df['hour_int'] >= 12])
        
        solids_am = len(df_solids[df_solids['hour_int'] < 12])
        solids_pm = len(df_solids[df_solids['hour_int'] >= 12])
        
        semi_am = len(df_semi[df_semi['hour_int'] < 12])
        semi_pm = len(df_semi[df_semi['hour_int'] >= 12])
    # ---------------------------------------------------------

    # 6. Styling
    big_card_style = {
        "border": "1px solid #ddd", "padding": "20px", "borderRadius": "10px", 
        "textAlign": "center", "backgroundColor": "white", "minWidth": "200px",
        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)", "margin": "10px", "flex": "1"
    }
    
    small_card_style = {
        "border": "1px solid #eee", "padding": "10px", "borderRadius": "8px", 
        "textAlign": "center", "backgroundColor": "#fcfcfc", "minWidth": "100px",
        "margin": "5px", "flex": "1"
    }

    # 7. Construct HTML Structure
    kpi_layout = html.Div(children=[
        # Row 1: General Big Cards
        html.Div(style={"display": "flex", "justifyContent": "space-around", "flexWrap": "wrap", "marginBottom": "15px"}, children=[
            html.Div(style=big_card_style, children=[
                html.H3("Total Fórmulas", style={"color": "#0056b3", "fontSize": "1.1em", "marginBottom": "5px"}),
                html.P(f"{total_formulas}", style={"fontSize": "2.5em", "fontWeight": "bold", "color": "#0056b3", "margin": "0"})
            ]),
            html.Div(style=big_card_style, children=[
                html.H3("Geral Manhã", style={"color": "#28a745", "fontSize": "1.1em", "marginBottom": "5px"}),
                html.P(f"{formulas_morning}", style={"fontSize": "2.5em", "fontWeight": "bold", "color": "#28a745", "margin": "0"})
            ]),
            html.Div(style=big_card_style, children=[
                html.H3("Geral Tarde", style={"color": "#ffc107", "fontSize": "1.1em", "marginBottom": "5px"}),
                html.P(f"{formulas_afternoon}", style={"fontSize": "2.5em", "fontWeight": "bold", "color": "#e0a800", "margin": "0"})
            ])
        ]),

        # Row 2: Category Breakdown
        html.Div(style={"display": "flex", "flexWrap": "wrap", "gap": "20px"}, children=[
            
            # Solids Group
            html.Div(style={"flex": "1", "backgroundColor": "white", "padding": "10px", "borderRadius": "10px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"}, children=[
                html.H4("Sólidos (Cápsulas) + SL + Sachês", style={"textAlign": "center", "color": "#333", "marginBottom": "10px"}),
                html.Div(style={"display": "flex", "justifyContent": "space-between"}, children=[
                    html.Div(style=small_card_style, children=[html.Span("Total", style={"fontSize":"0.8em"}), html.Br(), html.Strong(f"{solids_total}", style={"fontSize": "1.5em", "color":"#0056b3"})]),
                    html.Div(style=small_card_style, children=[html.Span("Manhã", style={"fontSize":"0.8em"}), html.Br(), html.Strong(f"{solids_am}", style={"fontSize": "1.5em", "color":"#28a745"})]),
                    html.Div(style=small_card_style, children=[html.Span("Tarde", style={"fontSize":"0.8em"}), html.Br(), html.Strong(f"{solids_pm}", style={"fontSize": "1.5em", "color":"#e0a800"})]),
                ])
            ]),

            # Semi-Solids Group
            html.Div(style={"flex": "1", "backgroundColor": "white", "padding": "10px", "borderRadius": "10px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"}, children=[
                html.H4("Semi-Sólidos + Líquidos", style={"textAlign": "center", "color": "#333", "marginBottom": "10px"}),
                html.Div(style={"display": "flex", "justifyContent": "space-between"}, children=[
                    html.Div(style=small_card_style, children=[html.Span("Total", style={"fontSize":"0.8em"}), html.Br(), html.Strong(f"{semi_total}", style={"fontSize": "1.5em", "color":"#17a2b8"})]),
                    html.Div(style=small_card_style, children=[html.Span("Manhã", style={"fontSize":"0.8em"}), html.Br(), html.Strong(f"{semi_am}", style={"fontSize": "1.5em", "color":"#28a745"})]),
                    html.Div(style=small_card_style, children=[html.Span("Tarde", style={"fontSize":"0.8em"}), html.Br(), html.Strong(f"{semi_pm}", style={"fontSize": "1.5em", "color":"#e0a800"})]),
                ])
            ])
        ])
    ])

    # --- Charts Generation ---
    formula_counts = filtered_df['tipo_formula'].value_counts().reset_index()
    formula_counts.columns = ['tipo_formula', 'count']
    tipo_formula_pie = px.pie(formula_counts, values='count', names='tipo_formula', title='Distribuição por Tipo', hole=.4)
    tipo_formula_pie.update_traces(textposition='inside', textinfo='percent+label')

    prod_melted = filtered_df.melt(id_vars=['date'], value_vars=['funcionario_pesagem', 'funcionario_manipulacao'], var_name='role', value_name='employee')
    production_counts = prod_melted.groupby('employee').size().reset_index(name='count').sort_values('count', ascending=False)
    production_fig = px.bar(production_counts, x='employee', y='count', color='employee', title="Produção (Pesagem + Manipulação)", text_auto=True)
    production_fig.update_layout(showlegend=False)

    pm_counts_distinct = filtered_df['funcionario_pm'].value_counts().reset_index()
    pm_counts_distinct.columns = ['Funcionário', 'Contagem']
    pm_distinct_fig = px.bar(pm_counts_distinct, x='Funcionário', y='Contagem', title='Verificadas (PM)', text_auto=True, color_discrete_sequence=['#6f42c1'])

    weighing_counts = filtered_df['funcionario_pesagem'].value_counts().reset_index()
    weighing_counts.columns = ['Funcionário', 'Contagem']
    weighing_fig = px.bar(weighing_counts, x='Funcionário', y='Contagem', title='Pesagem', text_auto=True)

    handling_counts = filtered_df['funcionario_manipulacao'].value_counts().reset_index()
    handling_counts.columns = ['Funcionário', 'Contagem']
    handling_fig = px.bar(handling_counts, x='Funcionário', y='Contagem', title='Manipulação', text_auto=True)

    pm_counts = filtered_df['funcionario_pm'].value_counts().reset_index()
    pm_counts.columns = ['Funcionário', 'Contagem']
    pm_fig = px.bar(pm_counts, x='Funcionário', y='Contagem', title='Verificadas (PM) Detalhe', text_auto=True)
    
    stock_made_df = filtered_df[filtered_df['estoque_feito'] == True]
    stock_made_counts = stock_made_df['funcionario_manipulacao'].value_counts().reset_index()
    stock_made_counts.columns = ['Funcionário', 'Contagem']
    stock_made_fig = px.bar(stock_made_counts, x='Funcionário', y='Contagem', title='Estoque Feito', text_auto=True)

    exc_reworked_df = filtered_df[filtered_df['refeito_exc'] == True]
    exc_reworked_counts = exc_reworked_df['funcionario_pesagem'].value_counts().reset_index()
    exc_reworked_counts.columns = ['Funcionário', 'Contagem']
    exc_reworked_fig = px.bar(exc_reworked_counts, x='Funcionário', y='Contagem', title='Refeito EXC', text_auto=True)

    pm_reworked_df = filtered_df[filtered_df['refeito_pm'] == True]
    pm_reworked_counts = pm_reworked_df['funcionario_manipulacao'].value_counts().reset_index()
    pm_reworked_counts.columns = ['Funcionário', 'Contagem']
    pm_reworked_fig = px.bar(pm_reworked_counts, x='Funcionário', y='Contagem', title='Refeito PM', text_auto=True)

    formulas_over_time_df = filtered_df.groupby(pd.Grouper(key='date', freq=time_freq)).size().reset_index(name='count')
    formulas_over_time_fig = px.line(formulas_over_time_df, x='date', y='count', markers=True, title='Histórico de Produção')

    stock_over_time_df = filtered_df.groupby(pd.Grouper(key='date', freq=time_freq)).agg({
        'estoque_feito': 'sum',
        'estoque_usado': 'sum'
    }).reset_index()
    stock_over_time_fig = go.Figure()
    stock_over_time_fig.add_trace(go.Scatter(x=stock_over_time_df['date'], y=stock_over_time_df['estoque_feito'], mode='lines+markers', name='Estoque Feito'))
    stock_over_time_fig.add_trace(go.Scatter(x=stock_over_time_df['date'], y=stock_over_time_df['estoque_usado'], mode='lines+markers', name='Estoque Usado'))
    stock_over_time_fig.update_layout(title='Estoque (Linha do Tempo)', hovermode="x unified")

    pm_mais_20_df = filtered_df[filtered_df['pm_mais_20'] == True]
    pm_mais_20_counts = pm_mais_20_df['funcionario_manipulacao'].value_counts().reset_index()
    pm_mais_20_counts.columns = ['Funcionário', 'Contagem']
    pm_mais_20_fig = px.bar(pm_mais_20_counts, x='Funcionário', y='Contagem', title='PM +20', text_auto=True)

    return (kpi_layout, tipo_formula_pie, production_fig, pm_distinct_fig, weighing_fig, handling_fig, pm_fig, 
            stock_made_fig, exc_reworked_fig, pm_reworked_fig, formulas_over_time_fig, stock_over_time_fig,
            pm_mais_20_fig)

if __name__ == "__main__":
    print("Starting Server on Port 8050...")
    app.run(debug=True, host='127.0.0.1', port=8050)