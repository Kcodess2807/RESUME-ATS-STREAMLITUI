#!/bin/bash
# Quick deployment script for AWS Elastic Beanstalk

set -e

echo "🚀 ATS BERT Model - AWS Elastic Beanstalk Deployment"
echo "=================================================="

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Installing..."
    pip install awsebcli --upgrade
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run: aws configure"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Get environment name
read -p "Enter environment name (default: ats-bert-prod): " ENV_NAME
ENV_NAME=${ENV_NAME:-ats-bert-prod}

# Get instance type
read -p "Enter instance type (default: t3.large): " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.large}

# Get number of instances
read -p "Enter number of instances (default: 2): " INSTANCE_COUNT
INSTANCE_COUNT=${INSTANCE_COUNT:-2}

echo ""
echo "📋 Deployment Configuration:"
echo "   Environment: $ENV_NAME"
echo "   Instance Type: $INSTANCE_TYPE"
echo "   Instance Count: $INSTANCE_COUNT"
echo ""

read -p "Continue with deployment? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Initialize EB if not already done
if [ ! -d ".elasticbeanstalk" ]; then
    echo "🔧 Initializing Elastic Beanstalk..."
    eb init -p python-3.11 ats-bert-model-api --region us-east-1
fi

# Create or update environment
if eb list | grep -q "$ENV_NAME"; then
    echo "📦 Deploying to existing environment: $ENV_NAME"
    eb deploy $ENV_NAME
else
    echo "🆕 Creating new environment: $ENV_NAME"
    eb create $ENV_NAME \
        --instance-type $INSTANCE_TYPE \
        --scale $INSTANCE_COUNT \
        --envvars MODEL_PATH=/var/app/current/models/finetuned-bert,TRANSFORMERS_CACHE=/tmp/transformers_cache
fi

# Wait for environment to be ready
echo "⏳ Waiting for environment to be ready..."
eb status $ENV_NAME

# Get the URL
URL=$(eb status $ENV_NAME | grep "CNAME" | awk '{print $2}')

echo ""
echo "✅ Deployment Complete!"
echo "=================================================="
echo "🌐 API URL: https://$URL"
echo ""
echo "Test endpoints:"
echo "  Health: curl https://$URL/health"
echo "  Predict: curl -X POST https://$URL/predict -H 'Content-Type: application/json' -d '{\"text\":\"test\"}'"
echo ""
echo "View logs: eb logs $ENV_NAME"
echo "SSH access: eb ssh $ENV_NAME"
echo "Console: eb console $ENV_NAME"
echo ""
