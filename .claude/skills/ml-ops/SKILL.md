---
name: ml-ops
description: "MLOps: Weights & Biases, MLflow, DVC, model registry, CI/CD for ML, feature stores, monitoring"
---

# MLOps

Production ML operations: experiment tracking with W&B and MLflow, data versioning with DVC, model registry, CI/CD for ML pipelines, feature stores, and production model monitoring.

## Weights & Biases (W&B)

```python
import wandb
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# Initialize run with full config
run = wandb.init(
    project="my-nlp-project",
    entity="my-team",
    name="bert-finetune-v3",
    config={
        "model": "bert-base-uncased",
        "learning_rate": 2e-5,
        "batch_size": 32,
        "epochs": 10,
        "warmup_ratio": 0.1,
        "weight_decay": 0.01,
        "max_length": 512,
        "dataset": "imdb",
    },
    tags=["bert", "classification", "production-candidate"],
    notes="Testing warmup schedule vs constant LR",
    group="bert-ablations",
    job_type="train",
)

# Access config (handles sweeps automatically)
config = wandb.config

# Watch model — log gradients and parameters
wandb.watch(model, log="all", log_freq=100)

# Training loop with logging
for epoch in range(config.epochs):
    model.train()
    for batch_idx, batch in enumerate(train_loader):
        optimizer.zero_grad()
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        scheduler.step()

        if batch_idx % 50 == 0:
            wandb.log({
                "train/loss": loss.item(),
                "train/learning_rate": scheduler.get_last_lr()[0],
                "train/epoch": epoch + batch_idx / len(train_loader),
                "train/grad_norm": torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0),
            })

    # Epoch-level validation
    val_metrics = evaluate(model, val_loader)
    wandb.log({
        "val/accuracy": val_metrics["accuracy"],
        "val/f1": val_metrics["f1"],
        "val/loss": val_metrics["loss"],
        "epoch": epoch,
    })

    # Save best model artifact
    if val_metrics["f1"] > best_f1:
        best_f1 = val_metrics["f1"]
        artifact = wandb.Artifact("bert-classifier", type="model",
            metadata={"f1": best_f1, "epoch": epoch})
        artifact.add_dir("./model_checkpoint")
        run.log_artifact(artifact, aliases=["best", "latest"])

# W&B Sweeps for hyperparameter search
sweep_config = {
    "method": "bayes",
    "metric": {"name": "val/f1", "goal": "maximize"},
    "parameters": {
        "learning_rate": {"distribution": "log_uniform_values", "min": 1e-6, "max": 1e-4},
        "batch_size": {"values": [16, 32, 64]},
        "warmup_ratio": {"distribution": "uniform", "min": 0.0, "max": 0.3},
    },
    "early_terminate": {"type": "hyperband", "min_iter": 3},
}
sweep_id = wandb.sweep(sweep_config, project="my-nlp-project")
wandb.agent(sweep_id, function=train, count=20)
```

## MLflow: Experiment Tracking and Model Registry

```python
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://mlflow-server:5000")
mlflow.set_experiment("customer-churn-prediction")

# Training with autologging (scikit-learn)
mlflow.sklearn.autolog(log_model_signatures=True, log_input_examples=True)

with mlflow.start_run(run_name="xgboost-v2-tuned") as run:
    # Manual logging for custom metrics
    mlflow.log_params({
        "model_type": "XGBClassifier",
        "n_estimators": 500,
        "max_depth": 6,
        "feature_set": "v3",
    })

    model = XGBClassifier(n_estimators=500, max_depth=6)
    model.fit(X_train, y_train)

    # Log metrics
    metrics = evaluate_model(model, X_test, y_test)
    mlflow.log_metrics(metrics)

    # Log artifacts
    mlflow.log_artifact("reports/feature_importance.png")
    mlflow.log_artifact("reports/confusion_matrix.png")

    # Log model with signature
    from mlflow.models.signature import infer_signature
    signature = infer_signature(X_train, model.predict_proba(X_train))
    mlflow.sklearn.log_model(
        model,
        "churn-model",
        signature=signature,
        registered_model_name="CustomerChurnModel",
        input_example=X_train[:5],
    )

    run_id = run.info.run_id

# Model Registry promotion workflow
client = MlflowClient()

def promote_model(model_name: str, version: int, stage: str):
    """Promote a model version to Staging or Production."""
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,
        archive_existing_versions=(stage == "Production"),
    )
    client.update_model_version(
        name=model_name, version=version,
        description=f"Promoted to {stage} on {datetime.now().isoformat()}"
    )

# Load production model
model = mlflow.sklearn.load_model(f"models:/CustomerChurnModel/Production")
```

## DVC: Data Version Control

```yaml
# dvc.yaml — ML pipeline definition
stages:
  ingest:
    cmd: python src/ingest.py
    deps:
      - src/ingest.py
      - data/raw/
    outs:
      - data/interim/raw_events.parquet

  featurize:
    cmd: python src/featurize.py
    deps:
      - src/featurize.py
      - data/interim/raw_events.parquet
    outs:
      - data/features/train.parquet
      - data/features/test.parquet
    metrics:
      - reports/feature_stats.json

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/features/train.parquet
      - params.yaml
    outs:
      - models/churn_model.pkl
    metrics:
      - reports/metrics.json:
          cache: false
    plots:
      - reports/feature_importance.csv:
          x: feature
          y: importance

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/churn_model.pkl
      - data/features/test.parquet
    metrics:
      - reports/eval_metrics.json:
          cache: false
```

```bash
# DVC commands
dvc init
dvc remote add -d myremote s3://my-bucket/dvc-store
dvc add data/raw/events.csv               # track large file
dvc push                                  # push to remote
dvc pull                                  # restore tracked files
dvc repro                                 # run pipeline (skip up-to-date stages)
dvc params diff HEAD~1                    # compare params
dvc metrics show                          # show current metrics
dvc metrics diff HEAD~1                   # compare metrics
dvc dag                                   # visualize pipeline DAG
```

## CI/CD for ML (GitHub Actions)

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    branches: [main]
    paths: ['src/**', 'params.yaml', 'dvc.yaml']
  pull_request:
    paths: ['src/**', 'params.yaml']

jobs:
  train-and-evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: '3.12' }

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Configure DVC remote
        run: |
          dvc remote modify myremote access_key_id ${{ secrets.AWS_ACCESS_KEY_ID }}
          dvc remote modify myremote secret_access_key ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Pull DVC data
        run: dvc pull data/features/

      - name: Run pipeline
        run: dvc repro
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          WANDB_API_KEY: ${{ secrets.WANDB_API_KEY }}

      - name: Check metrics gate
        run: |
          python scripts/check_metrics.py \
            --min-auc 0.85 \
            --min-f1 0.80 \
            --metrics-file reports/eval_metrics.json

      - name: Push DVC artifacts
        if: github.ref == 'refs/heads/main'
        run: dvc push

      - name: Register model (if main)
        if: github.ref == 'refs/heads/main' && success()
        run: python scripts/register_model.py --stage Staging
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
```

## Feature Store (Feast)

```python
# feature_repo/feature_store.yaml
project: my_ml_project
registry: s3://my-bucket/feast/registry.db
provider: aws
online_store:
  type: redis
  connection_string: redis://redis-host:6379

# feature_repo/features.py
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from datetime import timedelta

# Define entity
user = Entity(name="user_id", value_type=ValueType.STRING, description="User identifier")

# Data source
user_stats_source = FileSource(
    path="s3://my-bucket/user_stats.parquet",
    event_timestamp_column="event_timestamp",
)

# Feature view
user_features = FeatureView(
    name="user_features",
    entities=["user_id"],
    ttl=timedelta(days=7),
    features=[
        Feature(name="purchase_count_7d", dtype=ValueType.INT64),
        Feature(name="avg_order_value", dtype=ValueType.FLOAT),
        Feature(name="days_since_last_purchase", dtype=ValueType.INT32),
        Feature(name="preferred_category", dtype=ValueType.STRING),
    ],
    online=True,
    source=user_stats_source,
)

# Serving features
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo")

# Training: point-in-time correct feature retrieval
training_df = store.get_historical_features(
    entity_df=entity_df,  # has user_id + event_timestamp
    features=["user_features:purchase_count_7d", "user_features:avg_order_value"],
).to_df()

# Online serving (low-latency)
features = store.get_online_features(
    features=["user_features:purchase_count_7d", "user_features:avg_order_value"],
    entity_rows=[{"user_id": "user-123"}],
).to_dict()
```

## Production Model Monitoring

```python
# Evidently for data drift and model performance monitoring
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.metrics import ColumnDriftMetric

# Build monitoring report
report = Report(metrics=[
    DataDriftPreset(),
    ClassificationPreset(),
    ColumnDriftMetric(column_name="age"),
    ColumnDriftMetric(column_name="purchase_count_7d"),
])

report.run(reference_data=reference_df, current_data=current_df)
report.save_html("monitoring_report.html")

# Extract results programmatically
results = report.as_dict()
drift_detected = results["metrics"][0]["result"]["dataset_drift"]

if drift_detected:
    send_alert("Data drift detected — model retraining triggered")
    trigger_retraining_pipeline()
```

## Best Practices

- Log everything in experiments: hyperparams, data versions, environment, metrics, artifacts
- Pin library versions in `requirements.txt` and track with DVC or Git — reproducibility is critical
- Use a model registry with stage transitions (Development → Staging → Production) — never deploy directly
- Implement metric gates in CI: if accuracy drops below threshold, block promotion
- Monitor three things in production: data drift, prediction drift, and business metrics
- Use feature stores to ensure train/serve consistency — the #1 source of production ML bugs
- Version your data with DVC: treat data like code — every experiment should be reproducible from scratch
- Use `mlflow.set_tags({"git_commit": git_sha, "dataset_version": dvc_sha})` for full lineage
- Separate training and inference environments — inference should not depend on heavy training libraries
- Use canary deployments for model releases: route 5% of traffic to new model before full rollout

## Models to Use

- **Default**: `claude-sonnet-4-5` — MLflow, W&B, DVC pipelines, feature store setup
- **Complex ML systems**: `claude-opus-4-5` — multi-model architectures, drift detection strategy, feature engineering
- **Quick scripts**: `claude-haiku-3-5` — evaluation scripts, metric reporting, simple pipeline stages
