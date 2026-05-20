terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = file("../credentials.json")
  project     = var.project_id
  region      = var.region
}

# GCS Bucket (Data Lake)
resource "google_storage_bucket" "data_lake" {
  name          = "binance-lake-${var.project_id}"
  location      = var.region
  force_destroy = true
}

# BigQuery Dataset
resource "google_bigquery_dataset" "binance" {
  dataset_id = "binance_data"
  location   = var.region
}

# BigQuery Table
resource "google_bigquery_table" "klines" {
  dataset_id          = google_bigquery_dataset.binance.dataset_id
  table_id            = "raw_klines"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "open_time"
  }

  clustering = ["symbol"]

  schema = jsonencode([
    { name = "symbol",     type = "STRING",    mode = "REQUIRED" },
    { name = "open_time",  type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "open",       type = "FLOAT64",   mode = "NULLABLE" },
    { name = "high",       type = "FLOAT64",   mode = "NULLABLE" },
    { name = "low",        type = "FLOAT64",   mode = "NULLABLE" },
    { name = "close",      type = "FLOAT64",   mode = "NULLABLE" },
    { name = "volume",     type = "FLOAT64",   mode = "NULLABLE" },
    { name = "close_time", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "num_trades", type = "INT64",     mode = "NULLABLE" }
  ])
}