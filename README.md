# logpilot-infra — Infrastructure & DevOps

> **All Infrastructure as Code, Kubernetes manifests, CI/CD pipelines, monitoring stack, and deployment automation for the LogPilot platform.**

---

## 📋 Overview

| Property | Value |
|----------|-------|
| **Name** | `logpilot-infra` |
| **Technology** | Terraform, Kubernetes (EKS), Docker, GitHub Actions, Helm, Prometheus, Grafana |
| **Cloud Provider** | AWS (EKS, RDS, ElastiCache, S3, ALB, ECR, Route 53, CloudWatch) |
| **Team Owner** | DevOps/Cloud Engineer |
| **Build Priority** | Month 1, Week 1–2 — foundation for everything |

---

## 🎯 Responsibilities

1. **AWS Infrastructure** — Provision all cloud resources via Terraform
2. **Kubernetes Cluster** — EKS cluster setup, namespaces, RBAC
3. **Service Deployments** — K8s Deployment + Service + HPA manifests for all 8 services
4. **CI/CD Pipelines** — GitHub Actions workflows for build → test → deploy
5. **Docker** — Standardized Dockerfiles and docker-compose for local dev
6. **Monitoring** — Prometheus + Grafana stack for platform observability
7. **Secrets Management** — AWS Secrets Manager integration with K8s
8. **SSL/DNS** — Route 53 + ACM for domain and certificates
9. **Druid Cluster** — StatefulSet + ZooKeeper for Apache Druid

---

## 📦 Codebase Structure

```
logpilot-infra/
├── terraform/                                      # Infrastructure as Code
│   ├── main.tf                                     # Root module
│   ├── variables.tf                                # Input variables
│   ├── outputs.tf                                  # Output values
│   ├── provider.tf                                 # AWS provider config
│   ├── backend.tf                                  # S3 remote state backend
│   ├── modules/
│   │   ├── vpc/                                    # VPC, subnets, security groups
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── eks/                                    # EKS cluster + node groups
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── rds/                                    # PostgreSQL RDS instance
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── elasticache/                            # Redis cluster
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── s3/                                     # Druid deep storage, log archival
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   ├── ecr/                                    # Docker container registry
│   │   │   └── main.tf
│   │   ├── alb/                                    # Application Load Balancer
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   ├── route53/                                # DNS + SSL certificates
│   │   │   └── main.tf
│   │   └── secrets-manager/                        # Secret store
│   │       └── main.tf
│   └── environments/
│       ├── dev/
│       │   └── terraform.tfvars                    # Dev env variables
│       ├── staging/
│       │   └── terraform.tfvars                    # Staging env variables
│       └── prod/
│           └── terraform.tfvars                    # Production env variables
│
├── kubernetes/                                     # K8s manifests
│   ├── namespaces/
│   │   ├── logpilot-prod.yaml
│   │   └── logpilot-monitoring.yaml
│   ├── deployments/                                # One per service
│   │   ├── logpilot-collector.yaml
│   │   ├── logpilot-ingest.yaml
│   │   ├── logpilot-processor.yaml
│   │   ├── logpilot-ai-engine.yaml
│   │   ├── logpilot-alerting.yaml
│   │   ├── logpilot-gateway.yaml
│   │   ├── logpilot-query.yaml
│   │   └── logpilot-frontend.yaml
│   ├── services/                                   # K8s Service (ClusterIP/NodePort)
│   │   ├── logpilot-collector-svc.yaml
│   │   ├── logpilot-ingest-svc.yaml
│   │   ├── logpilot-processor-svc.yaml
│   │   ├── logpilot-ai-engine-svc.yaml
│   │   ├── logpilot-alerting-svc.yaml
│   │   ├── logpilot-gateway-svc.yaml
│   │   ├── logpilot-query-svc.yaml
│   │   └── logpilot-frontend-svc.yaml
│   ├── hpa/                                        # HorizontalPodAutoscaler
│   │   ├── logpilot-ingest-hpa.yaml                # Scale 2→20 on CPU
│   │   └── logpilot-processor-hpa.yaml
│   ├── configmaps/
│   │   └── logpilot-config.yaml                    # Shared env variables
│   ├── secrets/
│   │   └── logpilot-secrets.yaml                   # Encrypted credentials
│   ├── ingress/
│   │   └── alb-ingress.yaml                        # ALB Ingress Controller rules
│   ├── druid/                                      # Apache Druid cluster
│   │   ├── druid-statefulset.yaml
│   │   ├── druid-service.yaml
│   │   ├── zookeeper-statefulset.yaml
│   │   └── zookeeper-service.yaml
│   └── monitoring/
│       ├── prometheus/
│       │   ├── prometheus-deployment.yaml
│       │   ├── prometheus-config.yaml
│       │   └── prometheus-service.yaml
│       └── grafana/
│           ├── grafana-deployment.yaml
│           ├── grafana-dashboards/                  # Pre-built dashboards JSON
│           │   ├── platform-overview.json
│           │   ├── service-health.json
│           │   └── ingestion-pipeline.json
│           └── grafana-service.yaml
│
├── docker/                                          # Docker configs
│   ├── docker-compose.yml                           # Full local dev stack
│   ├── docker-compose.dev.yml                       # Dev overrides (hot-reload)
│   └── Dockerfile.spring-boot-template              # Standard Spring Boot Dockerfile
│
├── github-actions/                                  # CI/CD workflow templates
│   ├── build-and-deploy.yml                         # Main CI/CD pipeline
│   ├── test-only.yml                                # PR test pipeline
│   └── druid-deploy.yml                             # Druid-specific deployment
│
├── scripts/                                         # Utility scripts
│   ├── setup-cluster.sh                             # One-click EKS cluster setup
│   ├── deploy-all.sh                                # Deploy all services
│   ├── rollback.sh                                  # Rollback last deployment
│   ├── health-check.sh                              # Smoke test all endpoints
│   └── seed-data.sh                                 # Load sample data for testing
│
└── README.md
```

---

## 🔗 AWS Services & Estimated Cost (MVP)

| AWS Service | Purpose | Monthly Cost |
|-------------|---------|-------------|
| EKS (2× t3.medium) | Run all microservices | ~$150 |
| RDS PostgreSQL (db.t3.micro) | Production database | ~$50 |
| ElastiCache Redis (cache.t3.micro) | Stream buffer, cache | ~$30 |
| S3 | Druid deep storage, archival | ~$20 |
| ALB | Load balancer | ~$20 |
| CloudWatch | Infra monitoring | ~$15 |
| ECR | Docker image registry | ~$5 |
| Route 53 + ACM | DNS + SSL | ~$5 |
| **TOTAL** | | **~$295/month** |

---

## 🔄 CI/CD Pipeline Flow

```
Code Push to main
    │
    ├── 1. Run unit tests (mvn test / ng test)
    ├── 2. Build Docker image, tag with Git SHA
    ├── 3. Push image to Amazon ECR
    ├── 4. Run integration tests (test EKS namespace)
    ├── 5. Deploy to production EKS (kubectl rolling update)
    ├── 6. Post deployment status to Slack
    └── 7. Run smoke tests (health check endpoints)
```

---

## ✅ Setup Checklist

- [ ] AWS account created with IAM roles for Terraform
- [ ] S3 bucket for Terraform state + DynamoDB for locking
- [ ] `terraform init && terraform plan && terraform apply` for each environment
- [ ] EKS cluster reachable via `kubectl`
- [ ] All Docker images build and push to ECR
- [ ] GitHub Actions secrets configured (AWS creds, Docker creds)
- [ ] Druid cluster healthy with ZooKeeper
- [ ] Prometheus scraping all service metrics
- [ ] Grafana dashboards loaded and accessible
- [ ] ALB Ingress routing traffic correctly
- [ ] SSL certificate issued and attached
