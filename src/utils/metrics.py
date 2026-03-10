import pandas as pd
import numpy as np
from typing import Dict


def get_current_price(df: pd.DataFrame) -> float:
    """
    Get the most recent closing price.

    Parameters:
        df (pd.DataFrame): Historical OHLCV DataFrame

    Returns:
        float: Latest closing price in USD
    """
    if df.empty:
        return 0.0
    
    return float(df['Close'].iloc[-1])


def get_predicted_price(forecast_df: pd.DataFrame) -> float:
    """
    Get the final predicted price from the forecast.

    Parameters:
        forecast_df (pd.DataFrame): Forecast DataFrame with 'yhat' column

    Returns:
        float: Predicted price on the last forecast day
    """
    if forecast_df.empty:
        return 0.0
    
    return float(forecast_df['yhat'].iloc[-1])


def get_pct_change(current: float, predicted: float) -> float:
    """
    Calculate percentage change between current and predicted price.

    Parameters:
        current (float): Current price
        predicted (float): Predicted price

    Returns:
        float: Percentage change, e.g. 5.23 means +5.23%
    """
    if current == 0:
        return 0.0
    
    return ((predicted - current) / current) * 100


def get_volatility(df: pd.DataFrame, window: int = 30) -> float:
    """
    Calculate annualized rolling volatility using log returns.

    Parameters:
        df (pd.DataFrame): Historical OHLCV DataFrame
        window (int): Rolling window in days (default 30)

    Returns:
        float: Annualized volatility as a percentage, e.g. 42.5 means 42.5%
    """
    if df.empty or len(df) < 2:
        return 0.0
    
    # Calculate log returns
    log_returns = np.log(df['Close'] / df['Close'].shift(1))
    
    # Calculate rolling standard deviation
    rolling_std = log_returns.rolling(window=window).std()
    
    # Annualize the volatility (assuming 252 trading days per year)
    annualized_vol = rolling_std * np.sqrt(252) * 100
    
    # Return the last value (most recent volatility)
    return float(annualized_vol.iloc[-1]) if not np.isnan(annualized_vol.iloc[-1]) else 0.0


def get_all_metrics(df: pd.DataFrame, forecast_df: pd.DataFrame) -> Dict:
    """
    Compute all key metrics and return as a dictionary.

    Parameters:
        df (pd.DataFrame): Historical OHLCV DataFrame
        forecast_df (pd.DataFrame): Forecast DataFrame

    Returns:
        dict: {
            'current_price': float,
            'predicted_price': float,
            'pct_change': float,
            'volatility': float
        }
    """
    current_price = get_current_price(df)
    predicted_price = get_predicted_price(forecast_df)
    pct_change = get_pct_change(current_price, predicted_price)
    volatility = get_volatility(df)
    
    return {
        'current_price': current_price,
        'predicted_price': predicted_price,
        'pct_change': pct_change,
        'volatility': volatility
    }