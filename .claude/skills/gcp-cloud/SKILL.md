---
name: gcp-cloud
description: "Google Cloud Platform: Cloud Run, BigQuery, Pub/Sub, Cloud Storage, Vertex AI, Firebase, GKE"
---

# Google Cloud Platform (GCP)

Production GCP usage: Cloud Run for serverless containers, BigQuery for analytics, Pub/Sub for messaging, Cloud Storage, Vertex AI for ML, Firebase for mobile/web backends, and GKE for Kubernetes workloads.

## Authentication and SDK Setup

```python
# google-cloud-* libraries use Application Default Credentials
# gcloud auth application-default login  (local dev)
# Service accounts for production (Workload Identity preferred on GCP)

from google.cloud import bigquery, storage, pubsub_v1
from google.oauth2 import service_account
import os

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
REGION = os.environ.get("GCP_REGION", "us-central1")

# Explicit credentials (avoid in GKE — use Workload Identity instead)
# credentials = service_account.Credentials.from_service_account_file("sa.json")
```

## Cloud Run: Deploy Containerized Services

```dockerfile
# Dockerfile — optimized for Cloud Run
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

# Cloud Run sets PORT env var
ENV PORT=8080
EXPOSE $PORT

# Use exec form to handle SIGTERM properly
CMD ["python", "-m", "gunicorn", "main:app", \
     "--workers", "2", "--threads", "8", \
     "--bind", "0.0.0.0:8080", "--timeout", "0"]
```

```yaml
# cloudbuild.yaml — CI/CD pipeline
steps:
  - name: gcr.io/cloud-builders/docker
    args:
      - build
      - --cache-from
      - $_AR_HOSTNAME/$PROJECT_ID/cloud-run-source-deploy/$REPO_NAME/$_SERVICE_NAME:latest
      - --tag
      - $_AR_HOSTNAME/$PROJECT_ID/cloud-run-source-deploy/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA
      - --tag
      - $_AR_HOSTNAME/$PROJECT_ID/cloud-run-source-deploy/$REPO_NAME/$_SERVICE_NAME:latest
      - .

  - name: gcr.io/cloud-builders/docker
    args: [push, --all-tags, "$_AR_HOSTNAME/$PROJECT_ID/cloud-run-source-deploy/$REPO_NAME/$_SERVICE_NAME"]

  - name: gcr.io/google.com/cloudsdktool/cloud-sdk:slim
    entrypoint: gcloud
    args:
      - run
      - deploy
      - $_SERVICE_NAME
      - --image=$_AR_HOSTNAME/$PROJECT_ID/cloud-run-source-deploy/$REPO_NAME/$_SERVICE_NAME:$COMMIT_SHA
      - --region=$_DEPLOY_REGION
      - --set-env-vars=GCP_PROJECT_ID=$PROJECT_ID
      - --service-account=my-service@$PROJECT_ID.iam.gserviceaccount.com
      - --min-instances=1
      - --max-instances=100
      - --concurrency=80
      - --cpu=2
      - --memory=2Gi
      - --no-allow-unauthenticated

options:
  dynamicSubstitutions: true
  logging: CLOUD_LOGGING_ONLY
```

## BigQuery: Analytics at Scale

```python
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, QueryJobConfig, WriteDisposition

bq = bigquery.Client(project=PROJECT_ID)

def run_query(sql: str, params: list | None = None) -> list[dict]:
    """Run a parameterized BigQuery query."""
    config = QueryJobConfig(
        query_parameters=params or [],
        use_query_cache=True,
        maximum_bytes_billed=10 * 1024**3,  # 10 GB safety limit
    )
    job = bq.query(sql, job_config=config)
    return [dict(row) for row in job.result()]

# Example: parameterized query
results = run_query("""
    SELECT
        DATE(event_timestamp) AS date,
        event_name,
        COUNT(*)              AS event_count,
        COUNT(DISTINCT user_pseudo_id) AS unique_users
    FROM `{project}.analytics_{property_id}.events_*`
    WHERE _TABLE_SUFFIX BETWEEN @start_date AND @end_date
      AND event_name IN UNNEST(@event_names)
    GROUP BY 1, 2
    ORDER BY 1 DESC, 3 DESC
""".format(project=PROJECT_ID, property_id="123456789"),
params=[
    bigquery.ScalarQueryParameter("start_date", "STRING", "20260101"),
    bigquery.ScalarQueryParameter("end_date", "STRING", "20260131"),
    bigquery.ArrayQueryParameter("event_names", "STRING", ["purchase", "add_to_cart"]),
])

def load_dataframe(df, table_id: str, write_disposition=WriteDisposition.WRITE_APPEND):
    """Load a pandas DataFrame to BigQuery."""
    config = LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=False,   # always define schema explicitly in prod
        create_disposition="CREATE_IF_NEEDED",
    )
    job = bq.load_table_from_dataframe(df, table_id, job_config=config)
    job.result()  # wait
    print(f"Loaded {job.output_rows} rows to {table_id}")
```

## Pub/Sub: Event-Driven Messaging

```python
from google.cloud import pubsub_v1
from google.pubsub_v1.types import PubsubMessage
import json, base64

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

TOPIC_PATH = publisher.topic_path(PROJECT_ID, "my-topic")
SUB_PATH = subscriber.subscription_path(PROJECT_ID, "my-subscription")

def publish_event(event_type: str, payload: dict, attributes: dict | None = None) -> str:
    """Publish a JSON event to Pub/Sub."""
    data = json.dumps({"event_type": event_type, **payload}).encode("utf-8")
    attrs = {"event_type": event_type, **(attributes or {})}
    future = publisher.publish(TOPIC_PATH, data=data, **attrs)
    return future.result()  # returns message_id

def subscribe_pull(callback, max_messages: int = 100):
    """Pull-based subscription with manual ack."""
    def wrapped_callback(message: pubsub_v1.subscriber.message.Message):
        try:
            data = json.loads(message.data.decode("utf-8"))
            callback(data, message.attributes)
            message.ack()
        except Exception as e:
            print(f"Error processing message {message.message_id}: {e}")
            message.nack()

    flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)
    streaming_pull = subscriber.subscribe(SUB_PATH, callback=wrapped_callback,
                                          flow_control=flow_control)

    with subscriber:
        try:
            streaming_pull.result(timeout=300)
        except Exception:
            streaming_pull.cancel()
            streaming_pull.result()

# Push subscription Cloud Run handler
from flask import Flask, request
app = Flask(__name__)

@app.route("/pubsub/push", methods=["POST"])
def pubsub_push():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Bad Request", 400

    message = envelope["message"]
    data = json.loads(base64.b64decode(message["data"]).decode("utf-8"))
    attributes = message.get("attributes", {})

    try:
        process_event(data, attributes)
        return "OK", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500  # Pub/Sub will retry
```

## Cloud Storage: Object Storage

```python
from google.cloud import storage

gcs = storage.Client(project=PROJECT_ID)
BUCKET = gcs.bucket(f"{PROJECT_ID}-assets")

def upload_file(local_path: str, gcs_path: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file and return the public URL."""
    blob = BUCKET.blob(gcs_path)
    blob.upload_from_filename(local_path, content_type=content_type)
    return f"gs://{BUCKET.name}/{gcs_path}"

def generate_signed_url(gcs_path: str, expiration_minutes: int = 60) -> str:
    """Generate a time-limited signed URL for private objects."""
    from datetime import timedelta
    blob = BUCKET.blob(gcs_path)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET",
    )

def stream_gcs_to_bigquery(gcs_uri: str, table_id: str, source_format=bigquery.SourceFormat.PARQUET):
    """Load data from GCS directly to BigQuery."""
    config = LoadJobConfig(source_format=source_format, write_disposition=WriteDisposition.WRITE_APPEND)
    job = bq.load_table_from_uri(gcs_uri, table_id, job_config=config)
    job.result()
```

## Vertex AI: Generative AI and ML

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig, SafetySetting, HarmCategory, HarmBlockThreshold

vertexai.init(project=PROJECT_ID, location=REGION)

# Gemini for text generation
model = GenerativeModel(
    "gemini-1.5-pro-002",
    system_instruction="You are a helpful assistant specializing in data analysis.",
)

def generate_text(prompt: str, temperature: float = 0.7) -> str:
    config = GenerationConfig(
        temperature=temperature,
        top_p=0.95,
        max_output_tokens=8192,
    )
    safety = [
        SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                      threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
    ]
    response = model.generate_content(prompt, generation_config=config, safety_settings=safety)
    return response.text

# Embeddings
from vertexai.language_models import TextEmbeddingModel

embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

def get_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = embedding_model.get_embeddings(texts)
    return [e.values for e in embeddings]

# Batch prediction to GCS
from vertexai.preview.batch_prediction import BatchPredictionJob

job = BatchPredictionJob.submit(
    source_model="gemini-1.5-flash-002",
    input_dataset="gs://my-bucket/batch-input.jsonl",
    output_uri_prefix="gs://my-bucket/batch-output/",
)
job.wait()
```

## Best Practices

- Use **Workload Identity Federation** instead of service account keys — no secrets to manage
- Tag all Cloud Run services with `--service-account` pointing to a least-privilege SA
- Use **Secret Manager** for all secrets; reference in Cloud Run via `--set-secrets`
- Enable **Cloud Audit Logs** for all data access in BigQuery and Cloud Storage
- Use BigQuery **partitioned tables** (by date) and **clustering** to reduce bytes scanned and costs
- Set `maximum_bytes_billed` on all BigQuery query jobs to prevent runaway costs
- Use **Pub/Sub Lite** for high-throughput, latency-tolerant workloads at lower cost
- Use **Cloud Armor** for WAF protection on Load Balancers fronting Cloud Run
- Use **VPC Service Controls** to restrict data exfiltration for sensitive BigQuery datasets
- Monitor with **Cloud Monitoring** + **Cloud Trace**; instrument with OpenTelemetry

## Models to Use

- **Default**: `claude-sonnet-4-5` — Cloud Run, BigQuery SQL, Pub/Sub, GCS
- **Architecture**: `claude-opus-4-5` — multi-service design, Vertex AI pipelines, GKE workloads
- **Quick IaC / config**: `claude-haiku-3-5` — Terraform snippets, cloudbuild.yaml, IAM policies
