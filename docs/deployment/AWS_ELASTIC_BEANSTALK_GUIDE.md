# AWS Elastic Beanstalk Deployment Guide
## Fine-Tuned BERT Model for ATS Resume Scorer

This guide walks you through deploying your fine-tuned BERT model to AWS Elastic Beanstalk.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Setup AWS CLI & EB CLI](#setup-aws-cli--eb-cli)
4. [Prepare Your Model](#prepare-your-model)
5. [Deploy to Elastic Beanstalk](#deploy-to-elastic-beanstalk)
6. [Configure Environment](#configure-environment)
7. [Testing the Deployment](#testing-the-deployment)
8. [Monitoring & Scaling](#monitoring--scaling)
9. [Cost Optimization](#cost-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- AWS Account with appropriate permissions
- Fine-tuned BERT model files
- Python 3.10+
- AWS CLI installed
- EB CLI installed

### AWS Permissions Needed
- AWSElasticBeanstalkFullAccess
- IAMFullAccess (for creating service roles)
- AmazonS3FullAccess (for storing application versions)
- CloudWatchLogsFullAccess (for logging)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Load Balancer               │
│                    (Auto-scaling enabled)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│  EC2 Instance  │       │  EC2 Instance  │
│   (t3.large)   │       │   (t3.large)   │
│                │       │                │
│  Flask API     │       │  Flask API     │
│  BERT Model    │       │  BERT Model    │
└────────────────┘       └────────────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │    CloudWatch Logs      │
        │    (Monitoring)         │
        └─────────────────────────┘
```

---

## Setup AWS CLI & EB CLI

### 1. Install AWS CLI

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download from: https://aws.amazon.com/cli/
```

### 2. Configure AWS CLI

```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format: `json`

### 3. Install EB CLI

```bash
pip install awsebcli --upgrade
```

Verify installation:
```bash
eb --version
```

---

## Prepare Your Model

### 1. Organize Model Files

```bash
# Your model directory structure should look like:
models/finetuned-bert/
├── config.json
├── pytorch_model.bin
├── tokenizer_config.json
├── vocab.txt
└── special_tokens_map.json
```

### 2. Compress Model (if large)

```bash
cd models
tar -czf finetuned-bert.tar.gz finetuned-bert/
```

### 3. Upload to S3 (Recommended for large models)

```bash
# Create S3 bucket
aws s3 mb s3://your-model-bucket-name

# Upload model
aws s3 cp finetuned-bert.tar.gz s3://your-model-bucket-name/models/

# Make it accessible
aws s3api put-object-acl --bucket your-model-bucket-name --key models/finetuned-bert.tar.gz --acl private
```

### 4. Update Model Loading Script

If using S3, add download logic to `deployment/model_api.py`:

```python
import boto3

def download_model_from_s3():
    s3 = boto3.client('s3')
    bucket = 'your-model-bucket-name'
    key = 'models/finetuned-bert.tar.gz'
    local_path = '/tmp/model.tar.gz'
    
    s3.download_file(bucket, key, local_path)
    
    # Extract
    import tarfile
    with tarfile.open(local_path, 'r:gz') as tar:
        tar.extractall('/var/app/current/models/')
```

---

## Deploy to Elastic Beanstalk

### 1. Initialize EB Application

```bash
cd deployment
eb init
```

Follow prompts:
- Select region (e.g., `us-east-1`)
- Application name: `ats-bert-model-api`
- Platform: `Python 3.11`
- Use CodeCommit: `No`
- Setup SSH: `Yes` (recommended)

### 2. Create Environment

```bash
eb create ats-bert-prod \
  --instance-type t3.large \
  --envvars MODEL_PATH=/var/app/current/models/finetuned-bert,TRANSFORMERS_CACHE=/tmp/transformers_cache \
  --scale 2
```

Options explained:
- `ats-bert-prod`: Environment name
- `--instance-type t3.large`: Instance type (2 vCPU, 8GB RAM)
- `--envvars`: Environment variables
- `--scale 2`: Start with 2 instances

### 3. Deploy Application

```bash
# First deployment
eb deploy

# Check status
eb status

# View logs
eb logs
```

---

## Configure Environment

### 1. Set Environment Variables

```bash
eb setenv \
  MODEL_PATH=/var/app/current/models/finetuned-bert \
  TRANSFORMERS_CACHE=/tmp/transformers_cache \
  HF_HOME=/tmp/huggingface \
  FLASK_ENV=production \
  LOG_LEVEL=INFO
```

### 2. Configure Auto-Scaling

```bash
# Edit .ebextensions/03_instance_config.config
# Then deploy:
eb deploy
```

Or via console:
1. Go to AWS Console → Elastic Beanstalk
2. Select your environment
3. Configuration → Capacity
4. Set:
   - Min instances: 1
   - Max instances: 4
   - Scaling trigger: CPU > 70%

### 3. Configure Load Balancer

```bash
# Health check settings
eb config

# Or via console:
# Configuration → Load Balancer → Processes
# Health check path: /health
# Timeout: 30 seconds
# Interval: 60 seconds
```

---

## Testing the Deployment

### 1. Get Environment URL

```bash
eb status
```

Look for: `CNAME: ats-bert-prod.us-east-1.elasticbeanstalk.com`

### 2. Test Health Endpoint

```bash
curl https://ats-bert-prod.us-east-1.elasticbeanstalk.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### 3. Test Prediction Endpoint

```bash
curl -X POST https://ats-bert-prod.us-east-1.elasticbeanstalk.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Experienced software engineer with 5 years in Python and machine learning...",
    "max_length": 512
  }'
```

Expected response:
```json
{
  "score": 75,
  "confidence": 0.92,
  "label": "good",
  "class": 2
}
```

### 4. Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 -p test_payload.json -T application/json \
  https://ats-bert-prod.us-east-1.elasticbeanstalk.com/predict
```

---

## Monitoring & Scaling

### 1. CloudWatch Metrics

Key metrics to monitor:
- CPU Utilization
- Memory Usage
- Request Count
- Response Time
- Error Rate

Access via:
```bash
eb console
# Navigate to: Monitoring
```

### 2. Set Up Alarms

```bash
# Create CloudWatch alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name ats-bert-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ElasticBeanstalk \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### 3. View Logs

```bash
# Tail logs in real-time
eb logs --stream

# Download all logs
eb logs --all
```

---

## Cost Optimization

### Estimated Monthly Costs

**Production Setup (2 x t3.large instances):**
- EC2 Instances: ~$120/month
- Load Balancer: ~$20/month
- Data Transfer: ~$10/month
- **Total: ~$150/month**

### Cost Reduction Strategies

1. **Use Spot Instances** (50-70% savings)
   ```bash
   # In .ebextensions/03_instance_config.config
   aws:ec2:instances:
     EnableSpot: true
     SpotMaxPrice: 0.05
   ```

2. **Auto-scaling Schedule**
   - Scale down during off-hours
   - Use time-based scaling

3. **Use Smaller Instances for Dev**
   ```bash
   eb create ats-bert-dev --instance-type t3.medium --single
   ```

4. **Enable Compression**
   - Reduces data transfer costs

5. **Use Reserved Instances** (for production)
   - 1-year commitment: 30% savings
   - 3-year commitment: 50% savings

---

## Troubleshooting

### Common Issues

#### 1. Model Loading Timeout

**Symptom:** Health checks fail, 503 errors

**Solution:**
```bash
# Increase timeout in .ebextensions/03_instance_config.config
aws:elasticbeanstalk:environment:process:default:
  HealthCheckTimeout: 60
  HealthCheckInterval: 120
```

#### 2. Out of Memory

**Symptom:** Instance crashes, OOM errors in logs

**Solution:**
- Upgrade to larger instance (t3.xlarge)
- Reduce batch size
- Enable model quantization

#### 3. Slow Predictions

**Symptom:** High response times

**Solution:**
- Use GPU instances (p3.2xlarge)
- Implement model caching
- Use ONNX runtime for faster inference

#### 4. Deployment Fails

**Symptom:** `eb deploy` fails

**Solution:**
```bash
# Check logs
eb logs

# Common fixes:
# - Verify requirements.txt
# - Check .ebextensions syntax
# - Ensure model files are included
```

### Debug Commands

```bash
# SSH into instance
eb ssh

# Check running processes
ps aux | grep gunicorn

# Check disk space
df -h

# Check memory
free -m

# View application logs
tail -f /var/log/eb-engine.log
tail -f /var/log/web.stdout.log
```

---

## Integration with Main App

### Update Main Application

In your main Streamlit app, add API client:

```python
# app/ai/bert_client.py
import requests
import os

BERT_API_URL = os.getenv('BERT_API_URL', 'http://localhost:8080')

def get_bert_score(resume_text: str) -> dict:
    """Get BERT model score from API."""
    try:
        response = requests.post(
            f"{BERT_API_URL}/predict",
            json={"text": resume_text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"BERT API error: {e}")
        return {"score": 0, "confidence": 0, "label": "unknown"}
```

### Environment Variable

```bash
# In your .env file
BERT_API_URL=https://ats-bert-prod.us-east-1.elasticbeanstalk.com
```

---

## Next Steps

1. ✅ Set up AWS account and credentials
2. ✅ Prepare and test model locally
3. ✅ Deploy to Elastic Beanstalk
4. ✅ Configure monitoring and alarms
5. ✅ Load test the API
6. ✅ Integrate with main application
7. ✅ Set up CI/CD pipeline (optional)
8. ✅ Configure custom domain (optional)

---

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Deploying ML Models on AWS](https://aws.amazon.com/machine-learning/deploy/)
- [Cost Calculator](https://calculator.aws/)

---

## Support

For issues or questions:
- Check AWS CloudWatch logs
- Review EB environment health dashboard
- Consult AWS Support (if you have a support plan)

