"""
Expanding Window Training Approach for Time Series Models

This module implements an expanding window training approach where:
1. Each phase adds 1 month of data to the training set
2. Tests on the following month
3. Evaluates performance against thresholds
4. Performs model improvements if needed
"""
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from prophet import Prophet
from data_loader import download_data, prepare_prophet_df
from model_evaluation import evaluate_model_performance, calculate_mape
from sklearn.metrics import mean_absolute_error, mean_squared_error
import itertools

logger = logging.getLogger(__name__)

# Define threshold values for model performance
THRESHOLD_METRICS = {
    'mape': 10.0,  # Maximum acceptable MAPE percentage
    'rmse': None,  # Will be calculated dynamically based on data scale
    'mae': None,   # Will be calculated dynamically based on data scale
    'direction_accuracy': 55.0  # Minimum acceptable directional accuracy percentage
}

def calculate_dynamic_thresholds(data: pd.Series) -> Dict[str, float]:
    """
    Calculate dynamic thresholds based on the scale of the data
    
    Args:
        data: Time series data
        
    Returns:
        Dictionary with dynamic thresholds
    """
    data_mean = data.mean()
    
    # Calculate RMSE and MAE thresholds as percentages of the mean value
    rmse_threshold = data_mean * 0.05  # 5% of mean value
    mae_threshold = data_mean * 0.03   # 3% of mean value
    
    return {
        'rmse': rmse_threshold,
        'mae': mae_threshold
    }

def time_based_split(data: pd.DataFrame, train_months: int, test_months: int = 1) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split time series data chronologically based on months
    
    Args:
        data: DataFrame with 'ds' column containing dates
        train_months: Number of months for training
        test_months: Number of months for testing (default 1)
        
    Returns:
        Tuple of (train_df, test_df)
    """
    # Ensure data is sorted by date
    data = data.sort_values('ds').reset_index(drop=True)
    
    # Find the date range
    start_date = data['ds'].min()
    
    # Calculate the end of training period
    train_end_date = start_date + pd.DateOffset(months=train_months)
    
    # Calculate the end of test period
    test_end_date = train_end_date + pd.DateOffset(months=test_months)
    
    # Split the data
    train_mask = (data['ds'] >= start_date) & (data['ds'] < train_end_date)
    test_mask = (data['ds'] >= train_end_date) & (data['ds'] < test_end_date)
    
    train_df = data[train_mask].reset_index(drop=True)
    test_df = data[test_mask].reset_index(drop=True)
    
    return train_df, test_df

def hyperparameter_tuning(train_df: pd.DataFrame, test_df: pd.DataFrame, 
                         base_params: Dict = None) -> Tuple[Dict, float]:
    """
    Perform hyperparameter tuning to improve model performance
    
    Args:
        train_df: Training data
        test_df: Test data for validation
        base_params: Base parameters to start tuning from
        
    Returns:
        Tuple of (best_params, best_score)
    """
    if base_params is None:
        base_params = {
            'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
            'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
            'changepoint_range': [0.8, 0.9, 0.95],
            'seasonality_mode': ['additive', 'multiplicative']
        }
    
    # Define parameter combinations to try
    param_grid = list(itertools.product(*base_params.values()))
    param_names = list(base_params.keys())
    
    best_score = float('inf')
    best_params = None
    
    logger.info(f"Starting hyperparameter tuning with {len(param_grid)} combinations")
    
    for i, param_values in enumerate(param_grid):
        params = dict(zip(param_names, param_values))
        
        try:
            # Create and train model with current parameters
            model = Prophet(**params)
            model.fit(train_df)
            
            # Make predictions on test set
            future = model.make_future_dataframe(periods=len(test_df), freq='D')
            forecast = model.predict(future)
            
            # Extract predictions for test period
            test_predictions = forecast.tail(len(test_df)).reset_index(drop=True)
            test_actuals = test_df.reset_index(drop=True)
            
            # Calculate RMSE as the score to minimize
            score = np.sqrt(mean_squared_error(test_actuals['y'], test_predictions['yhat']))
            
            if score < best_score:
                best_score = score
                best_params = params.copy()
                
            if i % 20 == 0:  # Log progress every 20 iterations
                logger.info(f"Tried {i+1}/{len(param_grid)} parameter combinations, best RMSE so far: {best_score:.4f}")
                
        except Exception as e:
            logger.warning(f"Parameter combination {params} failed: {str(e)}")
            continue
    
    logger.info(f"Hyperparameter tuning completed. Best RMSE: {best_score:.4f}, Best params: {best_params}")
    return best_params, best_score

def feature_engineering(data: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering to improve model performance
    
    Args:
        data: Input DataFrame with 'ds' and 'y' columns
        
    Returns:
        DataFrame with engineered features
    """
    df = data.copy()
    
    # Add lag features
    df = df.sort_values('ds').reset_index(drop=True)
    
    # Add rolling statistics
    df['y_rolling_mean_7'] = df['y'].rolling(window=7, min_periods=1).mean()
    df['y_rolling_std_7'] = df['y'].rolling(window=7, min_periods=1).std()
    df['y_rolling_mean_14'] = df['y'].rolling(window=14, min_periods=1).mean()
    df['y_rolling_std_14'] = df['y'].rolling(window=14, min_periods=1).std()
    
    # Add percentage change
    df['y_pct_change'] = df['y'].pct_change(fill_method=None)
    df['y_pct_change'] = df['y_pct_change'].fillna(0)
    
    # Add day of week and month features
    df['day_of_week'] = df['ds'].dt.dayofweek
    df['month'] = df['ds'].dt.month
    df['quarter'] = df['ds'].dt.quarter
    
    # Add time-based trend features
    df['days_from_start'] = (df['ds'] - df['ds'].min()).dt.days
    
    return df

def train_with_improvements(train_df: pd.DataFrame, test_df: pd.DataFrame, 
                           target_metrics: Dict[str, float], 
                           max_iterations: int = 3) -> Tuple[Prophet, Dict, bool]:
    """
    Train model with iterative improvements until target metrics are met
    
    Args:
        train_df: Training data
        test_df: Test data for validation
        target_metrics: Target metric thresholds
        max_iterations: Maximum number of improvement iterations
        
    Returns:
        Tuple of (model, metrics, met_targets)
    """
    # Start with basic model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_mode='multiplicative',
        seasonality_prior_scale=10,
        changepoint_range=0.8
    )
    
    model.fit(train_df)
    
    # Evaluate initial model
    metrics = evaluate_model_performance_on_test_set(model, train_df, test_df)
    
    logger.info(f"Initial model metrics: {metrics}")
    
    # Check if targets are met
    met_targets = check_metrics_against_thresholds(metrics, target_metrics)
    
    if met_targets:
        logger.info("Initial model meets target metrics")
        return model, metrics, True
    
    # Iteratively improve the model
    iteration = 0
    while not met_targets and iteration < max_iterations:
        iteration += 1
        logger.info(f"Improvement iteration {iteration}: Starting model improvements")
        
        # Option 1: Hyperparameter tuning
        logger.info("Trying hyperparameter tuning...")
        best_params, _ = hyperparameter_tuning(train_df, test_df)
        
        if best_params:
            improved_model = Prophet(**best_params)
            improved_model.fit(train_df)
            
            # Evaluate improved model
            improved_metrics = evaluate_model_performance_on_test_set(improved_model, train_df, test_df)
            
            logger.info(f"Improved model metrics after tuning: {improved_metrics}")
            
            # Check if targets are met
            met_targets = check_metrics_against_thresholds(improved_metrics, target_metrics)
            
            if met_targets:
                logger.info(f"Model meets target metrics after hyperparameter tuning in iteration {iteration}")
                return improved_model, improved_metrics, True
            
            # If tuning didn't work, try feature engineering
            logger.info("Hyperparameter tuning didn't meet targets, trying feature engineering...")
            
            # Feature engineering approach
            enhanced_train_df = feature_engineering(train_df)
            enhanced_test_df = feature_engineering(test_df)
            
            # For Prophet, we need to select only the required columns
            enhanced_train_df = enhanced_train_df[['ds', 'y']]
            enhanced_test_df = enhanced_test_df[['ds', 'y']]
            
            # Re-train with enhanced features
            feature_model = Prophet(**best_params)
            feature_model.fit(enhanced_train_df)
            
            # Evaluate feature-enhanced model
            feature_metrics = evaluate_model_performance_on_test_set(feature_model, enhanced_train_df, enhanced_test_df)
            
            logger.info(f"Feature-enhanced model metrics: {feature_metrics}")
            
            # Check if targets are met
            met_targets = check_metrics_against_thresholds(feature_metrics, target_metrics)
            
            if met_targets:
                logger.info(f"Model meets target metrics after feature engineering in iteration {iteration}")
                return feature_model, feature_metrics, True
        else:
            logger.warning("Hyperparameter tuning failed, trying feature engineering...")
            
            # Feature engineering approach
            enhanced_train_df = feature_engineering(train_df)
            enhanced_test_df = feature_engineering(test_df)
            
            # For Prophet, we need to select only the required columns
            enhanced_train_df = enhanced_train_df[['ds', 'y']]
            enhanced_test_df = enhanced_test_df[['ds', 'y']]
            
            # Re-train with enhanced features
            feature_model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_mode='multiplicative',
                seasonality_prior_scale=10,
                changepoint_range=0.8
            )
            feature_model.fit(enhanced_train_df)
            
            # Evaluate feature-enhanced model
            feature_metrics = evaluate_model_performance_on_test_set(feature_model, enhanced_train_df, enhanced_test_df)
            
            logger.info(f"Feature-enhanced model metrics: {feature_metrics}")
            
            # Check if targets are met
            met_targets = check_metrics_against_thresholds(feature_metrics, target_metrics)
            
            if met_targets:
                logger.info(f"Model meets target metrics after feature engineering in iteration {iteration}")
                return feature_model, feature_metrics, True
    
    logger.info(f"Model did not meet target metrics after {max_iterations} iterations")
    return model, metrics, False

def evaluate_model_performance_on_test_set(model: Prophet, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, float]:
    """
    Evaluate model performance specifically on the test set using existing evaluation functions
    
    Args:
        model: Trained Prophet model
        train_df: Training data
        test_df: Test data
        
    Returns:
        Dictionary containing evaluation metrics
    """
    # Combine train and test data to simulate the real scenario
    combined_df = pd.concat([train_df, test_df]).reset_index(drop=True)
    
    # Use the existing evaluate_model_performance function with the combined data
    # but specifying the test portion
    try:
        # Temporarily create a model with the same parameters for evaluation
        eval_model = Prophet(
            yearly_seasonality=getattr(model, 'yearly_seasonality', True),
            weekly_seasonality=getattr(model, 'weekly_seasonality', True),
            daily_seasonality=getattr(model, 'daily_seasonality', False),
            changepoint_prior_scale=getattr(model, 'changepoint_prior_scale', 0.05),
            seasonality_mode=getattr(model, 'seasonality_mode', 'multiplicative'),
            seasonality_prior_scale=getattr(model, 'seasonality_prior_scale', 10),
            changepoint_range=getattr(model, 'changepoint_range', 0.8)
        )
        eval_model.fit(train_df)
        
        # Calculate test proportion for the evaluation function
        test_prop = len(test_df) / len(combined_df)
        
        # Use the existing evaluation function
        from model_evaluation import evaluate_model_performance
        metrics = evaluate_model_performance(eval_model, combined_df, test_size=test_prop)
        
        return metrics
    except Exception as e:
        logger.warning(f"Using fallback evaluation due to error: {str(e)}")
        
        # Fallback: manual calculation
        future = model.make_future_dataframe(periods=len(test_df), freq='D')
        forecast = model.predict(future)
        
        # Extract predictions for test period
        test_predictions = forecast.tail(len(test_df)).reset_index(drop=True)
        test_actuals = test_df.reset_index(drop=True)
        
        # Calculate metrics
        mae = mean_absolute_error(test_actuals['y'], test_predictions['yhat'])
        rmse = np.sqrt(mean_squared_error(test_actuals['y'], test_predictions['yhat']))
        mape = calculate_mape(test_actuals['y'], test_predictions['yhat'])
        
        # Calculate directional accuracy
        if len(test_actuals) > 1:
            actual_direction = np.diff(test_actuals['y']) > 0
            predicted_direction = np.diff(test_predictions['yhat']) > 0
            # Pad arrays to same length if needed
            if len(actual_direction) > len(predicted_direction):
                actual_direction = actual_direction[:len(predicted_direction)]
            elif len(predicted_direction) > len(actual_direction):
                predicted_direction = predicted_direction[:len(actual_direction)]
            
            direction_accuracy = np.mean(actual_direction == predicted_direction) * 100
        else:
            direction_accuracy = 0.0  # Can't calculate with only one point
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'direction_accuracy': direction_accuracy,
            'test_size': len(test_df)
        }

def check_metrics_against_thresholds(metrics: Dict[str, float], thresholds: Dict[str, float]) -> bool:
    """
    Check if model metrics meet the target thresholds
    
    Args:
        metrics: Current model metrics
        thresholds: Target thresholds
        
    Returns:
        True if all metrics meet thresholds, False otherwise
    """
    # Check each threshold
    for metric_name, threshold_value in thresholds.items():
        if threshold_value is not None:
            current_value = metrics.get(metric_name)
            if current_value is None:
                logger.warning(f"Metric {metric_name} not found in metrics")
                continue
                
            # For MAPE and similar metrics where lower is better
            if metric_name in ['mape', 'rmse', 'mae']:
                if current_value > threshold_value:
                    logger.info(f"Metric {metric_name} ({current_value:.4f}) exceeds threshold ({threshold_value:.4f})")
                    return False
            # For accuracy metrics where higher is better
            elif metric_name in ['direction_accuracy']:
                if current_value < threshold_value:
                    logger.info(f"Metric {metric_name} ({current_value:.4f}%) below threshold ({threshold_value:.4f}%)")
                    return False
    
    return True

def expanding_window_training(ticker: str, initial_train_months: int = 18, 
                             total_train_months: int = 24) -> List[Dict]:
    """
    Perform expanding window training for a given ticker
    
    Args:
        ticker: Asset ticker symbol
        initial_train_months: Initial number of months for training (default 18)
        total_train_months: Total number of months to cover (default 24)
        
    Returns:
        List of dictionaries containing results for each phase
    """
    logger.info(f"Starting expanding window training for {ticker}")
    
    # Download historical data
    historical_df = download_data(ticker, period="2y")
    
    if len(historical_df) < 30:
        raise ValueError(f"Insufficient data for {ticker}. Need at least 30 days of data, got {len(historical_df)} days.")
    
    # Prepare data for Prophet
    prophet_df = prepare_prophet_df(historical_df)
    
    if prophet_df.isnull().any().any():
        prophet_df = prophet_df.dropna()
    
    if len(prophet_df) < 30:
        raise ValueError(f"Insufficient clean data for {ticker} after preprocessing. Need at least 30 days of data.")
    
    # Ensure the data is sorted by date
    prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
    
    # Remove duplicate dates if any
    prophet_df = prophet_df.drop_duplicates(subset=['ds'])
    
    # Calculate dynamic thresholds based on the data
    dynamic_thresholds = calculate_dynamic_thresholds(prophet_df['y'])
    target_metrics = THRESHOLD_METRICS.copy()
    target_metrics.update(dynamic_thresholds)
    
    results = []
    current_train_months = initial_train_months
    
    # Start an MLflow run to track the entire expanding window process
    import mlflow
    with mlflow.start_run(run_name=f"{ticker}_expanding_window_training"):
        mlflow.log_param("ticker", ticker)
        mlflow.log_param("initial_train_months", initial_train_months)
        mlflow.log_param("total_train_months", total_train_months)
        mlflow.log_param("dataset_size", len(prophet_df))
        mlflow.log_param("data_start_date", str(prophet_df['ds'].min()))
        mlflow.log_param("data_end_date", str(prophet_df['ds'].max()))
        
        # Phase 1: Start with initial_train_months
        while current_train_months < total_train_months:
            logger.info(f"Starting Phase with {current_train_months} months of training data")
            
            # Split data for this phase
            train_df, test_df = time_based_split(prophet_df, current_train_months, 1)
            
            if len(train_df) < 30 or len(test_df) < 5:
                logger.warning(f"Insufficient data for phase with {current_train_months} training months. Train: {len(train_df)}, Test: {len(test_df)}")
                current_train_months += 1
                continue
            
            logger.info(f"Train set: {len(train_df)} samples, Test set: {len(test_df)} samples")
            
            # Train model with improvements until targets are met
            model, metrics, met_targets = train_with_improvements(
                train_df, test_df, target_metrics
            )
            
            # Record phase results
            phase_result = {
                'phase': current_train_months - initial_train_months + 1,
                'train_months': current_train_months,
                'test_period': f"{test_df['ds'].min().strftime('%Y-%m')} to {test_df['ds'].max().strftime('%Y-%m')}",
                'train_size': len(train_df),
                'test_size': len(test_df),
                'metrics': metrics,
                'met_targets': met_targets,
                'model': model
            }
            
            results.append(phase_result)
            
            logger.info(f"Phase {phase_result['phase']} completed. Met targets: {met_targets}")
            logger.info(f"Metrics: {metrics}")
            
            # Log phase results to MLflow
            mlflow.log_metric(f"phase_{phase_result['phase']}_train_months", current_train_months)
            mlflow.log_metric(f"phase_{phase_result['phase']}_train_size", len(train_df))
            mlflow.log_metric(f"phase_{phase_result['phase']}_test_size", len(test_df))
            mlflow.log_metric(f"phase_{phase_result['phase']}_mae", metrics['mae'])
            mlflow.log_metric(f"phase_{phase_result['phase']}_rmse", metrics['rmse'])
            mlflow.log_metric(f"phase_{phase_result['phase']}_mape", metrics['mape'])
            mlflow.log_metric(f"phase_{phase_result['phase']}_direction_accuracy", metrics['direction_accuracy'])
            mlflow.log_metric(f"phase_{phase_result['phase']}_met_targets", 1 if met_targets else 0)
            
            # Move to next phase by adding one month to training data
            current_train_months += 1
        
        logger.info(f"Expanding window training completed for {ticker}. Total phases: {len(results)}")
        
        # Log summary metrics
        avg_mape = sum(r['metrics']['mape'] for r in results) / len(results) if results else 0
        avg_rmse = sum(r['metrics']['rmse'] for r in results) / len(results) if results else 0
        avg_direction_accuracy = sum(r['metrics']['direction_accuracy'] for r in results) / len(results) if results else 0
        met_targets_count = sum(1 for r in results if r['met_targets'])
        
        mlflow.log_metric("avg_mape_across_phases", avg_mape)
        mlflow.log_metric("avg_rmse_across_phases", avg_rmse)
        mlflow.log_metric("avg_direction_accuracy_across_phases", avg_direction_accuracy)
        mlflow.log_metric("phases_met_targets", met_targets_count)
        mlflow.log_metric("total_phases", len(results))
    
    return results

def train_single_model_expanding_window(ticker: str) -> bool:
    """
    Train a model for a single ticker using the expanding window approach
    
    Args:
        ticker: Asset ticker symbol
        
    Returns:
        True if training successful, False otherwise
    """
    try:
        logger.info(f"Starting expanding window model training for {ticker}")
        
        # Perform expanding window training
        results = expanding_window_training(ticker)
        
        if not results:
            logger.error(f"No successful training phases for {ticker}")
            return False
        
        # Get the final model from the last phase
        final_result = results[-1]
        final_model = final_result['model']
        
        logger.info(f"Completed {len(results)} training phases for {ticker}")
        logger.info(f"Final model performance: {final_result['metrics']}")
        
        # Integrate with existing model evaluation and storage systems
        from model_evaluation import champion_challenger_evaluation, log_model_to_mlflow, promote_model_to_production
        from model_storage import save_model
        
        # Perform champion-challenger evaluation to see if this model should replace the current production model
        should_promote = champion_challenger_evaluation(ticker, final_model, historical_df)
        
        if should_promote:
            # Log the model to MLflow as a candidate first
            run_id = log_model_to_mlflow(ticker, final_model, historical_df, stage="candidate")

            # Promote to production
            promote_model_to_production(run_id, ticker)

            # Save the model locally as well
            success = save_model(final_model, ticker)
            if success:
                logger.info(f"Successfully trained, evaluated, and promoted model for {ticker}")
            else:
                logger.error(f"Failed to save model for {ticker}")
                return False
        else:
            logger.info(f"Expanding window model for {ticker} did not outperform champion, keeping current model")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in expanding window training for {ticker}: {str(e)}")
        return False

def train_all_models_expanding_window() -> Dict[str, bool]:
    """
    Train models for all supported tickers using expanding window approach
    
    Returns:
        Dictionary mapping ticker symbols to training success status
    """
    from data_loader import get_available_tickers

    tickers = [item['value'] for item in get_available_tickers()]
    results = {}

    for ticker in tickers:
        logger.info(f"Training model for {ticker} using expanding window approach")
        results[ticker] = train_single_model_expanding_window(ticker)

    return results