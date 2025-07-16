import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import json

# Initialize the Dash app
app = dash.Dash(__name__, title="XDG Benchmarking Dashboard")
server = app.server

# Data loading and processing functions
def load_benchmark_data():
    """Load all benchmark data from the results directory"""
    data = []
    results_dir = "results"

    if not os.path.exists(results_dir):
        return pd.DataFrame()

    # Find all result directories
    result_dirs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]

    for result_dir in result_dirs:
        run_date = result_dir
        run_path = os.path.join(results_dir, result_dir)

        # Load run summary if available
        run_summary_path = os.path.join(run_path, "run_summary.txt")
        run_config = {}
        if os.path.exists(run_summary_path):
            with open(run_summary_path, 'r') as f:
                content = f.read()
                # Extract run date
                for line in content.split('\n'):
                    if 'Run Date:' in line:
                        run_config['run_date'] = line.split('Run Date:')[1].strip()
                        break

        # Find all CSV files
        csv_files = glob.glob(os.path.join(run_path, "*_scaling.csv"))

        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            # Parse filename: Model_Executable_scaling.csv
            parts = filename.replace('_scaling.csv', '').split('_')
            if len(parts) >= 2:
                executable = parts[-1]  # Last part is executable
                model = '_'.join(parts[:-1])  # Everything else is model name

                try:
                    df = pd.read_csv(csv_file, comment='#')
                    df['Model'] = model
                    df['Executable'] = executable
                    df['Run_ID'] = run_date
                    df['Run_Date'] = run_config.get('run_date', run_date)

                    # Clean up column names
                    df.columns = [col.strip() for col in df.columns]

                    data.append(df)
                except Exception as e:
                    print(f"Error loading {csv_file}: {e}")

    if data:
        combined_df = pd.concat(data, ignore_index=True)
        # Convert threads to numeric, handling scientific notation
        combined_df['# Threads'] = pd.to_numeric(combined_df['# Threads'], errors='coerce')
        combined_df['Active rate'] = pd.to_numeric(combined_df['Active rate'], errors='coerce')
        combined_df['Inactive rate'] = pd.to_numeric(combined_df['Inactive rate'], errors='coerce')

        # Print column names for debugging
        print(f"Column names: {combined_df.columns.tolist()}")
        print(f"Sample data:\n{combined_df.head()}")

        return combined_df
    else:
        return pd.DataFrame()

# Load data
df = load_benchmark_data()

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("XDG Benchmarking Dashboard",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        html.P("Accelerated Discretized Geometry Performance Analysis",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': 18, 'marginBottom': 40})
    ]),

    # Filters section
    html.Div([
        html.H3("Filters", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div([
            html.Div([
                html.Label("Model:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='model-filter',
                    options=[{'label': model, 'value': model} for model in sorted(df['Model'].unique())] if not df.empty else [],
                    value=sorted(df['Model'].unique())[0] if not df.empty else None,
                    style={'width': '100%'}
                )
            ], style={'width': '25%', 'display': 'inline-block', 'marginRight': 20}),

            html.Div([
                html.Label("Executable:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='executable-filter',
                    options=[{'label': exe, 'value': exe} for exe in sorted(df['Executable'].unique())] if not df.empty else [],
                    value=sorted(df['Executable'].unique()) if not df.empty else [],
                    multi=True,
                    style={'width': '100%'}
                )
            ], style={'width': '25%', 'display': 'inline-block', 'marginRight': 20}),

            html.Div([
                html.Label("Run ID:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='run-filter',
                    options=[{'label': run, 'value': run} for run in sorted(df['Run_ID'].unique())] if not df.empty else [],
                    value=sorted(df['Run_ID'].unique()) if not df.empty else [],
                    multi=True,
                    style={'width': '100%'}
                )
            ], style={'width': '25%', 'display': 'inline-block', 'marginRight': 20}),

            html.Div([
                html.Label("Metric:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='metric-filter',
                    options=[
                        {'label': 'Active Rate (particles/sec)', 'value': 'Active rate'},
                        {'label': 'Inactive Rate (particles/sec)', 'value': 'Inactive rate'}
                    ],
                    value='Active rate',
                    style={'width': '100%'}
                )
            ], style={'width': '25%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'marginBottom': 30})
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 10, 'marginBottom': 30}),

    # Main charts section
    html.Div([
        html.Div([
            html.H3("Performance Scaling", style={'color': '#2c3e50', 'marginBottom': 15}),
            dcc.Graph(id='scaling-chart', style={'height': 500})
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.H3("Speedup Analysis", style={'color': '#2c3e50', 'marginBottom': 15}),
            dcc.Graph(id='speedup-chart', style={'height': 500})
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': 30}),

    # Comparison section
    html.Div([
        html.H3("Executable Comparison", style={'color': '#2c3e50', 'marginBottom': 15}),
        dcc.Graph(id='comparison-chart', style={'height': 400})
    ], style={'marginBottom': 30}),

    # Summary statistics
    html.Div([
        html.H3("Summary Statistics", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div(id='summary-stats', style={'backgroundColor': '#ecf0f1', 'padding': 20, 'borderRadius': 10})
    ], style={'marginBottom': 30}),

    # Data table
    html.Div([
        html.H3("Raw Data", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div(id='data-table')
    ])
], style={'padding': 20, 'fontFamily': 'Arial, sans-serif'})

# Callback for filtering data
@callback(
    Output('scaling-chart', 'figure'),
    Output('speedup-chart', 'figure'),
    Output('comparison-chart', 'figure'),
    Output('summary-stats', 'children'),
    Output('data-table', 'children'),
    Input('model-filter', 'value'),
    Input('executable-filter', 'value'),
    Input('run-filter', 'value'),
    Input('metric-filter', 'value')
)
def update_charts(model, executables, runs, metric):
    if df.empty:
        return {}, {}, {}, "No data available", "No data available"

    # Filter data
    filtered_df = df.copy()
    if model:
        filtered_df = filtered_df[filtered_df['Model'] == model]
    if executables:
        filtered_df = filtered_df[filtered_df['Executable'].isin(executables)]
    if runs:
        filtered_df = filtered_df[filtered_df['Run_ID'].isin(runs)]

    if filtered_df.empty:
        return {}, {}, {}, "No data available for selected filters", "No data available"

    # Scaling chart
    scaling_fig = px.line(
        filtered_df,
        x='# Threads',
        y=metric,
        color='Executable',
        title=f'{metric} vs Thread Count',
        labels={'# Threads': 'Number of Threads', metric: f'{metric} (particles/sec)'}
    )
    scaling_fig.update_layout(
        xaxis_title="Number of Threads",
        yaxis_title=f"{metric} (particles/sec)",
        hovermode='x unified'
    )

    # Speedup chart
    speedup_fig = go.Figure()

    # Calculate speedup for each executable
    for exe in filtered_df['Executable'].unique():
        exe_data = filtered_df[filtered_df['Executable'] == exe].copy()
        if not exe_data.empty:
            # Get single-thread performance as baseline
            single_thread = exe_data[exe_data['# Threads'] == 1][metric].iloc[0]
            if pd.notna(single_thread) and single_thread > 0:
                exe_data['Speedup'] = exe_data[metric] / single_thread
                exe_data['Efficiency'] = exe_data['Speedup'] / exe_data['# Threads']

                speedup_fig.add_trace(go.Scatter(
                    x=exe_data['# Threads'],
                    y=exe_data['Speedup'],
                    mode='lines+markers',
                    name=f'{exe} Speedup',
                    hovertemplate='Threads: %{x}<br>Speedup: %{y:.2f}<extra></extra>'
                ))

    # Add ideal speedup line
    max_threads = filtered_df['# Threads'].max()
    speedup_fig.add_trace(go.Scatter(
        x=[1, max_threads],
        y=[1, max_threads],
        mode='lines',
        name='Ideal Speedup',
        line=dict(dash='dash', color='gray'),
        hovertemplate='Threads: %{x}<br>Ideal Speedup: %{y}<extra></extra>'
    ))

    speedup_fig.update_layout(
        title='Speedup vs Thread Count',
        xaxis_title='Number of Threads',
        yaxis_title='Speedup',
        hovermode='x unified'
    )

    # Comparison chart (bar chart for max performance)
    max_performance = filtered_df.groupby(['Model', 'Executable'])[metric].max().reset_index()

    comparison_fig = px.bar(
        max_performance,
        x='Model',
        y=metric,
        color='Executable',
        title=f'Maximum {metric} by Model and Executable',
        barmode='group'
    )
    comparison_fig.update_layout(
        xaxis_title="Model",
        yaxis_title=f"{metric} (particles/sec)",
        hovermode='x unified'
    )

    # Summary statistics
    summary_stats = []

    # Overall statistics
    summary_stats.append(html.H4("Overall Statistics"))
    summary_stats.append(html.P(f"Total data points: {len(filtered_df)}"))
    summary_stats.append(html.P(f"Models: {', '.join(filtered_df['Model'].unique())}"))
    summary_stats.append(html.P(f"Executables: {', '.join(filtered_df['Executable'].unique())}"))
    summary_stats.append(html.P(f"Runs: {', '.join(filtered_df['Run_ID'].unique())}"))

    # Performance statistics
    summary_stats.append(html.H4("Performance Statistics"))
    max_rate = filtered_df[metric].max()
    min_rate = filtered_df[metric].min()
    mean_rate = filtered_df[metric].mean()

    summary_stats.append(html.P(f"Maximum {metric}: {max_rate:.2e} particles/sec"))
    summary_stats.append(html.P(f"Minimum {metric}: {min_rate:.2e} particles/sec"))
    summary_stats.append(html.P(f"Mean {metric}: {mean_rate:.2e} particles/sec"))

    # Best performing configuration
    best_config = filtered_df.loc[filtered_df[metric].idxmax()]
    summary_stats.append(html.H4("Best Performance"))
    summary_stats.append(html.P(f"Model: {best_config['Model']}"))
    summary_stats.append(html.P(f"Executable: {best_config['Executable']}"))
    summary_stats.append(html.P(f"Threads: {best_config['# Threads']}"))
    summary_stats.append(html.P(f"Rate: {best_config[metric]:.2e} particles/sec"))

    # Data table
    table_data = filtered_df.round(2).to_dict('records')
    table_columns = [{"name": col, "id": col} for col in filtered_df.columns]

    data_table = dash.dash_table.DataTable(
        data=table_data,
        columns=table_columns,
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
        ]
    )

    return scaling_fig, speedup_fig, comparison_fig, summary_stats, data_table

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)