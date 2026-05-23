# Service Metrics dbt Project

Transforms raw Open Signal data loaded into PostgreSQL into clean, analytics-ready tables.

## Structure
models/
├── staging/    # Views — cleans and standardises raw source tables
└── marts/      # Tables — aggregated, analytics-ready models

## Running

```bash
dbt run        # build all models
dbt test       # run data quality tests
dbt docs serve # view documentation
```

## Connections
Configure your Postgres connection in `profiles.yml` or via environment variables. Target database is `service_metrics_db`, schema `public`.