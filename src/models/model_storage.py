import os
import pickle
from prophet import Prophet
from typing import Optional
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def save_model(model: Prophet, ticker: str) -> bool:
    """
    Save the trained Prophet model to disk
    
    Args:
        model: Trained Prophet model
        ticker: Asset ticker symbol (e.g., 'BTC-USD')
    
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model saved for {ticker} at {model_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving model for {ticker}: {str(e)}")
        return False

def load_model(ticker: str) -> Optional[Prophet]:
    """
    Load a trained Prophet model from disk
    
    Args:
        ticker: Asset ticker symbol (e.g., 'BTC-USD')
    
    Returns:
        Loaded Prophet model or None if not found/error
    """
    try:
        model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
        if not os.path.exists(model_path):
            logger.warning(f"No saved model found for {ticker}")
            return None
            
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded for {ticker}")
        return model
    except Exception as e:
        logger.error(f"Error loading model for {ticker}: {str(e)}")
        return None

def delete_old_models():
    """Delete all old models from the model directory"""
    try:
        for filename in os.listdir(MODEL_DIR):
            if filename.endswith("_model.pkl"):
                filepath = os.path.join(MODEL_DIR, filename)
                os.remove(filepath)
                logger.info(f"Deleted old model: {filepath}")
    except Exception as e:
        logger.error(f"Error deleting old models: {str(e)}")