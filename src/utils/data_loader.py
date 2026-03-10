import yfinance as yf
import pandas as pd
from typing import Dict, List
from functools import lru_cache

# Module-level cache to store downloaded data
_DATA_CACHE: Dict[str, pd.DataFrame] = {}

# Supported tickers
SUPPORTED_TICKERS = [
    {'label': 'BTC — Bitcoin', 'value': 'BTC-USD'},
    {'label': 'ETH — Ethereum', 'value': 'ETH-USD'},
    {'label': 'SOL — Solana', 'value': 'SOL-USD'}
]

def prepare_prophet_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert OHLCV DataFrame to Prophet format.

    Parameters:
        df (pd.DataFrame): DataFrame with 'Date' and 'Close' columns

    Returns:
        pd.DataFrame: DataFrame with columns ['ds', 'y'] where ds is datetime and y is float
    """
    # Create a copy to avoid modifying the original DataFrame
    prophet_df = df[['Date', 'Close']].copy()

    # Rename columns to Prophet format
    prophet_df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

    # Ensure 'ds' is datetime and 'y' is numeric
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    # Remove timezone info if present (Prophet doesn't support timezone-aware datetimes)
    if prophet_df['ds'].dt.tz is not None:
        prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)
    prophet_df['y'] = pd.to_numeric(prophet_df['y'])

    return prophet_df

def download_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Download historical OHLCV data from Yahoo Finance.

    Parameters:
        ticker (str): Yahoo Finance ticker symbol, e.g. 'BTC-USD'
        period (str): Data period to download, e.g. '2y' for 2 years

    Returns:
        pd.DataFrame: Clean DataFrame with columns [Date, Open, High, Low, Close, Volume]
                      Date is a datetime column (not index).
    """
    # Check if data is already cached
    if ticker in _DATA_CACHE:
        return _DATA_CACHE[ticker].copy()
    
    try:
        # Download data from yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Rename Date column to ensure consistency
        df.rename(columns={'Date': 'Date'}, inplace=True)
        
        # Ensure Date column is datetime type
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Select only the required columns
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Drop any rows with NaN values
        df.dropna(inplace=True)
        
        # Sort by date to ensure chronological order
        df.sort_values(by='Date', inplace=True)
        
        # Cache the data
        _DATA_CACHE[ticker] = df.copy()
        
        return df
    
    except Exception as e:
        print(f"Error downloading data for {ticker}: {str(e)}")
        # Return an empty DataFrame in case of error
        return pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])


def clear_cache(ticker: str) -> None:
    """
    Remove cached data for a given ticker to force a fresh download.

    Parameters:
        ticker (str): Yahoo Finance ticker symbol to remove from cache
    """
    if ticker in _DATA_CACHE:
        del _DATA_CACHE[ticker]


def get_available_tickers() -> List[Dict]:
    """
    Return list of supported assets as Dash dropdown options.

    Returns:
        list[dict]: e.g. [{'label': 'BTC — Bitcoin', 'value': 'BTC-USD'}, ...]
    """
    return SUPPORTED_TICKERS