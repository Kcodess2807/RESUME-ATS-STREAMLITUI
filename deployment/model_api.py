"""
BERT Model API for AWS Elastic Beanstalk Deployment

This module provides a Flask API wrapper for the fine-tuned BERT model
that can be deployed separately on AWS Elastic Beanstalk.
"""

from flask import Flask, request, jsonify
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

application = Flask(__name__)

# Global model and tokenizer
model = None
tokenizer = None
device = None


def load_model():
    """Load the fine-tuned BERT model."""
    global model, tokenizer, device
    
    try:
        model_path = os.getenv('MODEL_PATH', 'models/finetuned-bert')
        
        logger.info(f"Loading model from {model_path}")
        
        # Set device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {device}")
        
        # Load tokenizer and model
        tokenizer = BertTokenizer.from_pretrained(model_path)
        model = BertForSequenceClassification.from_pretrained(model_path)
        model.to(device)
        model.eval()
        
        logger.info("Model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False


@application.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancer."""
    if model is None:
        return jsonify({'status': 'unhealthy', 'message': 'Model not loaded'}), 503
    return jsonify({'status': 'healthy'}), 200


@application.route('/predict', methods=['POST'])
def predict():
    """
    Predict endpoint for resume scoring.
    
    Expected JSON input:
    {
        "text": "resume text here",
        "max_length": 512  # optional
    }
    
    Returns:
    {
        "score": 0.85,
        "confidence": 0.92,
        "label": "good"
    }
    """
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 503
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text field'}), 400
        
        text = data['text']
        max_length = data.get('max_length', 512)
        
        # Tokenize input
        inputs = tokenizer(
            text,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Move to device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
        
        # Map class to label (adjust based on your model)
        label_map = {0: 'poor', 1: 'fair', 2: 'good', 3: 'excellent'}
        label = label_map.get(predicted_class, 'unknown')
        
        # Convert to score (0-100)
        score = (predicted_class + 1) * 25  # Simple mapping
        
        return jsonify({
            'score': score,
            'confidence': confidence,
            'label': label,
            'class': predicted_class
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@application.route('/batch_predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction endpoint.
    
    Expected JSON input:
    {
        "texts": ["resume 1", "resume 2", ...],
        "max_length": 512  # optional
    }
    """
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 503
        
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'Missing texts field'}), 400
        
        texts = data['texts']
        max_length = data.get('max_length', 512)
        
        if not isinstance(texts, list):
            return jsonify({'error': 'texts must be a list'}), 400
        
        results = []
        
        for text in texts:
            # Tokenize
            inputs = tokenizer(
                text,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            label_map = {0: 'poor', 1: 'fair', 2: 'good', 3: 'excellent'}
            label = label_map.get(predicted_class, 'unknown')
            score = (predicted_class + 1) * 25
            
            results.append({
                'score': score,
                'confidence': confidence,
                'label': label,
                'class': predicted_class
            })
        
        return jsonify({'results': results}), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@application.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'name': 'ATS Resume Scorer - BERT Model API',
        'version': '1.0.0',
        'endpoints': {
            '/health': 'GET - Health check',
            '/predict': 'POST - Single prediction',
            '/batch_predict': 'POST - Batch predictions'
        }
    }), 200


# Initialize model on startup
if __name__ == '__main__':
    logger.info("Starting model API...")
    load_model()
    application.run(host='0.0.0.0', port=8080, debug=False)
else:
    # For WSGI server
    load_model()
