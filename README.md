# XDG Benchmarking Dashboard

A comprehensive Plotly Dash web application for exploring and analyzing XDG (Accelerated Discretized Geometry) benchmarking results.

## Features

### 📊 Interactive Visualizations
- **Performance Scaling Charts**: Compare thread scaling across different executables
- **Speedup Analysis**: Visualize parallel efficiency and speedup curves
- **Executable Comparison**: Bar charts comparing maximum performance across models
- **Real-time Filtering**: Filter by model, executable, run ID, and performance metric

### 🔍 Data Analysis
- **Summary Statistics**: Key performance metrics and best configurations
- **Raw Data Table**: Interactive table with all benchmark data
- **Multi-run Support**: Compare results across different benchmark runs
- **Statistical Analysis**: Performance comparisons and efficiency calculations

### 🎯 Key Metrics
- **Active Rate**: Particles processed per second during active simulation
- **Inactive Rate**: Particles processed per second during inactive/burnup cycles
- **Speedup**: Performance improvement relative to single-thread execution
- **Efficiency**: Speedup divided by number of threads

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Dashboard
1. Ensure your benchmark results are in the `results/` directory
2. Start the dashboard:
   ```bash
   python app.py
   ```
3. Open your web browser and navigate to `http://localhost:8050`

### Data Structure
The dashboard expects benchmark results in the following structure:
```
results/
├── 20250715_171058/
│   ├── run_summary.txt
│   ├── Model_executable_scaling.csv
│   └── ...
└── 20250715_181043/
    ├── run_summary.txt
    ├── Model_executable_scaling.csv
    └── ...
```

### CSV File Format
Each scaling CSV file should contain:
```csv
# Threads,Inactive rate,Active rate
1.000000000000000e+00,nan,5.704179589970383e+03
5.000000000000000e+00,nan,1.762661104642666e+04
1.000000000000000e+01,nan,3.233096046521205e+04
1.500000000000000e+01,nan,4.361667815749022e+04
```

## Dashboard Features

### Filters
- **Model**: Select specific reactor models (Tokamak, ATR, MSRE)
- **Executable**: Choose which OpenMC implementations to compare
- **Run ID**: Filter by specific benchmark runs
- **Metric**: Switch between Active and Inactive rates

### Charts
1. **Performance Scaling**: Line charts showing performance vs thread count
2. **Speedup Analysis**: Speedup curves with ideal scaling reference
3. **Executable Comparison**: Bar charts comparing maximum performance
4. **Summary Statistics**: Key metrics and best configurations
5. **Raw Data Table**: Interactive table with all data points

### Interactivity
- Hover over data points for detailed information
- Zoom and pan on charts
- Download charts as PNG images
- Filter data dynamically
- Sort and search in data tables

## Supported Models and Executables

### Models
- **Tokamak**: Fusion reactor geometry
- **ATR**: Advanced Test Reactor (fission)
- **MSRE**: Molten Salt Reactor Experiment

### Executables
- **double-down**: Reference/baseline OpenMC implementation
- **xdg**: Accelerated Discretized Geometry implementation
- **moab**: MOAB mesh-based optimization

## Development

### Adding New Features
The dashboard is built with Plotly Dash and can be easily extended:
- Add new chart types in the callback functions
- Implement additional filtering options
- Create custom analysis functions
- Add export capabilities

### Customization
- Modify the layout in `app.layout`
- Add new callbacks for interactive features
- Customize styling and themes
- Implement additional data processing functions

## Troubleshooting

### Common Issues
1. **No data displayed**: Check that CSV files are in the correct format and location
2. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **Port conflicts**: Change the port in `app.py` if 8050 is already in use

### Data Validation
The dashboard automatically validates:
- CSV file format and column names
- Numeric data conversion
- Missing or invalid data points

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the data format requirements
3. Ensure all dependencies are properly installed
4. Create an issue with detailed error information