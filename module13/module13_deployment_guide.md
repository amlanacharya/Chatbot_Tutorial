# Chatbot Deployment Guide

This guide provides step-by-step instructions for deploying your chatbot to various environments.

## Local Deployment

### Running Directly

1. Install dependencies:
   ```bash
   pip install -r module13_requirements.txt
   ```

2. Run the application:
   ```bash
   python module13.py --run
   ```

3. Access the API at http://localhost:5000/chat

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t chatbot-app .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 -p 8000:8000 -e GROQ_API_KEY=your_api_key chatbot-app
   ```

### Using Docker Compose

1. Create a `.env` file with your environment variables:
   ```
   GROQ_API_KEY=your_api_key
   GRAFANA_ADMIN_USER=admin
   GRAFANA_ADMIN_PASSWORD=secure_password
   ```

2. Start all services:
   ```bash
   docker-compose up -d
   ```

3. Access the services:
   - Chatbot API: http://localhost:5000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

## Cloud Deployment

### AWS Deployment

#### Using Elastic Beanstalk

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB application:
   ```bash
   eb init -p python-3.9 chatbot-app
   ```

3. Create an environment:
   ```bash
   eb create chatbot-production
   ```

4. Set environment variables:
   ```bash
   eb setenv GROQ_API_KEY=your_api_key
   ```

5. Deploy:
   ```bash
   eb deploy
   ```

#### Using ECS with Docker

1. Create an ECR repository:
   ```bash
   aws ecr create-repository --repository-name chatbot-app
   ```

2. Authenticate Docker to ECR:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin your-account-id.dkr.ecr.region.amazonaws.com
   ```

3. Tag and push your image:
   ```bash
   docker tag chatbot-app:latest your-account-id.dkr.ecr.region.amazonaws.com/chatbot-app:latest
   docker push your-account-id.dkr.ecr.region.amazonaws.com/chatbot-app:latest
   ```

4. Create an ECS cluster, task definition, and service using the AWS console or CLI.

### Azure Deployment

#### Using Azure Container Instances

1. Create a resource group:
   ```bash
   az group create --name chatbot-resources --location eastus
   ```

2. Create a container registry:
   ```bash
   az acr create --resource-group chatbot-resources --name chatbotregistry --sku Basic
   ```

3. Log in to the registry:
   ```bash
   az acr login --name chatbotregistry
   ```

4. Tag and push your image:
   ```bash
   docker tag chatbot-app:latest chatbotregistry.azurecr.io/chatbot-app:latest
   docker push chatbotregistry.azurecr.io/chatbot-app:latest
   ```

5. Create a container instance:
   ```bash
   az container create --resource-group chatbot-resources --name chatbot-container --image chatbotregistry.azurecr.io/chatbot-app:latest --dns-name-label chatbot-app --ports 5000 --environment-variables GROQ_API_KEY=your_api_key
   ```

### Google Cloud Platform

#### Using Cloud Run

1. Build and push your image to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/chatbot-app
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy chatbot-service --image gcr.io/your-project-id/chatbot-app --platform managed --allow-unauthenticated --set-env-vars GROQ_API_KEY=your_api_key
   ```

## Monitoring Setup

### Setting Up Alerts in Prometheus

1. Add alert rules to `prometheus.yml`:
   ```yaml
   rule_files:
     - 'alerts.yml'
   ```

2. Create `alerts.yml`:
   ```yaml
   groups:
   - name: chatbot_alerts
     rules:
     - alert: HighErrorRate
       expr: rate(chatbot_requests_total{status="error"}[5m]) > 0.1
       for: 2m
       labels:
         severity: critical
       annotations:
         summary: "High error rate detected"
         description: "Error rate is above 10% for more than 2 minutes."
   ```

### Setting Up Grafana Dashboard

1. Log in to Grafana (default: admin/admin)
2. Add Prometheus as a data source
3. Import the provided dashboard JSON or create a new one with panels for:
   - Request rate
   - Error rate
   - Response time
   - Resource usage

## Scaling Strategies

### Horizontal Scaling

For containerized deployments, increase the number of replicas:

```bash
# Kubernetes
kubectl scale deployment chatbot-deployment --replicas=5

# Docker Compose
docker-compose up -d --scale chatbot-api=5
```

### Load Balancing

Ensure your load balancer is configured to distribute traffic evenly and perform health checks.

### Caching

Implement Redis caching as shown in the docker-compose.yml file to reduce API calls and improve response times.

## Security Considerations

1. **API Keys**: Never hardcode API keys. Use environment variables or secret management services.

2. **Network Security**: Use HTTPS and consider implementing API authentication.

3. **Container Security**: Run containers as non-root users and scan images for vulnerabilities.

4. **Rate Limiting**: Implement rate limiting to prevent abuse.

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check logs: `docker logs container_id`
   - Verify environment variables are set correctly
   - Ensure ports are not already in use

2. **High latency**:
   - Check network connectivity
   - Monitor resource usage
   - Consider scaling up or out

3. **Memory issues**:
   - Adjust container memory limits
   - Check for memory leaks
   - Implement proper garbage collection

## Maintenance

### Updates and Rollbacks

1. **Rolling updates**:
   ```bash
   # Kubernetes
   kubectl set image deployment/chatbot-deployment chatbot-container=new-image:tag

   # Docker Compose
   docker-compose up -d --no-deps chatbot-api
   ```

2. **Rollbacks**:
   ```bash
   # Kubernetes
   kubectl rollout undo deployment/chatbot-deployment

   # Docker Compose
   docker-compose up -d --no-deps chatbot-api:previous-tag
   ```

### Backup Strategies

1. **Database backups**: Schedule regular backups of any persistent data
2. **Configuration backups**: Version control your configuration files
3. **Image versioning**: Tag and store previous versions of your container images
