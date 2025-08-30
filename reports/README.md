# Reports Directory

This directory contains generated visualizations and analysis reports.

## Structure

```
reports/
└── figures/                # Generated plots and visualizations
    ├── overall_trend.png
    ├── top_reactions_bar.png
    ├── top_drugs_bar.png
    ├── top_reactions_trend.png
    ├── top_drugs_trend.png
    └── summary_statistics.png
```

## Generated Visualizations

The visualization files are created by running:

```bash
python -m src.etl.build_all
```

### Plot Types

- **Overall Trend**: Monthly adverse event reports over time
- **Top Reactions Bar**: Bar chart of most frequent adverse reactions
- **Top Drugs Bar**: Bar chart of drugs with most reports
- **Top Reactions Trend**: Time series for top adverse reactions
- **Top Drugs Trend**: Time series for top reported drugs
- **Summary Statistics**: Dashboard overview of key metrics

## Usage

These plots are used in the analysis and can be included in presentations or reports about adverse event trends.
