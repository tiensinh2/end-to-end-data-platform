# 🚀 Binance Real-Time Data Platform

An end-to-end streaming data pipeline that ingests real-time cryptocurrency market data from Binance WebSocket API, processes it with Apache Flink, stores it in Google Cloud, and visualizes it with Looker Studio.

---

## 📊 Architecture

```
Binance WebSocket API
        ↓
  Kafka (Docker)
        ↓
Apache Flink (Docker)
        ↓
  BigQuery (GCP)
        ↓
  dbt Transform
        ↓
 Looker Studio
```

**Orchestration**: Kestra schedules dbt runs hourly  
**Infrastructure**: Terraform provisions all GCP resources

---

## 🛠️ Technologies

| Layer | Technology |
|-------|-----------|
| Cloud | Google Cloud Platform (GCP) |
| IaC | Terraform |
| Ingestion | Binance WebSocket API |
| Message Broker | Apache Kafka (KRaft mode) |
| Stream Processing | Apache Flink + PyFlink |
| Data Lake | Google Cloud Storage (GCS) |
| Data Warehouse | BigQuery |
| Transformation | dbt (dbt-bigquery) |
| Orchestration | Kestra |
| Dashboard | Looker Studio |

---

## 📁 Project Structure

```
end-to-end-data-platform/
├── terraform/                  # IaC - GCP infrastructure
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── producer/                   # Binance WebSocket producer
│   └── producer.py
├── flink/                      # Flink streaming job
│   ├── Dockerfile
│   └── consumer.py
├── dbt/                        # dbt transformation
│   └── binance_analytics/
│       ├── models/
│       │   ├── staging/
│       │   │   ├── stg_klines.sql
│       │   │   └── sources.yml
│       │   └── mart/
│       │       ├── mart_price_over_time.sql
│       │       └── mart_volume_by_symbol.sql
│       └── dbt_project.yml
├── kestra/                     # Kestra orchestration flows
│   └── flows/
│       └── binance_dbt.yml
├── docker-compose.yml          # Kafka + Flink cluster
├── credentials.json            # GCP service account (not committed)
└── README.md
```

---

## 📋 Prerequisites

- Google Cloud Platform account (with $300 free credit)
- Docker + Docker Compose
- Python 3.10+
- Terraform
- `gcloud` CLI
- `uv` package manager

---

## 🚀 Reproduction Steps

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd end-to-end-data-platform
```

### 2. Setup GCP credentials

1. Go to [GCP Console](https://console.cloud.google.com)
2. Create a new project or use existing one
3. Go to **IAM & Admin → Service Accounts**
4. Create a service account with **Editor** role
5. Create and download JSON key → save as `credentials.json` in project root
6. Enable required APIs:
   - BigQuery API
   - Cloud Storage API

```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="./credentials.json"
```

### 3. Provision GCP infrastructure with Terraform

```bash
cd terraform/
terraform init
terraform plan -var="project_id=YOUR_GCP_PROJECT_ID"
terraform apply -var="project_id=YOUR_GCP_PROJECT_ID"
```

This creates:
- GCS bucket (data lake)
- BigQuery dataset `binance_data`
- BigQuery table `raw_klines` (partitioned by day, clustered by symbol)

### 4. Start Kafka + Flink cluster

```bash
cd ..
docker-compose up -d --build
```

Services started:
- `kafka` — Kafka broker (KRaft mode, no Zookeeper)
- `jobmanager` — Flink Job Manager (UI at http://localhost:8081)
- `taskmanager` — Flink Task Manager
- `flink-job` — PyFlink consumer job
- `kestra` — Orchestration UI at http://localhost:8080
- `postgres` — Kestra backend

### 5. Run the Binance producer

```bash
# Install dependencies
uv sync

# Run producer (streams real-time data from Binance)
uv run producer/producer.py
```

Producer subscribes to Binance WebSocket for:
- `BTCUSDT` — Bitcoin/USDT 1m klines
- `ETHUSDT` — Ethereum/USDT 1m klines
- `BNBUSDT` — BNB/USDT 1m klines

### 6. Verify data in BigQuery

After a few minutes, check BigQuery:

```sql
SELECT * FROM `YOUR_PROJECT_ID.binance_data.raw_klines`
ORDER BY open_time DESC
LIMIT 10
```

### 7. Run dbt transformations

```bash
# Setup dbt environment
python -m venv dbt-env
source dbt-env/bin/activate
pip install dbt-bigquery==1.8.2

# Configure dbt profile (~/.dbt/profiles.yml)
# See profiles.yml.example for reference

# Run dbt
cd dbt/binance_analytics
dbt debug     # verify connection
dbt run       # run all models
dbt test      # run tests
```

dbt creates:
- `binance_data_staging.stg_klines` — cleaned staging view
- `binance_data_mart.mart_price_over_time` — price over time table
- `binance_data_mart.mart_volume_by_symbol` — volume by symbol table

### 8. Setup Kestra orchestration

1. Go to http://localhost:8080
2. Navigate to **Flows → Import**
3. Upload `kestra/flows/binance_dbt.yml`

Kestra schedules dbt to run every hour automatically.

### 9. Dashboard

Dashboard is built with **Looker Studio** connected to BigQuery mart tables:

- **Tile 1**: Price over time (time series chart) — `mart_price_over_time`
- **Tile 2**: Volume by symbol (bar chart) — `mart_volume_by_symbol`

👉 [View Dashboard](#) *(add your Looker Studio link here)*

---

## 🗺️ Data Flow

```
1. Binance WebSocket → producer.py
   └── Sends 1-minute OHLCV kline data to Kafka topic "binance-klines"

2. Kafka → Flink consumer (consumer.py)
   └── Reads from Kafka, inserts rows into BigQuery raw_klines table

3. BigQuery raw_klines → dbt
   └── stg_klines (view): cleans and casts data types
   └── mart_price_over_time (table): price history with % change
   └── mart_volume_by_symbol (table): hourly volume aggregation

4. Kestra → schedules dbt run every hour

5. Looker Studio → reads from mart tables for visualization
```

---

## 📊 Dashboard Preview

| Tile | Chart Type | Description |
|------|-----------|-------------|
| Price Over Time | Time Series | Close price of BTC/ETH/BNB per minute |
| Volume by Symbol | Bar Chart | Total trading volume per symbol per hour |

---

## ⚠️ Important Notes

- `credentials.json` is in `.gitignore` — never commit it
- Use `.env.example` as reference for environment variables
- Kafka runs on port `29092` for local connections, `9092` for Docker internal
- Flink UI available at http://localhost:8081
- Kestra UI available at http://localhost:8080

---

## 🧹 Cleanup

To destroy all GCP resources:

```bash
cd terraform/
terraform destroy -var="project_id=YOUR_GCP_PROJECT_ID"
```

To stop Docker services:

```bash
docker-compose down
```