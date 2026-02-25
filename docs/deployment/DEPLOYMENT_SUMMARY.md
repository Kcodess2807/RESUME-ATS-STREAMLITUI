# AWS Elastic Beanstalk Deployment - Quick Reference

## Files Created

```
.ebextensions/
├── 01_python.config          # Python environment configuration
├── 02_model_setup.config     # Model and dependencies setup
└── 03_instance_config.config # Instance and scaling configuration

deployment/
├── model_api.py              # Flask API for BERT model
├── requirements_model.txt    # Python dependencies for API
├── Procfile                  # Process configuration for EB
├── .ebignore                 # Files to ignore during deployment
└── deploy.sh                 # Quick deployment script

docs/deployment/
└── AWS_ELASTIC_BEANSTALK_GUIDE.md  # Complete deployment guide
```

## Quick Start

### 1. Prerequisites
```bash
# Install AWS CLI
pip install awscli awsebcli

# Configure AWS credentials
aws configure
```

### 2. Prepare Model
```bash
# Ensure your model is in models/finetuned-bert/
ls models/finetuned-bert/
# Should contain: config.json, pytorch_model.bin, tokenizer files
```

### 3. Deploy
```bash
cd deployment
./deploy.sh
```

Or manually:
```bash
cd deployment
eb init -p python-3.11 ats-bert-model-api
eb create ats-bert-prod --instance-type t3.large --scale 2
eb deploy
```

### 4. Test
```bash
# Get URL
eb status

# Test health
curl https://your-env.elasticbeanstalk.com/health

# Test prediction
curl -X POST https://your-env.elasticbeanstalk.com/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Your resume text here"}'
```

## Architecture

```
Internet → ALB → EC2 Instances (t3.large) → BERT Model
                      ↓
                 CloudWatch Logs
```

## Cost Estimate

**Production (2 x t3.large):**
- ~$150/month

**Development (1 x t3.medium):**
- ~$30/month

## Key Commands

```bash
# Deploy updates
eb deploy

# View logs
eb logs --stream

# SSH into instance
eb ssh

# Scale up/down
eb scale 4

# Terminate environment
eb terminate ats-bert-prod
```

## Environment Variables

Set in `.env` or via `eb setenv`:
- `MODEL_PATH`: Path to model files
- `TRANSFORMERS_CACHE`: Cache directory
- `BERT_API_URL`: API endpoint (for main app)

## Integration with Main App

```python
# In your main app
import requests
import os

BERT_API_URL = os.getenv('BERT_API_URL')

def get_bert_score(text):
    response = requests.post(
        f"{BERT_API_URL}/predict",
        json={"text": text}
    )
    return response.json()
```

## Monitoring

- CloudWatch Dashboard: `eb console`
- Logs: `eb logs`
- Health: Check `/health` endpoint

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model loading timeout | Increase health check timeout |
| Out of memory | Use larger instance (t3.xlarge) |
| Slow predictions | Use GPU instance (p3.2xlarge) |
| Deployment fails | Check `eb logs` |

## Next Steps

1. ✅ Review complete guide: `docs/deployment/AWS_ELASTIC_BEANSTALK_GUIDE.md`
2. ✅ Test locally: `python deployment/model_api.py`
3. ✅ Deploy to AWS: `./deployment/deploy.sh`
4. ✅ Set up monitoring and alarms
5. ✅ Configure auto-scaling
6. ✅ Integrate with main application

## Support

- Full Guide: `docs/deployment/AWS_ELASTIC_BEANSTALK_GUIDE.md`
- AWS Docs: https://docs.aws.amazon.com/elasticbeanstalk/
- EB CLI: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html
