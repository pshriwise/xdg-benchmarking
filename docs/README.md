# XDG Benchmarking Dashboard Documentation

This directory contains documentation for the XDG (Accelerated Discretized Geometry) benchmarking dashboard project.

Shared memory parallelism is the main focus of the performance metrics here due
to the higher memory footprint of the geometry representation employed by XDG.

## Available Documentation

### [Schema Documentation](schema.md)
Complete documentation of the JSON schema used for benchmark data storage, including:
- Config file schema (`config.json`)
- Results file schema (`results.json`)
- Data types and validation rules
- Dynamic discovery system
- Examples and usage guidelines

## Project Structure

```
new-benchmarking-page/
├── docs/                    # This directory
│   ├── README.md           # This file
│   └── schema.md           # Data schema documentation
├── results/                # Benchmark data
│   └── runs/              # Auto-discovered benchmark runs
├── app.py                 # Plotly Dash application
├── requirements.txt       # Python dependencies
├── README.md             # Main project README
└── TODO.md               # Development tasks
```

## Quick Start

1. **Understanding the Data**: Read [schema.md](schema.md) to understand how benchmark data is structured
2. **Adding New Data**: Follow the schema documentation to add new benchmark runs
3. **Running the Dashboard**: See the main [README.md](../README.md) for setup and usage instructions

## Contributing

When adding new features or modifying the data structure:
1. Update the schema documentation in [schema.md](schema.md)
2. Add examples for new data formats
3. Update this README if new documentation is added

## Future Documentation

Planned documentation additions:
- Dashboard user guide
- API documentation (if API endpoints are added)
- Development setup guide
- Deployment instructions