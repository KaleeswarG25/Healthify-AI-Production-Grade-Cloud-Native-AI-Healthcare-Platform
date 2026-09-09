# Healthify AI

### Production-Oriented Cloud-Native AI Healthcare Platform

Healthify AI is a cloud-native healthcare platform that allows users to securely manage medical reports and receive AI-assisted analysis.

The project is designed as a production-oriented DevOps/Cloud/DevSecOps portfolio project, combining **microservices, Docker, Kubernetes, AWS, Terraform, Helm, GitHub Actions, security scanning, and GitOps with Argo CD**.

> **Project status:** Production-oriented portfolio implementation. The repository contains the application, infrastructure-as-code, Kubernetes/Helm configuration, CI/CD workflows, and Argo CD GitOps configuration. Actual production operation depends on the target AWS environment and its configuration.

---

## 🚀 What This Project Demonstrates

This project demonstrates an end-to-end cloud-native delivery workflow:

```text
Developer
    │
    ▼
GitHub
    │
    ▼
Pull Request
    │
    ▼
GitHub Actions CI
    │
    ├── Python validation
    ├── Frontend build
    ├── Helm lint
    │
    ▼
Merge to master
    │
    ▼
GitHub Actions CD
    │
    ├── Build Docker images
    ├── Push images to Amazon ECR
    │
    ▼
GitOps Commit
    │
    ▼
Argo CD
    │
    ▼
Amazon EKS
    │
    ▼
Healthify AI Platform
```

---

# ✨ Features

### 🔐 Authentication & Security

* JWT-based authentication
* Password hashing
* Role-aware authorization
* User identity derived from authenticated tokens
* Kubernetes ServiceAccounts
* Disabled automatic ServiceAccount token mounting where appropriate
* Kubernetes NetworkPolicies
* Non-root application containers
* AWS IAM-based workload access
* GitHub Actions AWS OIDC authentication
* No application secrets committed to Git
* Trivy filesystem and container image scanning

### 📄 Medical Report Management

* Upload medical PDF reports
* Extract report information
* Store report metadata
* User-specific report access
* Secure object storage using Amazon S3
* S3 access controlled through IAM

### 🤖 AI-Assisted Analysis

* AI-powered medical report analysis
* PDF text extraction
* Ollama-based local/self-hosted LLM integration
* Context-aware report analysis
* Report-related question answering
* Configurable model and inference parameters
* Medical-information disclaimer in AI responses

> **Important:** AI-generated output is informational and is not a substitute for professional medical diagnosis or treatment.

### ☁️ Cloud Infrastructure

* Amazon VPC
* Amazon EKS
* Amazon ECR
* Amazon RDS PostgreSQL
* Amazon S3
* AWS IAM
* AWS EBS CSI
* AWS Load Balancer Controller integration
* Infrastructure provisioned using Terraform

### ☸️ Kubernetes

* Deployments
* Services
* Ingress
* ServiceAccounts
* ConfigMaps
* Secrets
* Horizontal Pod Autoscaling
* Pod Disruption Budgets
* NetworkPolicies
* PersistentVolumeClaims
* Resource requests and limits
* Helm-based deployments

### 🔄 GitOps

* Argo CD
* Declarative Kubernetes configuration
* Git as the deployment source of truth
* Automated synchronization
* Automated pruning
* Self-healing configuration
* Immutable Git SHA image promotion

---

# 🏗️ Architecture

## High-Level Architecture

```text
                         Internet
                            │
                            ▼
                   AWS Application Load
                      Balancer (ALB)
                            │
                            ▼
                    Kubernetes Ingress
                            │
                            ▼
                     NGINX Gateway
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Frontend          Auth Service      Report Service
     React/NGINX          FastAPI            FastAPI
                                               │
                                               ▼
                                         Amazon S3
                                              
                            
                            
                       AI Service
                         FastAPI
                            │
                            ▼
                         Ollama
                            │
                            ▼
                       Local LLM

          ┌─────────────────────────────────────────┐
          │              Amazon EKS                 │
          │                                         │
          │  Frontend │ Gateway │ Auth │ Report │ AI│
          │                                         │
          │  Helm │ HPA │ PDB │ RBAC │ NetworkPolicy│
          └─────────────────────────────────────────┘
                            │
                            ▼
                    Amazon RDS PostgreSQL
```

---

# 🔧 Technology Stack

| Layer                  | Technologies                               |
| ---------------------- | ------------------------------------------ |
| Frontend               | React 18, Axios, React Router, React Icons |
| Backend                | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| Authentication         | JWT, password hashing                      |
| PDF Processing         | PyPDF2                                     |
| AI                     | Ollama, configurable LLM                   |
| Gateway                | NGINX                                      |
| Containers             | Docker, Docker Compose                     |
| Orchestration          | Kubernetes, Amazon EKS                     |
| Packaging              | Helm                                       |
| Infrastructure         | Terraform                                  |
| CI/CD                  | GitHub Actions                             |
| GitOps                 | Argo CD                                    |
| Container Registry     | Amazon ECR                                 |
| Database               | PostgreSQL / Amazon RDS                    |
| Object Storage         | Amazon S3                                  |
| Security               | Trivy, IAM, OIDC, NetworkPolicies          |
| Load Balancing         | AWS Application Load Balancer              |
| Storage                | AWS EBS CSI                                |
| Monitoring Integration | Prometheus / Grafana compatible            |

---

# 🧩 Microservices

```text
frontend/
    React application
         │
         ▼
gateway/
    NGINX reverse proxy
         │
         ├───────────────┐
         ▼               ▼
auth-service       report-service
    │                    │
    │                    ├── PostgreSQL
    │                    └── S3
    │
    ▼
authentication

ai-service
    │
    ├── PDF processing
    ├── report analysis
    └── Ollama
```

### Services

| Service  | Responsibility                |  Port |
| -------- | ----------------------------- | ----: |
| Frontend | Web application               |    80 |
| Gateway  | Reverse proxy / API routing   |    80 |
| Auth     | Authentication and users      |  8000 |
| Report   | Reports and S3 integration    |  8001 |
| AI       | AI analysis                   |  8002 |
| Ollama   | Local/self-hosted LLM runtime | 11434 |

---

# 📁 Repository Structure

```text
healthify_AI/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── frontend/
│   └── health-ai-frontend/
│
├── gateway/
│   ├── Dockerfile
│   └── nginx.conf
│
├── services/
│   ├── auth-service/
│   ├── report-service/
│   └── ai-service/
│
├── infrastructure/
│   │
│   ├── terraform/
│   │   ├── providers.tf
│   │   ├── variables.tf
│   │   ├── main.tf
│   │   ├── vpc.tf
│   │   ├── eks.tf
│   │   ├── addons.tf
│   │   ├── ecr.tf
│   │   ├── rds.tf
│   │   ├── s3.tf
│   │   ├── iam.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars.example
│   │
│   ├── kubernetes/
│   │   └── helm/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-staging.yaml
│   │       ├── values-prod.yaml
│   │       └── templates/
│   │
│   └── argocd/
│       ├── project.yaml
│       ├── application.yaml
│       └── README.md
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AWS_DEPLOYMENT.md
│   ├── CI_CD.md
│   ├── GITOPS.md
│   ├── KUBERNETES.md
│   ├── LOCAL_SETUP.md
│   ├── SECURITY.md
│   ├── TROUBLESHOOTING.md
│   └── screenshots/
│
├── scripts/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

# 🔄 CI/CD Pipeline

## Continuous Integration

Every pull request and manual CI run performs validation:

```text
Pull Request
     │
     ▼
Python Validation
     │
     ▼
Frontend Build
     │
     ▼
Helm Lint
     │
     ▼
Trivy Filesystem Scan
     │
     ▼
CI Result
```

The CI workflow validates:

* Python source compilation
* Frontend production build
* Helm chart syntax
* Repository security using Trivy

---

# 🚢 Continuous Delivery

After changes are merged into `master`:

```text
master
  │
  ▼
GitHub Actions
  │
  ├── Build frontend image
  ├── Build gateway image
  ├── Build auth image
  ├── Build report image
  └── Build AI image
          │
          ▼
      Trivy Scan
          │
          ▼
     Amazon ECR
          │
          ▼
GitOps Promotion
          │
          ▼
values-prod.yaml
          │
          ▼
       Argo CD
          │
          ▼
       Amazon EKS
```

Docker images are tagged with the Git commit SHA to provide immutable deployments.

Example:

```text
healthify-ai:<git-sha>
healthify-auth:<git-sha>
healthify-report:<git-sha>
healthify-gateway:<git-sha>
healthify-frontend:<git-sha>
```

---

# 🌱 GitOps

Argo CD continuously watches the Git repository.

```text
Git Repository
      │
      ▼
Helm Configuration
      │
      ▼
Argo CD
      │
      ├── Automated Sync
      ├── Self Heal
      └── Prune
      │
      ▼
Amazon EKS
```

The GitOps configuration is located at:

```text
infrastructure/argocd/
```

### Argo CD Application

The application points to:

```text
infrastructure/kubernetes/helm
```

and uses:

```text
values.yaml
values-prod.yaml
```

Argo CD is intentionally treated as a **cluster-level platform component**. The repository contains the Argo CD `AppProject` and `Application` definitions, but does not bundle the Argo CD installation itself.

---

# 🏭 Environments

The Helm chart supports separate configurations:

```text
values.yaml
      │
      ├── values-staging.yaml
      │
      └── values-prod.yaml
```

### Staging

Designed for lower-resource testing:

* Reduced replicas
* Ollama disabled
* Autoscaling disabled
* PDB disabled
* Ingress disabled

### Production

Configured for a more resilient deployment:

* Multiple application replicas
* HPA
* PDB
* ALB Ingress
* NetworkPolicies
* Resource limits
* Ollama configuration
* AWS integrations

---

# 🔐 Security Architecture

Security is integrated into the application and delivery pipeline.

```text
Developer
    │
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Trivy filesystem scan
    │
    ├── Docker image scan
    │
    └── AWS OIDC
    │
    ▼
Amazon ECR
    │
    ▼
Amazon EKS
    │
    ├── Non-root containers
    ├── ServiceAccounts
    ├── IAM workload permissions
    ├── NetworkPolicies
    ├── Resource limits
    └── Secrets management
```

### Security principles

* No hard-coded application credentials
* No AWS access keys in GitHub Actions
* GitHub Actions uses AWS OIDC
* IAM-based AWS access
* Least-privilege S3 access
* Kubernetes NetworkPolicies
* Non-root application containers
* Disabled ServiceAccount token automounting where appropriate
* Container image vulnerability scanning
* Filesystem vulnerability scanning
* Secrets supplied through environment-specific configuration

---

# ☁️ AWS Infrastructure

Terraform provisions the core AWS infrastructure.

```text
AWS
│
├── VPC
│   ├── Public Subnets
│   └── Private Subnets
│
├── EKS
│   ├── General Node Group
│   └── Optional GPU Workload
│
├── ECR
│   ├── Frontend
│   ├── Gateway
│   ├── Auth
│   ├── Report
│   └── AI
│
├── RDS PostgreSQL
│
├── S3
│
├── IAM
│
└── EBS CSI
```

Terraform configuration is located at:

```text
infrastructure/terraform/
```

---

# 🚀 Local Development

Clone the repository:

```bash
git clone https://github.com/KaleeswarG25/healthify_AI.git
cd healthify_AI
```

Create local environment configuration:

```bash
cp .env.example .env
```

Review the environment variables before starting the services.

Run the platform:

```bash
docker-compose up --build
```

Check running containers:

```bash
docker-compose ps
```

The frontend/gateway is exposed through the configured local ports in Docker Compose.

For detailed local setup:

```text
docs/LOCAL_SETUP.md
```

---

# ☸️ Kubernetes Deployment

The Kubernetes application is packaged as a Helm chart:

```text
infrastructure/kubernetes/helm/
```

Install Helm if it is not already available.

Validate the chart:

```bash
helm lint infrastructure/kubernetes/helm
```

Install the staging configuration:

```bash
helm upgrade --install healthify infrastructure/kubernetes/helm \
  -f infrastructure/kubernetes/helm/values-staging.yaml
```

For production-style configuration:

```bash
helm upgrade --install healthify infrastructure/kubernetes/helm \
  -f infrastructure/kubernetes/helm/values-prod.yaml
```

Check workloads:

```bash
kubectl get pods -n healthify
kubectl get svc -n healthify
kubectl get ingress -n healthify
kubectl get hpa -n healthify
```

Detailed Kubernetes documentation:

```text
docs/KUBERNETES.md
```

---

# 🔄 Argo CD Deployment

Install Argo CD separately on the target Kubernetes cluster using the official Argo CD installation process.

Then apply the project configuration:

```bash
kubectl apply -f infrastructure/argocd/project.yaml
kubectl apply -f infrastructure/argocd/application.yaml
```

Check the application:

```bash
kubectl get applications -n argocd
```

The Argo CD application is configured for:

```text
Repository:
https://github.com/KaleeswarG25/healthify_AI.git

Path:
infrastructure/kubernetes/helm

Namespace:
healthify
```

Detailed GitOps documentation:

```text
docs/GITOPS.md
```

---

# 🏗️ Terraform

Navigate to Terraform:

```bash
cd infrastructure/terraform
```

Create your variable file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Review and configure the values for your AWS environment.

Initialize Terraform:

```bash
terraform init
```

Format:

```bash
terraform fmt -recursive
```

Validate:

```bash
terraform validate
```

Review the infrastructure plan:

```bash
terraform plan
```

Apply only after reviewing the plan:

```bash
terraform apply
```

> Never commit `terraform.tfvars`, Terraform state files, credentials, or other sensitive environment-specific files.

---

# 📡 API Routes

The public API is routed through the NGINX gateway.

| Route                  | Service | Purpose                      |
| ---------------------- | ------- | ---------------------------- |
| `/api/auth/register`   | Auth    | User registration            |
| `/api/auth/login`      | Auth    | User authentication          |
| `/api/reports/...`     | Report  | Report management            |
| `/api/ai/analyze-text` | AI      | Analyze report text          |
| `/api/ai/analyze-pdf`  | AI      | Analyze PDF report           |
| `/api/ai/chat`         | AI      | Ask questions about analysis |

Backend services also expose health endpoints.

```text
/health
```

FastAPI services provide interactive API documentation when directly exposed in development environments.

---

# 📚 Documentation

Detailed documentation is available under `docs/`.

* [Architecture](docs/ARCHITECTURE.md)
* [Local Setup](docs/LOCAL_SETUP.md)
* [AWS Deployment](docs/AWS_DEPLOYMENT.md)
* [Kubernetes](docs/KUBERNETES.md)
* [CI/CD](docs/CI_CD.md)
* [GitOps / Argo CD](docs/GITOPS.md)
* [Security](docs/SECURITY.md)
* [Troubleshooting](docs/TROUBLESHOOTING.md)

---

# 🧪 Validation

Before creating a release, validate the main components.

### Python

```bash
python -m compileall services
```

### Frontend

```bash
cd frontend/health-ai-frontend
npm ci
npm run build
```

### Helm

```bash
helm lint infrastructure/kubernetes/helm
```

### Kubernetes

```bash
kubectl get nodes
kubectl get pods -n healthify
kubectl get svc -n healthify
kubectl get ingress -n healthify
```

### Argo CD

```bash
kubectl get applications -n argocd
```

---

# 🛠️ Troubleshooting

Check Kubernetes workloads:

```bash
kubectl get pods -n healthify
```

Check a specific pod:

```bash
kubectl describe pod <pod-name> -n healthify
```

View logs:

```bash
kubectl logs <pod-name> -n healthify
```

Check deployment:

```bash
kubectl get deployments -n healthify
```

Check events:

```bash
kubectl get events -n healthify --sort-by=.lastTimestamp
```

For common problems and recovery procedures:

```text
docs/TROUBLESHOOTING.md
```

---

# 🔁 Development Workflow

```text
Create Feature Branch
        │
        ▼
Develop Locally
        │
        ▼
Run Tests / Validation
        │
        ▼
Push Feature Branch
        │
        ▼
Create Pull Request
        │
        ▼
GitHub Actions CI
        │
        ▼
Code Review
        │
        ▼
Merge to master
        │
        ▼
GitHub Actions CD
        │
        ▼
ECR Image
        │
        ▼
GitOps Promotion
        │
        ▼
Argo CD
        │
        ▼
Amazon EKS
```

---

# 🎯 Engineering Highlights

This project focuses on demonstrating practical engineering concepts rather than only deploying an application.

### Cloud

* AWS networking
* EKS
* ECR
* RDS
* S3
* IAM
* Load balancing
* Persistent storage

### DevOps

* Docker
* Kubernetes
* Helm
* Terraform
* GitHub Actions
* Argo CD
* GitOps

### DevSecOps

* OIDC-based AWS authentication
* Trivy
* IAM least privilege
* Kubernetes NetworkPolicies
* Non-root containers
* Secret separation
* Immutable container image tags

### Reliability

* Multiple replicas
* HPA
* PDB
* Kubernetes health checks
* Resource requests/limits
* GitOps self-healing

---

# 🔮 Future Improvements

Possible future extensions include:

* Argo Rollouts for progressive delivery
* External Secrets Operator
* OpenTelemetry
* Loki-based centralized logging
* Prometheus/Grafana dashboards
* Kubernetes policy enforcement
* Dedicated GPU node pool for AI inference
* Automated disaster recovery
* Multi-AZ production hardening
* Automated integration and end-to-end testing

---

# ⚠️ Important Notes

This project processes medical-report data. It should be treated as a **technical demonstration and portfolio project**, not as a certified medical system.

AI output can be inaccurate and must not be treated as medical diagnosis.

AWS infrastructure can incur charges. Review Terraform plans and AWS resources before deployment.

Never commit:

```text
.env
terraform.tfvars
terraform.tfstate
AWS credentials
private keys
database passwords
JWT secrets
```

---

# 📄 License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Project

**Healthify AI**

Cloud-native AI healthcare platform demonstrating:

```text
AWS
+
Docker
+
Kubernetes
+
Terraform
+
Helm
+
GitHub Actions
+
Trivy
+
Argo CD
+
GitOps
```

Built as a hands-on cloud engineering and DevSecOps portfolio project.
