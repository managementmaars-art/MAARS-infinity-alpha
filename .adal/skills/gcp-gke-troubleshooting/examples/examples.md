# GKE Troubleshooting Examples

## Example 1: Complete Troubleshooting Workflow

```bash
#!/bin/bash
# Comprehensive troubleshooting script

NAMESPACE="wtr-supplier-charges"
DEPLOYMENT="supplier-charges-hub"

echo "=== GKE Troubleshooting Workflow ==="

echo ""
echo "1. Pod Status"
kubectl get pods -n $NAMESPACE -o wide

echo ""
echo "2. Describe Problem Pod"
POD=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD -n $NAMESPACE

echo ""
echo "3. Recent Events"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

echo ""
echo "4. Pod Logs (Current)"
kubectl logs $POD -n $NAMESPACE | tail -30

echo ""
echo "5. Pod Logs (Previous - if crashed)"
kubectl logs $POD -n $NAMESPACE --previous 2>/dev/null | tail -30

echo ""
echo "6. Resource Usage"
echo "Pod resources:"
kubectl top pod $POD -n $NAMESPACE
echo ""
echo "Node resources:"
kubectl top nodes

echo ""
echo "7. Health Check Status"
kubectl describe pod $POD -n $NAMESPACE | grep -A 5 "Liveness\|Readiness"

echo ""
echo "8. Service Endpoints"
kubectl get endpoints $DEPLOYMENT -n $NAMESPACE

echo ""
echo "9. ConfigMap/Secrets"
kubectl get configmap,secret -n $NAMESPACE
```

## Example 2: Database Connectivity Debugging

```bash
#!/bin/bash
# Debug Cloud SQL connection issues

POD=$(kubectl get pods -n wtr-supplier-charges -o jsonpath='{.items[0].metadata.name}')
NAMESPACE="wtr-supplier-charges"

echo "=== Cloud SQL Connection Debugging ==="

echo ""
echo "1. Cloud SQL Proxy Status"
kubectl logs $POD -c cloud-sql-proxy -n $NAMESPACE | tail -10

echo ""
echo "2. Database Connection Variables"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- env | grep DB_

echo ""
echo "3. Cloud SQL Proxy Connectivity"
kubectl exec $POD -c cloud-sql-proxy -n $NAMESPACE -- \
  nc -zv localhost 5432 && echo "CONNECTED" || echo "FAILED"

echo ""
echo "4. Application Datasource Status"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- \
  curl -s localhost:8080/actuator/health/liveness | jq .

echo ""
echo "5. Check Service Account Permissions"
echo "Service Account:"
kubectl get sa app-runtime -n $NAMESPACE -o jsonpath='{.metadata.annotations.iam\.gke\.io/gcp-service-account}'
echo ""

echo "6. Verify Workload Identity Binding"
GSA=$(kubectl get sa app-runtime -n $NAMESPACE -o jsonpath='{.metadata.annotations.iam\.gke\.io/gcp-service-account}')
gcloud iam service-accounts get-iam-policy $GSA | grep workloadIdentityUser
```

## Example 3: Pub/Sub Debugging

```bash
#!/bin/bash
# Debug Pub/Sub message processing issues

POD=$(kubectl get pods -n wtr-supplier-charges -o jsonpath='{.items[0].metadata.name}')

echo "=== Pub/Sub Debugging ==="

echo ""
echo "1. Subscription Status"
gcloud pubsub subscriptions describe supplier-charges-incoming-sub \
  --project=ecp-wtr-supplier-charges-labs

echo ""
echo "2. Application Logs (Pub/Sub activity)"
kubectl logs $POD -c supplier-charges-hub-container \
  -n wtr-supplier-charges | grep -i pubsub | tail -20

echo ""
echo "3. Test Pub/Sub Connectivity"
kubectl exec $POD -n wtr-supplier-charges -- \
  gcloud pubsub topics list --project=ecp-wtr-supplier-charges-labs

echo ""
echo "4. Publish Test Message"
gcloud pubsub topics publish supplier-charges-incoming \
  --project=ecp-wtr-supplier-charges-labs \
  --message='{"test":true}' \
  && echo "Message published" \
  || echo "Message publish failed"

echo ""
echo "5. Monitor Pod Logs for Message Processing"
echo "(Run in another terminal:)"
echo "kubectl logs -f $POD -c supplier-charges-hub-container -n wtr-supplier-charges"
```
