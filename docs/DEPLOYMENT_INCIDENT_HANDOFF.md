# Healthify AI Deployment Incident and Handoff

## 1. Purpose

This document records the complete deployment journey for Healthify AI from the initial half-complete state through the AWS EKS prototype, including failures, root causes, changes, commands, validation results, and remaining risks.

The target architecture was:

```text
GitHub Push
    |
    v
GitHub Actions
    |
    v
Docker Build -> Amazon ECR
    |
    v
Argo CD GitOps
    |
    v
Amazon EKS
    |
    +-- ALB -> Frontend
    +-- Gateway -> Auth Service
    +-- Gateway -> Report Service -> PostgreSQL and S3
    +-- Gateway -> AI Service -> Ollama -> llama3.2:1b
```

## 2. Initial State

The project contained the application services and AWS/Kubernetes documentation, but the deployment path was inconsistent:

- `k8s-live/healthify.yaml` used hard-coded ECR images.
- `k8s-live/pos.yaml` used a different PostgreSQL image, database name, and password.
- The Helm values used placeholder image repositories such as `your-registry/...`.
- The Argo CD file defined several separate Applications that all targeted the same namespace and could prune each other's resources.
- No GitHub Actions workflow existed in the repository.
- Report Service required static AWS access keys during Python module import.
- AI Service was missing `python-multipart`, required by FastAPI file uploads.
- The local Docker Compose stack did not represent the complete seven-service production topology.

## 3. AWS Environment Discovered

Verified AWS environment:

```text
Account:       124502390077
Region:        ap-south-1
EKS cluster:   eswar
Nodes:         4 worker nodes
Kubernetes:    v1.34.10
ECR repositories:
  healthify-auth
  healthify-report
  healthify-ai
  healthify-gateway
  healthify-frontend
```

The AWS Load Balancer Controller was installed and running. A public ALB already existed for the `aihealth` namespace.

Public prototype URL:

```text
http://k8s-aihealth-healthif-cdfae1a745-1238636594.ap-south-1.elb.amazonaws.com
```

## 4. First Kubernetes Failures

The initial live state showed:

```text
auth-service       CrashLoopBackOff
report-service     CrashLoopBackOff
ai-service         CrashLoopBackOff
postgres           Pending
report-service     Pending replica
healthify-alb      ALB address available
```

### 4.1 PostgreSQL URL failure

The running secret contained:

```text
postgresql://postgres:HealthifyDB@2026@postgres:5432/healthai
```

The password contained `@` but was not URL encoded. PostgreSQL parsed `2026@postgres` as part of the hostname.

Observed error:

```text
could not translate host name "2026@postgres" to address
```

The corrected value became:

```text
postgresql://postgres:HealthifyDB%402026@postgres:5432/healthai
```

### 4.2 Report Service static credential failure

Report Service exited during import when `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` were absent.

The service was changed to use the standard boto3 credential chain. This supports:

- Local AWS profiles.
- Environment credentials.
- EKS Pod Identity.

Static AWS keys are no longer required inside the image or Kubernetes Secret.

### 4.3 AI multipart dependency failure

AI Service failed at startup with:

```text
Form data requires "python-multipart" to be installed.
```

The dependency was added:

```text
python-multipart==0.0.20
```

### 4.4 Invalid AI Dockerfile

The AI Dockerfile started with stray shell text:

```text
Get-Content .env.exampleFROM python:3.11
```

It was corrected to:

```dockerfile
FROM python:3.11
```

## 5. GitHub Actions, ECR, and Argo CD Changes

### 5.1 GitHub Actions

Added:

```text
.github/workflows/build-push-deploy.yml
```

The workflow:

1. Checks out the repository.
2. Assumes an AWS role using GitHub OIDC.
3. Logs in to ECR.
4. Builds five images.
5. Pushes images using the Git commit SHA.
6. Updates `k8s-live/kustomization.yaml`.
7. Pushes the GitOps tag update back to GitHub.

Images:

```text
healthify-auth
healthify-report
healthify-ai
healthify-gateway
healthify-frontend
```

### 5.2 AWS GitHub OIDC

Created the GitHub OIDC provider and role:

```text
HealthifyGitHubActionsRole
```

The role is restricted to the `master` branch of:

```text
KaleeswarG25/healthify_AI
```

The role can push only to the Healthify ECR repositories.

### 5.3 Argo CD

The original five competing Argo Applications were replaced by one authoritative Application:

```text
Application: aihealth
Source path: k8s-live
Namespace: aihealth
Sync: automated
Prune: enabled
Self-heal: enabled
```

This prevents multiple Applications from pruning each other's resources.

## 6. S3 and IAM Configuration

The Report Service uses:

```text
EKS Pod Identity -> HealthifyReportS3Role -> private S3 bucket
```

Created AWS resources:

```text
HealthifyS3Policy
HealthifyReportS3Role
EKS Pod Identity association:
  namespace: aihealth
  service account: report-service
```

The policy permits only:

```text
s3:GetObject
s3:PutObject
s3:DeleteObject
s3:ListBucket
```

The target bucket is:

```text
healthify-ai-reports-124502390077
```

Public access block was verified as enabled.

## 7. S3 CORS Failure

The frontend uploads directly to a presigned S3 URL using browser JavaScript. The browser sends an `OPTIONS` preflight before the `PUT` request.

Initial error:

```text
NoSuchCORSConfiguration
Access-Control-Allow-Origin header missing
```

Added:

```text
infrastructure/aws/s3-cors.json
```

Allowed origins:

```text
http://k8s-aihealth-healthif-cdfae1a745-1238636594.ap-south-1.elb.amazonaws.com
http://localhost:3000
http://localhost:80
```

Allowed methods:

```text
GET
PUT
HEAD
```

Verified preflight result:

```text
HTTP 200
Access-Control-Allow-Origin: ALB origin
Access-Control-Allow-Methods: GET, PUT, HEAD
Access-Control-Allow-Headers: content-type
```

## 8. EKS Storage and Capacity Problems

### 8.1 Missing PostgreSQL PVC

PostgreSQL was initially Pending because the required PVC did not exist in the live namespace.

The authoritative `k8s-live/healthify.yaml` manifest now creates:

```text
postgres-pvc
```

### 8.2 EBS CSI IAM failure

The EBS CSI controller could not call:

```text
ec2:DescribeAvailabilityZones
```

Observed error:

```text
UnauthorizedOperation
```

Actions taken:

- Attached `AmazonEBSCSIDriverPolicy` to the node role as a recovery step.
- Created `AmazonEKS_EBS_CSI_DriverRole`.
- Added EKS OIDC trust.
- Added the role annotation to `ebs-csi-controller-sa`.
- Restarted the EBS CSI controller.

PostgreSQL eventually obtained:

```text
postgres-pvc: Bound
volume size: 10Gi
storage class: gp3
```

### 8.3 PostgreSQL `lost+found` failure

PostgreSQL failed on the fresh EBS filesystem:

```text
initdb: directory exists but is not empty
It contains a lost+found directory
```

The deployment was fixed with:

```yaml
env:
  - name: PGDATA
    value: /var/lib/postgresql/data/pgdata
```

PostgreSQL then initialized successfully and logged:

```text
database system is ready to accept connections
```

### 8.4 EKS pod capacity limit

Each node allowed 11 pods. The cluster had four nodes:

```text
4 nodes x 11 pods = 44 pod capacity
```

The account also hit an EC2 vCPU quota:

```text
VcpuLimitExceeded
current vCPU limit: 8
```

The EKS node group became `DEGRADED` while trying to launch additional nodes.

Temporary capacity actions included pausing and restoring workloads as needed:

- Monitoring control-plane pods.
- CloudCart frontend replicas.
- Argo CD server and repository replicas.
- Duplicate EBS CSI controller replicas.

Stale terminating pods were also force-removed when they held scheduler slots.

The permanent fix is to request a higher EC2 vCPU quota and add worker capacity.

## 9. 504 Gateway Timeout Failure

The AI PDF endpoint returned:

```text
504 Gateway Time-out
```

The request path was:

```text
ALB -> Gateway -> AI Service -> Ollama
```

Initial changes:

- AI Ollama request timeout: 300 seconds.
- Gateway Nginx upstream timeout: 300 seconds.
- ALB idle timeout: 360 seconds.

The ALB attribute was verified:

```text
idle_timeout.timeout_seconds = 360
```

However, the deeper problem was that Gateway and AI EndpointSlices pointed only to terminating pods:

```text
ready: false
terminating: true
```

The replacement pods were Pending because the cluster had no free pod slots. After stale pod cleanup and capacity management, Gateway and AI had healthy endpoints again.

The public upload URL endpoint then returned:

```text
HTTP 200
```

## 10. 503 AI Inference Failure

The final AI error was:

```text
503 Service Unavailable
AI inference is temporarily unavailable
```

The AI pod and Ollama pod were both marked Running, but Ollama logs showed:

```text
models=0
POST /api/generate 404
```

The actual root cause was that the Ollama model was missing after the pod had been recreated. The model was restored with:

```powershell
kubectl exec -n aihealth deploy/ollama -- ollama pull llama3.2:1b
```

The AI service was also changed to return a real `503` when Ollama fails instead of storing an error message as a successful analysis.

The AI runtime limits are:

```text
OLLAMA_NUM_CTX=4096
OLLAMA_NUM_PREDICT=256
```

These limits reduce the likelihood of Ollama being killed while loading the 1.3 GiB model on the small worker nodes.

## 11. Ollama Persistence Attempt

A persistent Ollama PVC was attempted so the model would survive pod restarts.

The dynamic PVC became stuck because:

- A worker node became `NotReady`.
- EBS CSI attachment remained `Attached: false`.
- The cluster was at its pod limit.

A static EBS volume was created in `ap-south-1b` and temporarily bound through a static PV, but the CSI attachment remained stuck. The active deployment was returned to an unblocked filesystem so the AI service could recover immediately.

Current operational implication:

```text
The Ollama model must be pulled again if the Ollama pod is recreated.
```

Permanent solution:

1. Increase EKS worker capacity and EC2 vCPU quota.
2. Repair EBS CSI/node health.
3. Re-enable an EBS-backed Ollama PVC.
4. Pull `llama3.2:1b` into the persistent mount.
5. Add a readiness check that verifies the model exists.

## 12. Final Verified Health Checks

At the successful recovery point, these pods were Running:

```text
ai-service       1/1 Running
auth-service     1/1 Running
frontend         1/1 Running
gateway          1/1 Running
ollama           1/1 Running
postgres         1/1 Running
report-service   1/1 Running
```

Internal endpoint checks returned:

```text
Auth:   {"status":"healthy"}
Report: {"status":"healthy"}
AI:     {"status":"healthy","service":"ai-service"}
```

Public presigned URL check returned:

```text
HTTP 200
```

The ALB was:

```text
http://k8s-aihealth-healthif-cdfae1a745-1238636594.ap-south-1.elb.amazonaws.com
```

## 13. Current Important Files

```text
.github/workflows/build-push-deploy.yml
infrastructure/aws/healthify-s3-policy.json
infrastructure/aws/healthify-pod-trust.json
infrastructure/aws/github-actions-trust.json
infrastructure/aws/github-actions-policy.json
infrastructure/aws/s3-cors.json
k8s-live/healthify.yaml
k8s-live/kustomization.yaml
services/ai-service/Dockerfile
services/ai-service/app/ai_engine.py
services/ai-service/requirements.txt
services/report-service/app/s3.py
infrastructure/argocd/applications.yaml
```

## 14. Recommended Production Follow-up

### Required

- Request an EC2 vCPU quota increase above the current limit of 8.
- Add at least one more EKS worker or use larger nodes.
- Repair the `NotReady` worker node.
- Restore EBS CSI controller redundancy after capacity is available.
- Re-enable persistent Ollama storage.
- Commit and push all repository changes so Argo CD owns the final state.

### Recommended

- Use immutable image tags instead of `latest` for Kubernetes deployments.
- Add Kubernetes readiness and liveness probes to Auth, Report, AI, Gateway, and Ollama.
- Add an Ollama model readiness check that verifies `llama3.2:1b` exists.
- Add a startup job that pulls the model only when the persistent model directory is empty.
- Use AWS Secrets Manager or External Secrets for production secrets.
- Use RDS PostgreSQL instead of a single-pod PostgreSQL deployment for production durability.
- Keep monitoring and Argo CD replicas separate from application capacity planning.
- Add an integration test that uploads a small PDF and verifies the complete flow:

```text
Browser -> ALB -> Gateway -> Report -> S3 PUT -> AI -> Ollama
```

## 15. Recovery Commands

Check the full platform:

```powershell
kubectl get pods -n aihealth -o wide
kubectl get svc -n aihealth
kubectl get endpoints -n aihealth
kubectl get ingress -n aihealth
kubectl get pvc -n aihealth
```

Check AI model:

```powershell
kubectl exec -n aihealth deploy/ollama -- ollama list
kubectl exec -n aihealth deploy/ollama -- ollama pull llama3.2:1b
```

Check service health:

```powershell
kubectl exec -n aihealth deploy/auth-service -- python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
kubectl exec -n aihealth deploy/report-service -- python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8001/health').read().decode())"
kubectl exec -n aihealth deploy/ai-service -- python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8002/health').read().decode())"
```

Check the public presigned URL endpoint:

```powershell
$base='http://k8s-aihealth-healthif-cdfae1a745-1238636594.ap-south-1.elb.amazonaws.com/api/generate-upload-url'
$uri=$base+'?file_name=test.pdf&content_type=application%2Fpdf&user_id=1'
Invoke-WebRequest -Uri $uri -UseBasicParsing
```

## 16. Final Status Summary

```text
GitHub Actions workflow:       Added
ECR repositories:              Available
EKS cluster access:            Working
ALB:                           Created
Frontend:                      Working prototype
Auth Service:                  Working when PostgreSQL is Ready
Report Service:                Working with Pod Identity and S3
S3 CORS:                      Configured and preflight verified
AI Service:                    Running with bounded inference settings
Ollama model:                  Restored manually; persistence still pending
PostgreSQL:                    Working with EBS PVC and PGDATA fix
Argo CD:                       Configuration prepared; final Git push required
Cluster capacity:              Insufficient for all workloads permanently
```
