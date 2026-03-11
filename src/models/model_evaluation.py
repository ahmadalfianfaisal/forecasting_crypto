import mlflow
import mlflow.prophet
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Tuple, Dict, Optional
import logging
from src.utils.data_loader import prepare_prophet_df, download_data

logger = logging.getLogger(__name__)

# Set MLflow tracking URI
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Crypto_Forecast_Models")

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero_idx = y_true != 0
    return np.mean(np.abs((y_true[non_zero_idx] - y_pred[non_zero_idx]) / y_true[non_zero_idx])) * 100

def evaluate_model_performance(model: Prophet, df: pd.DataFrame, test_size: float = 0.1) -> Dict[str, float]:
    """
    Evaluate model performance using time series cross-validation
    
    Args:
        model: Trained Prophet model
        df: DataFrame with 'ds' and 'y' columns
        test_size: Proportion of data to use for testing
    
    Returns:
        Dictionary containing evaluation metrics
    """
    # Split data into train and test sets
    n_test = int(len(df) * test_size)
    train_df = df[:-n_test].copy()
    test_df = df[-n_test:].copy()
    
    if len(train_df) < 30 or len(test_df) < 5:
        raise ValueError(f"Insufficient data for evaluation. Need at least 30 train and 5 test samples, got {len(train_df)} train and {len(test_df)} test")
    
    # Retrain the model on training data only
    eval_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=model.changepoint_prior_scale,
        seasonality_mode=model.seasonality_mode,
        seasonality_prior_scale=model.seasonality_prior_scale,
        changepoint_range=model.changepoint_range
    )
    eval_model.fit(train_df)
    
    # Make predictions on test data
    future = eval_model.make_future_dataframe(periods=len(test_df), freq='D')
    forecast = eval_model.predict(future)
    
    # Extract predictions for test period
    test_predictions = forecast.tail(len(test_df)).reset_index(drop=True)
    test_actuals = test_df.reset_index(drop=True)
    
    # Calculate metrics
    mae = mean_absolute_error(test_actuals['y'], test_predictions['yhat'])
    rmse = np.sqrt(mean_squared_error(test_actuals['y'], test_predictions['yhat']))
    mape = calculate_mape(test_actuals['y'], test_predictions['yhat'])
    
    # Calculate directional accuracy
    actual_direction = np.diff(test_actuals['y']) > 0
    predicted_direction = np.diff(test_predictions['yhat']) > 0
    direction_accuracy = np.mean(actual_direction == predicted_direction) * 100
    
    return {
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
        'direction_accuracy': direction_accuracy,
        'test_size': len(test_df)
    }

def get_latest_production_model(ticker: str) -> Optional[Tuple[Prophet, Dict]]:
    """
    Retrieve the latest production model for a given ticker
    
    Args:
        ticker: Asset ticker symbol
        
    Returns:
        Tuple of (model, metadata) or None if no production model exists
    """
    try:
        # Search for the latest production model in MLflow
        filter_string = f"tags.ticker = '{ticker}' AND tags.stage = 'production'"
        runs = mlflow.search_runs(filter_string=filter_string, max_results=1)
        
        if runs.empty:
            logger.info(f"No production model found for {ticker}")
            return None
        
        # Get the run_id of the latest production model
        latest_run_id = runs.iloc[0]['run_id']
        
        # Load the model from MLflow
        model_uri = f"runs:/{latest_run_id}/model"
        model = mlflow.prophet.load_model(model_uri)
        
        # Get run info
        run_info = mlflow.get_run(latest_run_id)
        metadata = {
            'run_id': latest_run_id,
            'timestamp': run_info.info.start_time,
            'metrics': run_info.data.metrics,
            'params': run_info.data.params
        }
        
        logger.info(f"Loaded production model for {ticker} from run {latest_run_id}")
        return model, metadata
    except Exception as e:
        logger.error(f"Error loading production model for {ticker}: {str(e)}")
        return None

def champion_challenger_evaluation(ticker: str, challenger_model: Prophet, df: pd.DataFrame) -> bool:
    """
    Perform champion-challenger evaluation and determine if challenger should be promoted
    
    Args:
        ticker: Asset ticker symbol
        challenger_model: Newly trained model to evaluate
        df: Full dataset for evaluation
        
    Returns:
        True if challenger should be promoted, False otherwise
    """
    logger.info(f"Starting champion-challenger evaluation for {ticker}")
    
    # Get the current champion model
    champion_result = get_latest_production_model(ticker)
    
    # Prepare data for evaluation
    prophet_df = prepare_prophet_df(df)
    if prophet_df.isnull().any().any():
        prophet_df = prophet_df.dropna()
    
    if len(prophet_df) < 30:
        raise ValueError(f"Insufficient data for evaluation for {ticker}")
    
    prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
    prophet_df = prophet_df.drop_duplicates(subset=['ds'])
    
    # Evaluate the challenger model
    try:
        challenger_metrics = evaluate_model_performance(challenger_model, prophet_df)
        logger.info(f"Challenger model metrics for {ticker}: {challenger_metrics}")
    except Exception as e:
        logger.error(f"Error evaluating challenger model for {ticker}: {str(e)}")
        return False
    
    # If no champion exists, promote the challenger
    if champion_result is None:
        logger.info(f"No champion model exists for {ticker}, promoting challenger")
        return True
    
    # Evaluate the champion model
    champion_model, champion_metadata = champion_result
    try:
        champion_metrics = evaluate_model_performance(champion_model, prophet_df)
        logger.info(f"Champion model metrics for {ticker}: {champion_metrics}")
    except Exception as e:
        logger.error(f"Error evaluating champion model for {ticker}: {str(e)}")
        # If champion evaluation fails, promote the challenger
        return True
    
    # Compare models based on RMSE (lower is better)
    challenger_better = challenger_metrics['rmse'] < champion_metrics['rmse']
    
    # Log comparison results
    logger.info(f"Model comparison for {ticker}:")
    logger.info(f"  Champion RMSE: {champion_metrics['rmse']:.4f}")
    logger.info(f"  Challenger RMSE: {challenger_metrics['rmse']:.4f}")
    logger.info(f"  Challenger is {'better' if challenger_better else 'worse'} than champion")
    
    return challenger_better

def log_model_to_mlflow(ticker: str, model: Prophet, df: pd.DataFrame, stage: str = "candidate"):
    """
    Log the model to MLflow with metrics and parameters
    
    Args:
        ticker: Asset ticker symbol
        model: Prophet model to log
        df: Training data
        stage: Model stage ('candidate', 'production', etc.)
    """
    with mlflow.start_run(run_name=f"{ticker}_model_training"):
        # Prepare data for evaluation
        prophet_df = prepare_prophet_df(df)
        if prophet_df.isnull().any().any():
            prophet_df = prophet_df.dropna()
        prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
        prophet_df = prophet_df.drop_duplicates(subset=['ds'])
        
        # Evaluate model
        metrics = evaluate_model_performance(model, prophet_df)
        
        # Log parameters
        mlflow.log_param("ticker", ticker)
        mlflow.log_param("changepoint_prior_scale", model.changepoint_prior_scale)
        mlflow.log_param("seasonality_mode", model.seasonality_mode)
        mlflow.log_param("seasonality_prior_scale", model.seasonality_prior_scale)
        mlflow.log_param("changepoint_range", model.changepoint_range)
        mlflow.log_param("yearly_seasonality", model.yearly_seasonality)
        mlflow.log_param("weekly_seasonality", model.weekly_seasonality)
        mlflow.log_param("daily_seasonality", model.daily_seasonality)
        mlflow.log_param("dataset_size", len(prophet_df))
        mlflow.log_param("training_start_date", str(prophet_df['ds'].min()))
        mlflow.log_param("training_end_date", str(prophet_df['ds'].max()))
        
        # Log metrics
        mlflow.log_metrics(metrics)
        
        # Log the model
        mlflow.prophet.log_model(
            model,
            artifact_path="model",
            conda_env="./environment.yml"  # We'll create this later
        )
        
        # Set tags
        mlflow.set_tag("ticker", ticker)
        mlflow.set_tag("stage", stage)
        mlflow.set_tag("model_type", "prophet")
        
        run_id = mlflow.active_run().info.run_id
        logger.info(f"Model logged to MLflow with run_id: {run_id}")
        
        return run_id

def promote_model_to_production(run_id: str, ticker: str):
    """
    Promote a model to production stage in MLflow
    
    Args:
        run_id: MLflow run ID of the model to promote
        ticker: Asset ticker symbol
    """
    # In a real scenario, we would update the model version stage
    # For now, we'll just log that the model is promoted
    logger.info(f"Promoting model {run_id} for {ticker} to production")
    
    # Update the tag to indicate production stage
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("stage", "production")
        mlflow.set_tag("promoted_at", pd.Timestamp.now().isoformat())
    
    logger.info(f"Model {run_id} for {ticker} promoted to production")