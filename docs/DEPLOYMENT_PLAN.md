# Deployment Plan

Environments
- `dev` — for local development and quick iteration
- `staging` — production-like testing
- `prod` — customer-facing

Infrastructure (v1)
- Containers (Docker) for services
- Kubernetes (GKE/EKS/AKS) or managed compute for production
- Managed vector DB recommended for v1 speed-to-market
- Object storage: S3 or S3-compatible
- Relational DB: Postgres

CI/CD
- GitHub Actions pipeline: build images, run tests, deploy to staging, promote to prod

Secrets & config
- Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Environment-based feature flags for staged rollouts
