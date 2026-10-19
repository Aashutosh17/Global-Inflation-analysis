"""
Interactive Dash + Plotly Dashboard for World Bank Inflation Data
Run this script to launch the dashboard: python run_dashboard.py
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from dash import Dash, dcc, html, Input, Output
import os
import sys

# Load data
data_path = Path(__file__).parent.parent / 'data' / 'processed_inflation_data.csv'
if not data_path.exists():
    print(f"Error: Data file not found at {data_path}")
    print("Please run the preprocessing notebook first.")
    sys.exit(1)

df = pd.read_csv(data_path)
print(f"✓ Loaded {len(df)} records from {data_path}")

# Remove rows with missing countries
df = df.dropna(subset=['country'])

# Initialize Dash app
app = Dash(__name__)
server = app.server


@server.get('/health')
def health_check():
    return {'status': 'ok'}, 200

# Get unique values
countries = sorted(df['country'].unique())
years = sorted(df['year'].unique())

print(f"✓ Dashboard initialized with {len(countries)} countries")
print(f"✓ Year range: {years[0]} - {years[-1]}")

# Define app layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🌍 World Bank Inflation Data Dashboard", 
                style={'textAlign': 'center', 'marginBottom': 10, 'color': '#1f77b4'}),
        html.P("Interactive Analysis of Global Inflation Trends (2000-2024)",
               style={'textAlign': 'center', 'color': '#666', 'marginBottom': 0}),
        html.Hr()
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'marginBottom': 20, 'borderRadius': '5px'}),
    
    # Control Panel
    html.Div([
        html.Div([
            html.Div([
                html.Label("Select Country:", style={'fontWeight': 'bold', 'marginBottom': '8px'}),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': 'All Countries', 'value': 'ALL'}] + 
                            [{'label': c, 'value': c} for c in countries],
                    value='United States',
                    style={'width': '100%'}
                )
            ], style={'marginBottom': '15px'}),
            
            html.Label("Inflation Category Filter:", style={'fontWeight': 'bold', 'marginBottom': '8px'}),
            dcc.Checklist(
                id='category-filter',
                options=[
                    {'label': ' Low (< 2%)', 'value': 'Low'},
                    {'label': ' Moderate (2-5%)', 'value': 'Moderate'},
                    {'label': ' High (5-10%)', 'value': 'High'},
                    {'label': ' Very High (> 10%)', 'value': 'Very High'}
                ],
                value=['Low', 'Moderate', 'High', 'Very High'],
                inline=True,
                style={'marginBottom': '15px'}
            ),
        ], style={'flex': '1', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("Year Range:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'display': 'block'}),
            dcc.RangeSlider(
                id='year-slider',
                min=years[0],
                max=years[-1],
                value=[max(years[0], years[-1]-10), years[-1]],  # Last 10 years default
                marks={year: str(year) for year in range(years[0], years[-1] + 1, 5)},
                tooltip={"placement": "bottom", "always_visible": True},
                step=1
            ),
            html.Div(id='year-display', style={'marginTop': '10px', 'fontSize': '12px', 'color': '#666'})
        ], style={'flex': '2', 'marginLeft': '20px'})
    ], style={'display': 'flex', 'marginBottom': '30px', 'backgroundColor': '#fff', 
              'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),
    
    # Row 1: Time Series and Statistics
    html.Div([
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="default",
                children=[dcc.Graph(id='time-series-graph')]
            )
        ], style={'flex': '1.5', 'marginRight': '15px', 'backgroundColor': '#fff', 
                  'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),
        
        html.Div([
            dcc.Loading(
                id="loading-2",
                type="default",
                children=[dcc.Graph(id='stats-box')]
            )
        ], style={'flex': '1', 'marginLeft': '15px', 'backgroundColor': '#fff', 
                  'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'})
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Row 2: Distribution and Top Countries
    html.Div([
        html.Div([
            dcc.Loading(
                id="loading-3",
                type="default",
                children=[dcc.Graph(id='distribution-graph')]
            )
        ], style={'flex': '1', 'marginRight': '15px', 'backgroundColor': '#fff', 
                  'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),
        
        html.Div([
            dcc.Loading(
                id="loading-4",
                type="default",
                children=[dcc.Graph(id='top-countries-graph')]
            )
        ], style={'flex': '1', 'marginLeft': '15px', 'backgroundColor': '#fff', 
                  'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'})
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Row 3: Anomalies and Category Distribution
    html.Div([
        html.Div([
            dcc.Loading(
                id="loading-5",
                type="default",
                children=[dcc.Graph(id='anomaly-graph')]
            )
        ], style={'flex': '1', 'marginRight': '15px', 'backgroundColor': '#fff', 
                  'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),
        
        html.Div([
            dcc.Loading(
                id="loading-6",
                type="default",
                children=[dcc.Graph(id='category-graph')]
            )
        ], style={'flex': '1', 'marginLeft': '15px', 'backgroundColor': '#fff', 
                  'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'})
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Footer
    html.Div([
        html.P("📊 Data Source: World Bank | 📅 Updated: November 2024 | 💡 Dashboard powered by Dash & Plotly",
               style={'textAlign': 'center', 'color': '#999', 'margin': '0'}),
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'marginTop': '20px'})
    
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f5f5f5', 
          'minHeight': '100vh', 'maxWidth': '1400px', 'margin': '0 auto'})


@app.callback(
    Output('year-display', 'children'),
    Input('year-slider', 'value')
)
def update_year_display(year_range):
    return f"Selected: {year_range[0]} - {year_range[1]}"


@app.callback(
    [
        Output('time-series-graph', 'figure'),
        Output('stats-box', 'figure'),
        Output('distribution-graph', 'figure'),
        Output('top-countries-graph', 'figure'),
        Output('anomaly-graph', 'figure'),
        Output('category-graph', 'figure')
    ],
    [
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('category-filter', 'value')
    ]
)
def update_dashboard(selected_country, year_range, selected_categories):
    # Filter by year
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])].copy()
    
    # Filter by category
    if selected_categories:
        filtered_df = filtered_df[filtered_df['inflation_category'].isin(selected_categories)]
    
    # Filter by country if not "ALL"
    if selected_country != 'ALL':
        country_data = filtered_df[filtered_df['country'] == selected_country].copy()
    else:
        country_data = filtered_df.copy()
    
    # ===== FIGURE 1: TIME SERIES =====
    if selected_country != 'ALL':
        ts_data = country_data.dropna(subset=['inflation_rate']).sort_values('year')
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=ts_data['year'], 
            y=ts_data['inflation_rate'],
            mode='lines+markers', 
            name=selected_country,
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        
        # Add 3-year MA if available
        if 'inflation_3yr_ma' in ts_data.columns and not ts_data['inflation_3yr_ma'].empty:
            fig1.add_trace(go.Scatter(
                x=ts_data['year'], 
                y=ts_data['inflation_3yr_ma'],
                mode='lines', 
                name='3-Year Moving Avg',
                line=dict(color='#ff7f0e', dash='dash', width=2)
            ))
        
        fig1.update_layout(
            title=f'Inflation Trend - {selected_country}',
            xaxis_title='Year',
            yaxis_title='Inflation Rate (%)',
            hovermode='x unified',
            height=450,
            plot_bgcolor='#f9f9f9',
            margin=dict(l=50, r=20, t=40, b=40)
        )
    else:
        # Global trend
        global_trend = filtered_df.groupby('year').agg({
            'inflation_rate': ['mean', 'median', 'std']
        }).reset_index()
        global_trend.columns = ['year', 'mean', 'median', 'std']
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=global_trend['year'], 
            y=global_trend['mean'],
            mode='lines+markers', 
            name='Mean',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=5)
        ))
        fig1.add_trace(go.Scatter(
            x=global_trend['year'], 
            y=global_trend['median'],
            mode='lines+markers', 
            name='Median',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=5)
        ))
        
        fig1.update_layout(
            title='Global Average Inflation Trends',
            xaxis_title='Year',
            yaxis_title='Inflation Rate (%)',
            hovermode='x unified',
            height=450,
            plot_bgcolor='#f9f9f9',
            margin=dict(l=50, r=20, t=40, b=40)
        )
    
    # ===== FIGURE 2: STATISTICS TABLE =====
    stats = country_data['inflation_rate'].describe()
    fig2 = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Statistic</b>', '<b>Value</b>'],
            fill_color='#1f77b4',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[
                ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max'],
                [
                    f"{stats['count']:.0f}",
                    f"{stats['mean']:.2f}%",
                    f"{stats['std']:.2f}%",
                    f"{stats['min']:.2f}%",
                    f"{stats['25%']:.2f}%",
                    f"{stats['50%']:.2f}%",
                    f"{stats['75%']:.2f}%",
                    f"{stats['max']:.2f}%"
                ]
            ],
            fill_color='#f0f0f0',
            align='left',
            font=dict(size=11),
            height=28
        )
    )])
    fig2.update_layout(
        title='Summary Statistics',
        height=450,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # ===== FIGURE 3: DISTRIBUTION =====
    dist_data = country_data.dropna(subset=['inflation_rate'])
    fig3 = px.histogram(
        dist_data, 
        x='inflation_rate',
        nbins=30,
        title='Inflation Rate Distribution',
        labels={'inflation_rate': 'Inflation Rate (%)'},
        color_discrete_sequence=['#1f77b4']
    )
    fig3.update_layout(
        height=450,
        plot_bgcolor='#f9f9f9',
        margin=dict(l=50, r=20, t=40, b=40),
        showlegend=False
    )
    
    # ===== FIGURE 4: TOP COUNTRIES =====
    latest_year = year_range[1]
    top_countries = filtered_df[filtered_df['year'] == latest_year].nlargest(10, 'inflation_rate')
    fig4 = px.bar(
        top_countries,
        x='country',
        y='inflation_rate',
        title=f'Top 10 Countries by Inflation ({latest_year})',
        labels={'inflation_rate': 'Inflation Rate (%)', 'country': 'Country'},
        color='inflation_rate',
        color_continuous_scale='Reds'
    )
    fig4.update_layout(
        xaxis_tickangle=-45,
        height=450,
        plot_bgcolor='#f9f9f9',
        margin=dict(l=50, r=20, t=40, b=60),
        showlegend=False
    )
    
    # ===== FIGURE 5: ANOMALIES =====
    anomaly_data = country_data[country_data['is_anomaly']].copy()
    if len(anomaly_data) > 0:
        fig5 = px.scatter(
            anomaly_data,
            x='year',
            y='inflation_rate',
            size='z_score',
            color='z_score',
            hover_data=['country'],
            title='Detected Inflation Anomalies',
            labels={'inflation_rate': 'Inflation Rate (%)', 'z_score': 'Z-Score'},
            color_continuous_scale='Reds'
        )
    else:
        fig5 = go.Figure()
        fig5.add_annotation(text='No anomalies detected', xref='paper', yref='paper',
                          x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#999'))
        fig5.update_layout(title='Detected Inflation Anomalies')
    
    fig5.update_layout(
        height=450,
        plot_bgcolor='#f9f9f9',
        margin=dict(l=50, r=20, t=40, b=40)
    )
    
    # ===== FIGURE 6: CATEGORY DISTRIBUTION =====
    category_counts = country_data['inflation_category'].value_counts()
    if len(category_counts) > 0:
        fig6 = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Distribution by Inflation Category',
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        )
    else:
        fig6 = go.Figure()
        fig6.add_annotation(text='No data available', xref='paper', yref='paper',
                          x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#999'))
        fig6.update_layout(title='Distribution by Inflation Category')
    
    fig6.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig1, fig2, fig3, fig4, fig5, fig6


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 LAUNCHING DASHBOARD")
    print("="*60)
    print("\n📍 Open your browser and navigate to:")
    print("   http://127.0.0.1:8050/")
    print("\n⏹️  Press CTRL+C to stop the server\n")
    
    app.run(
        debug=os.getenv('DASH_DEBUG', 'false').lower() == 'true',
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', '8050')),
    )