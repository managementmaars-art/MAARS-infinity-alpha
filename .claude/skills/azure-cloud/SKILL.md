---
name: azure-cloud
description: "Azure: App Service, Azure Functions, Cosmos DB, Azure OpenAI, DevOps pipelines, AKS, Bicep"
---

# Microsoft Azure Cloud

Production Azure development: App Service for web apps, Azure Functions for serverless, Cosmos DB for NoSQL, Azure OpenAI for AI, Azure DevOps CI/CD pipelines, AKS for Kubernetes, and Bicep for infrastructure as code.

## Authentication with Azure SDK (Python)

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import os

# DefaultAzureCredential checks: Managed Identity → Environment → CLI → VS Code
credential = DefaultAzureCredential()

# For production on Azure (App Service / AKS), use ManagedIdentityCredential
# credential = ManagedIdentityCredential(client_id=os.environ["MI_CLIENT_ID"])

# Key Vault for secrets
vault_url = f"https://{os.environ['KEYVAULT_NAME']}.vault.azure.net"
kv_client = SecretClient(vault_url=vault_url, credential=credential)

db_password = kv_client.get_secret("database-password").value
```

## Azure Functions (v2 Python)

```python
# function_app.py
import azure.functions as func
import logging
import json
from datetime import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# HTTP Trigger
@app.route(route="users/{id}", methods=["GET"])
def get_user(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params.get("id")
    logging.info(f"Fetching user: {user_id}")

    try:
        user = fetch_user_from_db(user_id)
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "User not found"}),
                status_code=404,
                mimetype="application/json"
            )
        return func.HttpResponse(json.dumps(user), mimetype="application/json")
    except Exception as e:
        logging.exception("Error fetching user")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

# Timer Trigger — cron syntax
@app.schedule(schedule="0 0 2 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def daily_cleanup(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.warning("Timer trigger is past due")
    logging.info(f"Daily cleanup started at {datetime.utcnow()}")
    cleanup_expired_records()

# Service Bus Trigger
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="%QUEUE_NAME%",
    connection="SERVICE_BUS_CONNECTION"
)
def process_queue_message(msg: func.ServiceBusMessage) -> None:
    body = msg.get_body().decode("utf-8")
    data = json.loads(body)
    logging.info(f"Processing message: {data['event_type']}")
    handle_event(data)

# Blob Trigger
@app.blob_trigger(
    arg_name="blob",
    path="uploads/{name}",
    connection="STORAGE_CONNECTION"
)
@app.blob_output(arg_name="output", path="processed/{name}", connection="STORAGE_CONNECTION")
def process_blob(blob: func.InputStream, output: func.Out[bytes]) -> None:
    content = blob.read()
    processed = transform(content)
    output.set(processed)
```

## Cosmos DB (NoSQL)

```python
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.container import ContainerProxy

COSMOS_URL = os.environ["COSMOS_URL"]
# Use managed identity — no connection string needed
cosmos_client = CosmosClient(COSMOS_URL, credential=credential)

db = cosmos_client.get_database_client("myapp")
container: ContainerProxy = db.get_container_client("users")

def get_user(user_id: str, tenant_id: str) -> dict | None:
    """Point read — O(1), cheapest operation."""
    try:
        return container.read_item(item=user_id, partition_key=tenant_id)
    except exceptions.CosmosResourceNotFoundError:
        return None

def create_user(user: dict) -> dict:
    return container.create_item(body=user)

def upsert_user(user: dict) -> dict:
    return container.upsert_item(body=user)

def query_users(tenant_id: str, email: str | None = None) -> list[dict]:
    """Cross-partition queries cost more — prefer partition-scoped."""
    params = [{"name": "@tenantId", "value": tenant_id}]
    query = "SELECT * FROM c WHERE c.tenantId = @tenantId"

    if email:
        query += " AND c.email = @email"
        params.append({"name": "@email", "value": email})

    return list(container.query_items(
        query=query,
        parameters=params,
        partition_key=tenant_id,  # scoped to partition = cheaper
        max_item_count=100,
    ))

def bulk_upsert(items: list[dict]) -> None:
    """Batch operations for throughput."""
    for item in items:
        container.upsert_item(body=item)
```

## Azure OpenAI

```python
from openai import AzureOpenAI

openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-10-21",
    azure_ad_token_provider=lambda: credential.get_token(
        "https://cognitiveservices.azure.com/.default"
    ).token,
)

def chat_completion(messages: list[dict], model: str = "gpt-4o") -> str:
    response = openai_client.chat.completions.create(
        model=model,  # deployment name
        messages=messages,
        temperature=0.7,
        max_tokens=4096,
        stream=False,
    )
    return response.choices[0].message.content

def get_embedding(text: str, model: str = "text-embedding-3-large") -> list[float]:
    response = openai_client.embeddings.create(input=text, model=model)
    return response.data[0].embedding

# Streaming response
def stream_chat(messages: list[dict]):
    stream = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main, release/*]
  paths:
    exclude: ['**/*.md', 'docs/**']

pr:
  branches:
    include: [main]

variables:
  pythonVersion: '3.12'
  containerRegistry: 'myregistry.azurecr.io'
  imageRepository: 'myapp'
  dockerfilePath: 'Dockerfile'
  tag: '$(Build.BuildId)'

pool:
  vmImage: ubuntu-latest

stages:
  - stage: Test
    jobs:
      - job: UnitTests
        steps:
          - task: UsePythonVersion@0
            inputs: { versionSpec: '$(pythonVersion)' }

          - script: pip install -r requirements-dev.txt
            displayName: Install dependencies

          - script: |
              pytest tests/unit/ \
                --junitxml=$(Build.ArtifactStagingDirectory)/test-results.xml \
                --cov=src --cov-report=xml:$(Build.ArtifactStagingDirectory)/coverage.xml
            displayName: Run unit tests

          - task: PublishTestResults@2
            inputs:
              testResultsFormat: JUnit
              testResultsFiles: '$(Build.ArtifactStagingDirectory)/test-results.xml'

  - stage: Build
    dependsOn: Test
    condition: succeeded()
    jobs:
      - job: BuildAndPush
        steps:
          - task: Docker@2
            displayName: Build and push image
            inputs:
              command: buildAndPush
              repository: $(imageRepository)
              dockerfile: $(dockerfilePath)
              containerRegistry: myAcr
              tags: |
                $(tag)
                latest

  - stage: DeployStaging
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    environment: staging
    jobs:
      - deployment: DeployToAKS
        strategy:
          runOnce:
            deploy:
              steps:
                - task: HelmDeploy@0
                  inputs:
                    command: upgrade
                    chartName: ./charts/myapp
                    releaseName: myapp-staging
                    namespace: staging
                    valueFile: './charts/myapp/values-staging.yaml'
                    overrideValues: 'image.tag=$(tag)'
```

## Bicep Infrastructure as Code

```bicep
// main.bicep
@description('The environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('The Azure region for all resources')
param location string = resourceGroup().location

var appName = 'myapp-${environment}'
var tags = { Environment: environment, Project: 'MyApp', ManagedBy: 'Bicep' }

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan'
  location: location
  tags: tags
  sku: {
    name: environment == 'prod' ? 'P2v3' : 'B2'
    tier: environment == 'prod' ? 'PremiumV3' : 'Basic'
  }
  properties: { reserved: true }  // Linux
}

// App Service
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: appName
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }  // Managed Identity
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      pythonVersion: '3.12'
      alwaysOn: environment == 'prod'
      minTlsVersion: '1.2'
      appSettings: [
        { name: 'KEYVAULT_NAME', value: keyVault.name }
        { name: 'COSMOS_URL', value: cosmosAccount.properties.documentEndpoint }
        { name: 'ENVIRONMENT', value: environment }
      ]
    }
    httpsOnly: true
  }
}

// Key Vault with access policy for the web app's managed identity
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${appName}-kv'
  location: location
  tags: tags
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
}

// RBAC: give web app Key Vault Secrets User role
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, webApp.id, '4633458b-17de-408a-b874-0445c86b69e6')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
```

## Best Practices

- Use **Managed Identity** everywhere — never store connection strings or keys in app settings
- Use **Key Vault references** in App Service settings: `@Microsoft.KeyVault(SecretUri=...)`
- Enable **Azure Defender for Cloud** on all subscriptions for security posture management
- Use **Private Endpoints** for Cosmos DB, Storage, and Key Vault in production
- Set **diagnostic settings** on all resources to send logs to Log Analytics Workspace
- Use **Azure Policy** to enforce tagging, allowed regions, and SKU restrictions
- For Cosmos DB: design partition keys carefully — aim for even distribution and high-cardinality
- For AKS: use **Workload Identity** (not Pod Identity), enable **KEDA** for event-driven autoscaling
- Prefer **Consumption plan** Azure Functions for sporadic workloads; **Flex Consumption** for latency-sensitive
- Use Bicep modules from the **Azure Verified Modules** library for production-ready IaC

## Models to Use

- **Default**: `claude-sonnet-4-5` — Functions, Cosmos DB, Azure OpenAI, pipelines
- **Architecture / IaC**: `claude-opus-4-5` — AKS design, Bicep modules, enterprise landing zones
- **Quick snippets**: `claude-haiku-3-5` — pipeline YAML, Bicep resources, SDK calls
