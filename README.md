# Service Metrics Pipeline

A locally hosted end-to-end data pipeline designed for team use in analysing network service metrics. The pipeline ingests raw network performance data, transforms it through a series of stages, and presents it via an interactive dashboard accessible to the entire team on a local network.

The solution is intentionally designed for on-premises or internal-network deployment, where network metrics are intended to remain within the organization’s environment rather than being exposed through a public-facing application.

![Airflow](./assets/airflow.png)

## Stack
- **Ingestion**: Python + Pandas, FastAPI + Confluent Kafka
- **Storage**: PostgreSQL
- **Orchestration**: Apache Airflow
- **Transformation**: dbt
- **Visualization**: Streamlit + Plotly

## Data Flow

### Batch (Open Signal, High Utilization)
```mermaid
flowchart LR
    A[📄 XLSX, CSV] --> B[⚙️ ELT\nPandas]
    B --> C[(PostgreSQL\nraw)]
    C --> D[dbt\nStaging]
    D --> E[(PostgreSQL\nstg)]
    E --> F[dbt\nMarts]
    F --> G[(PostgreSQL\nmart)]
    G --> H[📊 Streamlit]
```

### Streaming (Speed Test)
```mermaid
flowchart LR
    A[Device] --> B[Spring Boot\nProducer]
    B --> C[Kafka\nTopic]
    C --> D[Spring Boot\nConsumer]
    D --> E[(PostgreSQL\nraw)]
    E --> F[dbt\nStaging]
    F --> G[(PostgreSQL\nstg)]
    G --> H[dbt\nMarts]
    H --> I[(PostgreSQL\nmart)]
    I --> J[📊 Streamlit]
```

## Dashboard

Accessible via browser on the local network at `http://localhost:8501`.

Built with Streamlit and Plotly, the dashboard reads from the mart layer.

### Available Dashboards

- Open Signal

![Dashboard](./assets/open_signal_dashboard.png)

- High Utilization

![Dashboard](./assets/high_utilization_dashboard.png)

- Speed Test

![Dashboard](./assets/speed_test_dashboard.png)

## Structure
```
service_metrics_pipeline/
├── airflow/
│   └── dags/
├── elt/
├── kafka/
├── service_metrics_dbt/
├── dashboard/
│   └── pages/
├── data/
├── docker-compose.yml
├── .env.*
```

>Default Credentials: admin:admin

## Getting Started

### 1. Configure environment variables

Copy and fill in the env each files:
```bash
cp .env.example .env
```

### 2. Start all services
```bash
docker compose up --build
```

### 3. Access
| Service          | URL                   |
|------------------|-----------------------|
| Airflow          | http://localhost:8080 |
| Dashboard        | http://localhost:8501 |
| Producer API     | http://localhost:8000/docs |

## Commands

### Rebuilding a single service
```bash
docker compose up --build <service_name>
```

### Shutting down
```bash
docker compose down
```

### Access Postgres instance
```bash
docker exec -it service-metrics-pipeline-metrics_postgres-1 psql -U postgres
```

## Hypothetical AWS Architecture

This project runs entirely locally via Docker Compose. The diagram below shows how it would map to AWS if deployed for an internal/private org setup.

```mermaid
flowchart TB
    subgraph Ingestion
        S3RAW[(Amazon S3<br/>Raw XLSX/CSV)]
        FASTAPI[FastAPI Kafka Producer<br/>Fargate]
        MSK[Amazon MSK<br/>Kafka Cluster]
        CONSUMER[Python Kafka Consumer<br/>Fargate]
    end

    subgraph Orchestration
        MWAA[Amazon MWAA<br/>Airflow]
    end

    subgraph ELT
        GLUE[AWS Glue<br/>Extract & Load]
        DBT[dbt<br/>Fargate Task]
    end

    subgraph Storage
        RDS[(Amazon RDS<br/>PostgreSQL)]
    end

    subgraph Serving
        DASH[Streamlit Dashboard<br/>ECS/Fargate]
        ALB[Application Load Balancer]
    end

    S3RAW --> GLUE
    FASTAPI --> MSK --> CONSUMER --> RDS
    MWAA --> GLUE --> RDS
    MWAA --> DBT --> RDS
    RDS --> DASH --> ALB
```

## Related Projects

- [service-metrics-service](https://github.com/kirkalyn13/service-metrics-service) — Standalone Spring Boot microservice that decouples the Kafka producer/consumer layer from this pipeline. Exposes a REST API for publishing service metrics to Kafka and persisting them to PostgreSQL.

## Authors

- [Engr. Kirk Alyn Santos](https://github.com/kirkalyn13)

## License

MIT