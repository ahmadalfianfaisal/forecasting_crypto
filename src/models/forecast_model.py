import pandas as pd
from prophet import Prophet
from typing import Tuple
from src.utils.data_loader import download_data, prepare_prophet_df
from src.models.model_storage import load_model
from src.models.model_trainer import train_single_model
from src.models.model_evaluation import get_latest_production_model
import mlflow
import mlflow.prophet


def train_prophet(df: pd.DataFrame) -> Prophet:
    """
    Initialize and fit a Prophet model on prepared data.

    Parameters:
        df (pd.DataFrame): Prophet-format DataFrame with ['ds', 'y']

    Returns:
        Prophet: Fitted Prophet model instance
    """
    # Initialize Prophet model with financial-tuned hyperparameters
    # Using more conservative parameters to handle volatile crypto data
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,  # Reduced to prevent overfitting
        seasonality_mode='multiplicative',  # Better for volatile data
        seasonality_prior_scale=10,
        changepoint_range=0.8  # Allow changes in the last 80% of the series
    )

    # Fit the model on the data
    model.fit(df)

    return model


def clip_negative_forecast(forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clip negative values in forecast to minimum acceptable values.
    
    Parameters:
        forecast_df (pd.DataFrame): Forecast DataFrame with columns ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        
    Returns:
        pd.DataFrame: Forecast DataFrame with non-negative values
    """
    # Create a copy to avoid modifying the original
    clipped_df = forecast_df.copy()
    
    # Find the minimum positive value in the historical data as baseline
    # This ensures that our clipped values are realistic
    
    # Replace negative values with small positive values (e.g., 0.01 or 1% of min positive value)
    # First, find the minimum positive forecast value to establish a baseline
    min_positive_value = clipped_df[clipped_df['yhat'] > 0]['yhat'].min()
    
    # If there are no positive values, use a reasonable default
    if pd.isna(min_positive_value) or min_positive_value <= 0:
        min_positive_value = 1.0  # Default to $1 as minimum
    
    # Calculate a minimum threshold based on the minimum positive value
    min_threshold = min_positive_value * 0.01  # 1% of minimum positive value, but at least 0.01
    min_threshold = max(min_threshold, 0.01)
    
    # Clip the values to ensure they're not negative
    clipped_df['yhat'] = clipped_df['yhat'].clip(lower=min_threshold)
    clipped_df['yhat_lower'] = clipped_df['yhat_lower'].clip(lower=min_threshold)
    
    # Ensure upper bound is also reasonable (though it rarely goes negative)
    clipped_df['yhat_upper'] = clipped_df['yhat_upper'].clip(lower=min_threshold)
    
    # Important: Maintain the relationship between upper and lower bounds
    # If lower bound is now higher than prediction, adjust accordingly
    clipped_df['yhat_lower'] = clipped_df[['yhat', 'yhat_lower']].min(axis=1)
    clipped_df['yhat_upper'] = clipped_df[['yhat', 'yhat_upper']].max(axis=1)
    
    return clipped_df


def generate_forecast(model: Prophet, periods: int = 30) -> pd.DataFrame:
    """
    Create future dataframe and generate forecast.

    Parameters:
        model (Prophet): Fitted Prophet model
        periods (int): Number of future days to forecast

    Returns:
        pd.DataFrame: Forecast DataFrame with columns ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
                      Contains only future rows (from tomorrow onward).
    """
    # Create future dataframe for the specified number of periods
    future_df = model.make_future_dataframe(periods=periods)

    # Generate forecast
    forecast_df = model.predict(future_df)

    # Filter to only include future dates (after the last historical date)
    last_historical_date = model.history['ds'].max()
    forecast_df = forecast_df[forecast_df['ds'] > last_historical_date]

    # Apply clipping to handle negative forecasts
    forecast_df = clip_negative_forecast(forecast_df)

    # Return only the relevant columns
    return forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


def run_forecast(ticker: str, periods: int = 30) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Full forecasting pipeline: download data, load production model from MLflow, generate forecast.

    Parameters:
        ticker (str): Yahoo Finance ticker symbol
        periods (int): Number of days to forecast

    Returns:
        tuple: (historical_df, forecast_df)
               historical_df has columns [Date, Open, High, Low, Close, Volume]
               forecast_df has columns [ds, yhat, yhat_lower, yhat_upper]
    """
    # Download historical data
    historical_df = download_data(ticker, period="2y")

    # Check if we have sufficient data
    if len(historical_df) < 30:
        raise ValueError(f"Insufficient data for {ticker}. Need at least 30 days of data, got {len(historical_df)} days.")

    # Load the production model from MLflow
    model_result = get_latest_production_model(ticker)
    
    if model_result is None:
        print(f"No production model found for {ticker}, training now...")
        success = train_single_model(ticker)
        if success:
            model_result = get_latest_production_model(ticker)
            if model_result is None:
                # Fallback to local model if MLflow model isn't available
                model = load_model(ticker)
                if model is None:
                    raise ValueError(f"Failed to load model for {ticker} even after training")
            else:
                model, _ = model_result
        else:
            raise ValueError(f"Failed to train model for {ticker}")
    else:
        model, _ = model_result

    # Generate forecast using the loaded model
    forecast_df = generate_forecast(model, periods)

    return historical_df, forecast_df