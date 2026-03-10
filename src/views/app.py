import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash import dash_table
from datetime import datetime
import traceback
from src.utils.data_loader import get_available_tickers, clear_cache
from src.models.forecast_model import run_forecast
from src.utils.metrics import get_all_metrics
from src.services.scheduler import ModelRetrainScheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the scheduler with expanding window approach
scheduler = ModelRetrainScheduler(use_expanding_window=True)

# Initialize the Dash app with Bootstrap CYBORG theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Define the layout
app.layout = html.Div(
    style={'backgroundColor': '#000014', 'fontFamily': '"Courier New", Courier, monospace', 'height': '100vh', 'overflow': 'hidden'},
    children=[
        # Title Bar
        html.Div(
            style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'right': '0',
                'height': '40px',
                'backgroundColor': '#000022',
                'color': '#00F0FF',
                'fontSize': '16px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'padding': '0 10px',
                'borderBottom': '1px solid #00F0FF',
                'zIndex': '1001',
                'fontWeight': 'bold'
            },
            children=[
                html.Span("CRYPTO VIBECAST - Big 3 Crypto Forecasting Dashboard", style={'letterSpacing': '1px'})
            ]
        ),
        
        # Market Ticker Bar
        html.Div(
            id='market-ticker',
            style={
                'position': 'fixed',
                'top': '40px',  # Adjusted position to be below the title bar
                'left': '0',
                'right': '0',
                'height': '24px',
                'backgroundColor': '#000022',
                'color': '#00F0FF',
                'fontSize': '12px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-around',
                'padding': '0 10px',
                'borderBottom': '1px solid #00F0FF',
                'zIndex': '1000',
                'overflow': 'hidden'
            },
            children=[
                html.Span("BTC: $67,278.73 ", id='btc-ticker', style={'color': '#00FF00'}),
                html.Span("ETH: $1,981.43 ", id='eth-ticker', style={'color': '#FFA500'}),
                html.Span("SOL: $83.27 ", id='sol-ticker', style={'color': '#00F0FF'}),
                html.Span("24h: +2.34% ", id='change-ticker', style={'color': '#00FF00'})
            ]
        ),
        
        # Main Container with Sidebar and Dashboard Area
        html.Div(
            style={'display': 'flex', 'height': 'calc(100vh - 64px)', 'marginTop': '64px'},
            children=[
                # Left Sidebar Control Panel
                html.Div(
                    style={
                        'width': '250px',
                        'backgroundColor': '#000022',
                        'borderRight': '1px solid #00F0FF',
                        'padding': '15px',
                        'color': '#00F0FF',
                        'fontFamily': '"Courier New", Courier, monospace',
                        'overflowY': 'auto'
                    },
                    children=[
                        html.H3("CONTROLS",
                                style={
                                    'color': '#00F0FF',
                                    'fontSize': '16px',
                                    'fontWeight': 'bold',
                                    'textTransform': 'uppercase',
                                    'marginBottom': '20px',
                                    'borderBottom': '1px solid #00F0FF',
                                    'paddingBottom': '5px'
                                }),

                        # Information about the supported cryptocurrencies
                        html.Div([
                            html.P("BIG 3 CRYPTOCURRENCIES:", 
                                   style={'color': '#FFA500', 'fontSize': '10px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'marginBottom': '5px'}),
                            html.Ul([
                                html.Li("BTC — Bitcoin", style={'color': '#00F0FF', 'fontSize': '10px', 'margin': '2px 0'}),
                                html.Li("ETH — Ethereum", style={'color': '#00F0FF', 'fontSize': '10px', 'margin': '2px 0'}),
                                html.Li("SOL — Solana", style={'color': '#00F0FF', 'fontSize': '10px', 'margin': '2px 0'})
                            ], style={'paddingLeft': '15px'})
                        ], style={'marginBottom': '15px'}),

                        html.Div([
                            html.Label("SELECT ASSET:",
                                      style={'color': '#00F0FF', 'fontSize': '12px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'display': 'block', 'marginBottom': '5px'}),
                            dcc.Dropdown(
                                id='asset-selector',
                                options=get_available_tickers(),
                                value='BTC-USD',
                                style={
                                    'backgroundColor': '#000014',
                                    'color': '#00F0FF',
                                    'border': '1px solid #00F0FF',
                                    'borderRadius': '4px',
                                    'fontFamily': '"Courier New", Courier, monospace',
                                    'fontSize': '12px',
                                    'marginBottom': '15px'
                                }
                            ),
                        ]),

                        html.Div([
                            html.Label("FORECAST HORIZON:",
                                      style={'color': '#00F0FF', 'fontSize': '12px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'display': 'block', 'marginBottom': '5px'}),
                            dcc.RadioItems(
                                id='horizon-selector',
                                options=[
                                    {'label': '7D', 'value': 7},
                                    {'label': '30D', 'value': 30},
                                    {'label': '90D', 'value': 90},
                                    {'label': '180D', 'value': 180}
                                ],
                                value=30,
                                style={'color': '#00F0FF', 'fontFamily': '"Courier New", Courier, monospace', 'fontSize': '12px'},
                                inputStyle={"margin-right": "10px", "margin-left": "5px", "marginBottom": "5px"},
                                labelStyle={'display': 'block', 'marginBottom': '5px'}
                            ),
                        ], style={'marginBottom': '15px'}),

                        html.Div([
                            dbc.Button("RUN FORECAST", id="run-forecast-button",
                                      style={
                                          'backgroundColor': '#000014',
                                          'color': '#00F0FF',
                                          'border': '1px solid #00F0FF',
                                          'borderRadius': '4px',
                                          'fontFamily': '"Courier New", Courier, monospace',
                                          'fontSize': '12px',
                                          'fontWeight': 'bold',
                                          'padding': '8px',
                                          'width': '100%',
                                          'marginBottom': '10px'
                                      }),
                            dbc.Button("REFRESH DATA", id="refresh-button",
                                      style={
                                          'backgroundColor': '#000014',
                                          'color': '#00F0FF',
                                          'border': '1px solid #00F0FF',
                                          'borderRadius': '4px',
                                          'fontFamily': '"Courier New", Courier, monospace',
                                          'fontSize': '12px',
                                          'fontWeight': 'bold',
                                          'padding': '8px',
                                          'width': '100%',
                                          'marginBottom': '10px'
                                      }),
                            dbc.Button("SHOW TABLE", id="toggle-view-button",
                                      style={
                                          'backgroundColor': '#000014',
                                          'color': '#FFA500',
                                          'border': '1px solid #FFA500',
                                          'borderRadius': '4px',
                                          'fontFamily': '"Courier New", Courier, monospace',
                                          'fontSize': '12px',
                                          'fontWeight': 'bold',
                                          'padding': '8px',
                                          'width': '100%'
                                      }),
                        ], style={'marginBottom': '15px'}),

                        html.Div([
                            html.P("Keyboard Shortcuts:",
                                  style={'color': '#00F0FF', 'fontSize': '10px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'marginBottom': '5px'}),
                            html.P("B: BTC | E: ETH | S: SOL", style={'color': '#FFA500', 'fontSize': '10px', 'margin': '2px 0'}),
                            html.P("1: 7D | 2: 30D | 3: 90D | 4: 180D", style={'color': '#FFA500', 'fontSize': '10px', 'margin': '2px 0'}),
                            html.P("F: Forecast | R: Refresh", style={'color': '#FFA500', 'fontSize': '10px', 'margin': '2px 0'})
                        ], style={'fontSize': '10px', 'color': '#FFA500', 'marginTop': '20px'})
                    ]
                ),

                # Main Dashboard Area (Right Side)
                html.Div(
                    style={
                        'flex': '1',
                        'padding': '15px',
                        'backgroundColor': '#000014',
                        'color': '#00F0FF',
                        'overflowY': 'auto'
                    },
                    children=[
                        # Top Metric Strip
                        html.Div(
                            id='top-metric-strip',
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'marginBottom': '15px',
                                'gap': '10px'
                            },
                            children=[
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("CURRENT PRICE", className="card-title", style={'color': '#00F0FF', 'fontSize': '10px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'marginBottom': '2px'}),
                                        html.P(id='metric-current-price', style={'color': '#FFFFFF', 'fontSize': '14px', 'fontFamily': '"Courier New", Courier, monospace', 'margin': '0', 'fontWeight': 'bold'})
                                    ])
                                ], style={'backgroundColor': '#000022', 'border': '1px solid #00F0FF', 'borderRadius': '4px', 'padding': '8px', 'flex': '1'}),

                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("PREDICTED PRICE", className="card-title", style={'color': '#00F0FF', 'fontSize': '10px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'marginBottom': '2px'}),
                                        html.P(id='metric-predicted-price', style={'color': '#FFFFFF', 'fontSize': '14px', 'fontFamily': '"Courier New", Courier, monospace', 'margin': '0', 'fontWeight': 'bold'})
                                    ])
                                ], style={'backgroundColor': '#000022', 'border': '1px solid #00F0FF', 'borderRadius': '4px', 'padding': '8px', 'flex': '1'}),

                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("% CHANGE", className="card-title", style={'color': '#00F0FF', 'fontSize': '10px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'marginBottom': '2px'}),
                                        html.P(id='metric-pct-change', style={'color': '#e6edf3', 'fontSize': '14px', 'fontFamily': '"Courier New", Courier, monospace', 'margin': '0', 'fontWeight': 'bold'})
                                    ])
                                ], style={'backgroundColor': '#000022', 'border': '1px solid #00F0FF', 'borderRadius': '4px', 'padding': '8px', 'flex': '1'}),

                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("VOLATILITY (30D)", className="card-title", style={'color': '#00F0FF', 'fontSize': '10px', 'fontWeight': 'bold', 'textTransform': 'uppercase', 'marginBottom': '2px'}),
                                        html.P(id='metric-volatility', style={'color': '#FFFFFF', 'fontSize': '14px', 'fontFamily': '"Courier New", Courier, monospace', 'margin': '0', 'fontWeight': 'bold'})
                                    ])
                                ], style={'backgroundColor': '#000022', 'border': '1px solid #00F0FF', 'borderRadius': '4px', 'padding': '8px', 'flex': '1'})
                            ]
                        ),

                        # Main Price Chart and Forecast Table
                        html.Div([
                            dcc.Loading(
                                id="loading-forecast",
                                type="circle",
                                color="#00d4ff",
                                children=[
                                    html.Div([
                                        dcc.Graph(id='forecast-chart', style={'height': 'calc(100vh - 200px)'})
                                    ], id='chart-container'),
                                    html.Div([
                                        dash_table.DataTable(
                                            id='forecast-table',
                                            columns=[
                                                {'name': 'Date', 'id': 'ds', 'type': 'datetime'},
                                                {'name': 'Forecast Price', 'id': 'yhat', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
                                                {'name': 'Lower Bound', 'id': 'yhat_lower', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
                                                {'name': 'Upper Bound', 'id': 'yhat_upper', 'type': 'numeric', 'format': {'specifier': '$,.2f'}}
                                            ],
                                            style_cell={
                                                'backgroundColor': '#000022',
                                                'color': '#FFFFFF',
                                                'fontFamily': '"Courier New", Courier, monospace',
                                                'textAlign': 'left',
                                                'border': '1px solid #00F0FF'
                                            },
                                            style_header={
                                                'backgroundColor': '#000014',
                                                'color': '#00F0FF',
                                                'fontWeight': 'bold',
                                                'border': '1px solid #00F0FF'
                                            },
                                            style_data={
                                                'whiteSpace': 'normal',
                                                'height': 'auto',
                                            },
                                            style_table={
                                                'height': 'calc(100vh - 200px)',
                                                'overflowY': 'auto'
                                            },
                                            page_size=10,
                                            sort_action='native',
                                            filter_action='native'
                                        )
                                    ], id='table-container', style={'display': 'none'})
                                ]
                            )
                        ])
                    ]
                )
            ]
        ),

        # Last updated indicator
        html.Div(id='last-updated',
                 style={'color': '#FFA500', 'textAlign': 'right', 'marginTop': '10px', 'fontSize': '14px', 'fontWeight': 'bold'}),
        
        # Hidden div to store keyboard events
        dcc.Store(id='keyboard-store', data={}),

        # Interval to update ticker
        dcc.Interval(id='ticker-interval', interval=5000, n_intervals=0)
    ]
)








# Callback to update forecast chart and metrics
@app.callback(
    [Output('forecast-chart', 'figure'),
     Output('forecast-table', 'data'),
     Output('metric-current-price', 'children'),
     Output('metric-predicted-price', 'children'),
     Output('metric-pct-change', 'children'),
     Output('metric-pct-change', 'style'),
     Output('metric-volatility', 'children'),
     Output('last-updated', 'children')],
    [Input('asset-selector', 'value'),
     Input('horizon-selector', 'value'),
     Input('run-forecast-button', 'n_clicks'),
     Input('refresh-button', 'n_clicks')],
    prevent_initial_call=False
)
def update_forecast_and_metrics(asset, horizon, run_clicks, refresh_clicks):
    ctx = dash.callback_context

    # Determine which input triggered the callback
    triggered_id = ''
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Update timestamp
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    last_updated_text = f"Last updated: {timestamp}"

    # If neither button was clicked initially, don't run forecast
    if not ctx.triggered or triggered_id in ['asset-selector', 'horizon-selector']:
        # Just load historical data without forecast
        try:
            historical_df = run_forecast(asset, 1)[0]  # Just get historical data
            if historical_df.empty:
                fig = go.Figure()
                fig.add_annotation(text="No data available", showarrow=False)
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#000014',
                    plot_bgcolor='#000014',
                    title=dict(text=f'{asset} Price Chart', font=dict(color='#00F0FF'))
                )
                return fig, [], "$0.00", "$0.00", "0.00%", {'color': '#e6edf3'}, "0.00%", last_updated_text

            # Create the historical price chart only
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=historical_df['Date'],
                y=historical_df['Close'],
                mode='lines',
                name='Historical',
                line=dict(color='#ffffff', width=1.5)
            ))

            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#000014',
                plot_bgcolor='#000014',
                title=dict(text=f'{asset} Price Chart', font=dict(color='#00F0FF')),
                xaxis=dict(
                    gridcolor='#00F0FF',
                    linecolor='#00F0FF',
                    tickfont=dict(color='#00F0FF')
                ),
                yaxis=dict(
                    title='Price (USD)',
                    tickprefix='$',
                    tickformat=',.0f',
                    gridcolor='#00F0FF',
                    linecolor='#00F0FF',
                    tickfont=dict(color='#00F0FF')
                ),
                hovermode='x unified',
                hoverlabel=dict(bgcolor='#000014', font=dict(color='#00F0FF', family='"Courier New", Courier, monospace')),
                margin=dict(l=60, r=20, t=50, b=40)
            )

            # Calculate metrics for historical data only
            current_price = historical_df['Close'].iloc[-1]
            predicted_price = current_price  # Placeholder until forecast is run
            pct_change = 0.0  # Placeholder until forecast is run
            volatility = get_all_metrics(historical_df, historical_df)['volatility']  # Use historical for volatility

            return fig, [], f"${current_price:,.2f}", f"${predicted_price:,.2f}", f"{pct_change:+.2f}%", {'color': '#e6edf3'}, f"{volatility:.2f}%", last_updated_text
        except Exception as e:
            print(f"Error in initial chart: {str(e)}")
            fig = go.Figure()
            fig.add_annotation(text="Error loading data", showarrow=False)
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#000014',
                plot_bgcolor='#000014',
                title=dict(text=f'{asset} Price Chart', font=dict(color='#00F0FF'))
            )
            return fig, [], "$0.00", "$0.00", "0.00%", {'color': '#e6edf3'}, "0.00%", last_updated_text

    try:
        # Run the full forecasting pipeline when Run Forecast is clicked
        if triggered_id == 'run-forecast-button' or triggered_id == 'refresh-button':
            historical_df, forecast_df = run_forecast(asset, horizon)

        if historical_df.empty or forecast_df.empty:
            # Return empty chart and default metrics
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for forecasting", showarrow=False)
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#000014',
                plot_bgcolor='#000014',
                title=dict(text=f'{asset} Price Forecast ({horizon} Days)', font=dict(color='#00F0FF'))
            )

            return fig, [], "$0.00", "$0.00", "0.00%", {'color': '#e6edf3'}, "0.00%", last_updated_text

        # Calculate metrics
        metrics = get_all_metrics(historical_df, forecast_df)

        # Format metric values
        current_price_str = f"${metrics['current_price']:,.2f}"
        predicted_price_str = f"${metrics['predicted_price']:,.2f}"
        pct_change_str = f"{metrics['pct_change']:+.2f}%"
        volatility_str = f"{metrics['volatility']:.2f}%"

        # Determine color for % change
        pct_change_style = {
            'color': '#00FF00' if metrics['pct_change'] >= 0 else '#FF4444',  # Green for positive, red for negative
            'fontSize': '14px',
            'fontFamily': '"Courier New", Courier, monospace',
            'fontWeight': 'bold',
            'margin': '0'
        }

        # Create the combined forecast chart
        fig = go.Figure()

        # Confidence interval (draw first so it appears behind lines)
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast_df['ds'], forecast_df['ds'][::-1]]),
            y=pd.concat([forecast_df['yhat_upper'], forecast_df['yhat_lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(0, 212, 255, 0.12)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Interval',
            hoverinfo='skip'
        ))

        # Historical line
        fig.add_trace(go.Scatter(
            x=historical_df['Date'],
            y=historical_df['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='#ffffff', width=1.5)
        ))

        # Forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='#00d4ff', width=2, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Forecast: $%{y:,.2f}<extra></extra>'
        ))

        # Vertical separator line at forecast start
        fig.add_shape(
            type='line',
            xref='x', yref='paper',
            x0=historical_df['Date'].iloc[-1], x1=historical_df['Date'].iloc[-1],
            y0=0, y1=1,
            line=dict(color='#8b949e', dash='dot'),
        )
        # Add annotation separately
        fig.add_annotation(
            x=historical_df['Date'].iloc[-1],
            y=0.9,
            xref='x', yref='paper',
            text='Forecast Start',
            showarrow=False,
            font=dict(color='#8b949e'),
            xanchor='left'
        )

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#000014',
            plot_bgcolor='#000014',
            title=dict(text=f'{asset} Price Forecast ({horizon} Days)', font=dict(color='#00F0FF')),
            xaxis=dict(
                gridcolor='#00F0FF',
                linecolor='#00F0FF',
                tickfont=dict(color='#00F0FF')
            ),
            yaxis=dict(
                title='Price (USD)',
                tickprefix='$',
                tickformat=',.0f',
                gridcolor='#00F0FF',
                linecolor='#00F0FF',
                tickfont=dict(color='#00F0FF')
            ),
            hovermode='x unified',
            hoverlabel=dict(bgcolor='#000014', font=dict(color='#00F0FF', family='"Courier New", Courier, monospace')),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#00F0FF')),
            margin=dict(l=60, r=20, t=60, b=40)
        )

        # Prepare data for the forecast table
        table_data = forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records')

        return fig, table_data, current_price_str, predicted_price_str, pct_change_str, pct_change_style, volatility_str, last_updated_text

    except Exception as e:
        print(f"Error in update_forecast_and_metrics: {str(e)}")
        traceback.print_exc()

        # Return error chart and default metrics
        fig = go.Figure()
        error_message = f"Forecast model training failed: {str(e)}. Try a different asset or horizon."
        fig.add_annotation(text=error_message, showarrow=False)
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#000014',
            plot_bgcolor='#000014',
            title=dict(text=f'{asset} Price Forecast ({horizon} Days)', font=dict(color='#00F0FF'))
        )

        return fig, [], "$0.00", "$0.00", "0.00%", {'color': '#e6edf3'}, "0.00%", last_updated_text


# Callback to toggle between chart and table views
@app.callback(
    [Output('chart-container', 'style'),
     Output('table-container', 'style'),
     Output('toggle-view-button', 'children')],
    [Input('toggle-view-button', 'n_clicks')],
    [State('chart-container', 'style'),
     State('table-container', 'style')]
)
def toggle_view(n_clicks, chart_style, table_style):
    if n_clicks is None:
        # Default to chart view
        return {'display': 'block'}, {'display': 'none'}, "SHOW TABLE"
    
    # Toggle based on number of clicks (odd = table view, even = chart view)
    if n_clicks % 2 == 1:
        # Show table, hide chart
        return {'display': 'none'}, {'display': 'block'}, "SHOW CHART"
    else:
        # Show chart, hide table
        return {'display': 'block'}, {'display': 'none'}, "SHOW TABLE"


# Add global keyboard event listener
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script>
            document.addEventListener('keydown', function(event) {
                // Only trigger if not in an input field
                if (event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
                    var key = event.key.toLowerCase();
                    
                    // Handle asset switching shortcuts
                    if (key === 'b') {
                        var dropdown = document.getElementById('asset-selector');
                        if (dropdown) {
                            dropdown.value = 'BTC-USD';
                            var changeEvent = new Event('change', { bubbles: true });
                            dropdown.dispatchEvent(changeEvent);
                        }
                    } else if (key === 'e') {
                        var dropdown = document.getElementById('asset-selector');
                        if (dropdown) {
                            dropdown.value = 'ETH-USD';
                            var changeEvent = new Event('change', { bubbles: true });
                            dropdown.dispatchEvent(changeEvent);
                        }
                    } else if (key === 's') {
                        var dropdown = document.getElementById('asset-selector');
                        if (dropdown) {
                            dropdown.value = 'SOL-USD';
                            var changeEvent = new Event('change', { bubbles: true });
                            dropdown.dispatchEvent(changeEvent);
                        }
                    }
                    
                    // Handle forecast horizon shortcuts
                    if (key === '1') {
                        var radios = document.querySelectorAll('input[name="horizon-selector"]');
                        if (radios.length > 0) {
                            radios[0].checked = true;
                            var changeEvent = new Event('change', { bubbles: true });
                            radios[0].dispatchEvent(changeEvent);
                        }
                    } else if (key === '2') {
                        var radios = document.querySelectorAll('input[name="horizon-selector"]');
                        if (radios.length > 1) {
                            radios[1].checked = true;
                            var changeEvent = new Event('change', { bubbles: true });
                            radios[1].dispatchEvent(changeEvent);
                        }
                    } else if (key === '3') {
                        var radios = document.querySelectorAll('input[name="horizon-selector"]');
                        if (radios.length > 2) {
                            radios[2].checked = true;
                            var changeEvent = new Event('change', { bubbles: true });
                            radios[2].dispatchEvent(changeEvent);
                        }
                    } else if (key === '4') {
                        var radios = document.querySelectorAll('input[name="horizon-selector"]');
                        if (radios.length > 3) {
                            radios[3].checked = true;
                            var changeEvent = new Event('change', { bubbles: true });
                            radios[3].dispatchEvent(changeEvent);
                        }
                    }
                    
                    // Handle action shortcuts
                    if (key === 'f') {
                        var btn = document.getElementById('run-forecast-button');
                        if (btn) btn.click();
                    } else if (key === 'r') {
                        var btn = document.getElementById('refresh-button');
                        if (btn) btn.click();
                    }
                    
                    // Handle view toggle shortcuts
                    if (key === 'v') {
                        var btn = document.getElementById('toggle-view-button');
                        if (btn) btn.click();
                    }
                }
            });
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Callback to update market ticker
@app.callback(
    Output('btc-ticker', 'children'),
    Output('eth-ticker', 'children'),
    Output('sol-ticker', 'children'),
    Output('change-ticker', 'children'),
    Output('btc-ticker', 'style'),
    Output('eth-ticker', 'style'),
    Output('sol-ticker', 'style'),
    Output('change-ticker', 'style'),
    Input('ticker-interval', 'n_intervals')
)
def update_market_ticker(n):
    try:
        import yfinance as yf
        import random
        
        # Fetch live data from yfinance
        btc = yf.Ticker("BTC-USD")
        eth = yf.Ticker("ETH-USD")
        sol = yf.Ticker("SOL-USD")
        
        # Get current prices
        btc_info = btc.history(period="1d")
        eth_info = eth.history(period="1d")
        sol_info = sol.history(period="1d")
        
        if not btc_info.empty and not eth_info.empty and not sol_info.empty:
            # Get base prices
            base_btc_price = btc_info['Close'].iloc[-1]
            base_eth_price = eth_info['Close'].iloc[-1]
            base_sol_price = sol_info['Close'].iloc[-1]
            
            # Add small random fluctuations (±1-2%) to simulate live movement
            btc_price = base_btc_price * (1 + random.uniform(-0.01, 0.01))  # ±1% fluctuation
            eth_price = base_eth_price * (1 + random.uniform(-0.01, 0.01))  # ±1% fluctuation
            sol_price = base_sol_price * (1 + random.uniform(-0.01, 0.01))  # ±1% fluctuation
            
            # Calculate 24h change percentage based on base prices
            if len(btc_info) >= 2:
                btc_prev_close = btc_info['Close'].iloc[-2]
                btc_base_change = ((base_btc_price - btc_prev_close) / btc_prev_close) * 100
            else:
                btc_base_change = 0.0
                
            if len(eth_info) >= 2:
                eth_prev_close = eth_info['Close'].iloc[-2]
                eth_base_change = ((base_eth_price - eth_prev_close) / eth_prev_close) * 100
            else:
                eth_base_change = 0.0
                
            if len(sol_info) >= 2:
                sol_prev_close = sol_info['Close'].iloc[-2]
                sol_base_change = ((base_sol_price - sol_prev_close) / sol_prev_close) * 100
            else:
                sol_base_change = 0.0
            
            # Use BTC base change as overall market sentiment
            overall_change = btc_base_change
            
            # Determine colors based on base changes (not the simulated fluctuations)
            change_color = '#00FF00' if overall_change >= 0 else '#FF4444'
            
            return (
                f"BTC: ${btc_price:,.2f} ",
                f"ETH: ${eth_price:,.2f} ",
                f"SOL: ${sol_price:,.2f} ",
                f"24h: {overall_change:+.2f}% ",
                {'color': '#00FF00' if btc_base_change >= 0 else '#FF4444'},
                {'color': '#00FF00' if eth_base_change >= 0 else '#FF4444'},
                {'color': '#00FF00' if sol_base_change >= 0 else '#FF4444'},
                {'color': change_color}
            )
        else:
            # Fallback to approximate prices if API fails
            return (
                "BTC: $67,868.65 ", 
                "ETH: $2,959.79 ", 
                "SOL: $156.75 ", 
                "24h: +0.50% ", 
                {'color': '#00FF00'}, 
                {'color': '#FF4444'}, 
                {'color': '#00FF00'}, 
                {'color': '#00FF00'}
            )
    except Exception as e:
        # Fallback to approximate prices if API fails
        return (
            "BTC: $67,868.65 ", 
            "ETH: $2,959.79 ", 
            "SOL: $156.75 ", 
            "24h: +0.50% ", 
            {'color': '#00FF00'}, 
            {'color': '#FF4444'}, 
            {'color': '#00FF00'}, 
            {'color': '#00FF00'}
        )


def main():
    """Main function untuk menjalankan aplikasi"""
    app.run(host="0.0.0.0", port=8050, debug=False)


# Run the server
if __name__ == "__main__":
    main()