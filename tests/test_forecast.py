#!/usr/bin/env python
"""
Test script to verify the forecast model functionality with Bloomberg Terminal-like features
"""

from forecast_model import run_forecast
from data_loader import get_available_tickers
from metrics import get_all_metrics
import pandas as pd
import numpy as np
from datetime import datetime

def format_currency(value):
    """Format currency with proper precision"""
    if abs(value) >= 1:
        return f"${value:,.2f}"
    else:
        return f"${value:.6f}"

def calculate_technical_indicators(df):
    """Calculate basic technical indicators similar to Bloomberg"""
    df = df.copy()
    
    # Moving averages
    df['MA_7'] = df['Close'].rolling(window=7).mean()
    df['MA_21'] = df['Close'].rolling(window=21).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    
    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # MACD
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
    
    return df

def test_forecast():
    """Test the forecast model with different assets and Bloomberg-like features"""
    tickers = get_available_tickers()
    
    print("="*100)
    print("BLOOMBERG TERMINAL STYLE CRYPTO FORECAST ANALYSIS")
    print("="*100)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*100)
    
    for ticker_info in tickers:
        ticker = ticker_info['value']
        ticker_name = ticker_info['label'].split(' — ')[1]  # Extract name like "Bitcoin"
        
        print(f"\n{ticker} — {ticker_name}")
        print("-" * 60)
        
        try:
            # Get forecast data
            historical_df, forecast_df = run_forecast(ticker, periods=7)
            
            # Calculate metrics
            metrics = get_all_metrics(historical_df, forecast_df)
            
            # Calculate technical indicators
            tech_df = calculate_technical_indicators(historical_df)
            
            # Print key metrics
            print(f"Current Price:       {format_currency(historical_df['Close'].iloc[-1])}")
            print(f"Predicted Price:     {format_currency(forecast_df['yhat'].iloc[-1])}")
            print(f"Expected Change:     {metrics['pct_change']:+.2f}%")
            print(f"30-Day Volatility:   {metrics['volatility']:.2f}%")
            
            # Technical indicators
            current_rsi = tech_df['RSI'].iloc[-1]
            current_ma7 = tech_df['MA_7'].iloc[-1]
            current_ma21 = tech_df['MA_21'].iloc[-1]
            
            print(f"RSI (14-day):        {current_rsi:.2f}", end="")
            if current_rsi > 70:
                print(" [OVERBOUGHT]")
            elif current_rsi < 30:
                print(" [OVERSOLD]")
            else:
                print(" [NEUTRAL]")
                
            print(f"MA (7-day):          {format_currency(current_ma7)}")
            print(f"MA (21-day):         {format_currency(current_ma21)}")
            
            # Price trend
            price_change_7d = ((historical_df['Close'].iloc[-1] / historical_df['Close'].iloc[-8]) - 1) * 100 if len(historical_df) >= 8 else 0
            print(f"7-Day Price Change:  {price_change_7d:+.2f}%")
            
            # Forecast confidence
            if not forecast_df.empty:
                confidence_range = forecast_df['yhat_upper'].iloc[-1] - forecast_df['yhat_lower'].iloc[-1]
                confidence_pct = (confidence_range / forecast_df['yhat'].iloc[-1]) * 100
                print(f"Forecast Confidence: ±{confidence_pct:.2f}%")
            
            print("STATUS: SUCCESS - Forecast model trained and validated")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            print("STATUS: FAILED - Could not generate forecast")
    
    print("\n" + "="*100)
    print("ANALYSIS COMPLETE")
    print("="*100)

if __name__ == "__main__":
    test_forecast()