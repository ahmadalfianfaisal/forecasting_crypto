import logging
from typing import Dict
from prophet import Prophet
import pandas as pd
from src.utils.data_loader import download_data, prepare_prophet_df
from src.models.model_storage import save_model, delete_old_models
from src.models.model_evaluation import champion_challenger_evaluation, log_model_to_mlflow, promote_model_to_production

logger = logging.getLogger(__name__)

def train_single_model(ticker: str, use_expanding_window: bool = False) -> bool:
    """
    Train a Prophet model for a single ticker with champion-challenger evaluation

    Args:
        ticker: Asset ticker symbol (e.g., 'BTC-USD')
        use_expanding_window: Whether to use expanding window training approach

    Returns:
        True if training and evaluation successful, False otherwise
    """
    if use_expanding_window:
        # Use the expanding window training approach
        from src.models.expanding_window_trainer import train_single_model_expanding_window
        return train_single_model_expanding_window(ticker)
    
    try:
        logger.info(f"Starting model training for {ticker}")

        # Download latest data
        historical_df = download_data(ticker, period="2y")

        if len(historical_df) < 30:
            raise ValueError(f"Insufficient data for {ticker}. Need at least 30 days of data, got {len(historical_df)} days.")

        # Prepare data for Prophet
        prophet_df = prepare_prophet_df(historical_df)

        # Additional data validation for Prophet
        if prophet_df.isnull().any().any():
            # Remove any rows with null values
            prophet_df = prophet_df.dropna()

        if len(prophet_df) < 30:
            raise ValueError(f"Insufficient clean data for {ticker} after preprocessing. Need at least 30 days of data.")

        # Ensure the data is sorted by date
        prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)

        # Remove duplicate dates if any
        prophet_df = prophet_df.drop_duplicates(subset=['ds'])

        # Check again after cleaning
        if len(prophet_df) < 30:
            raise ValueError(f"Insufficient clean data for {ticker} after removing duplicates. Need at least 30 days of data.")

        # Train the Prophet model with multiple fallback strategies
        model = None
        error_messages = []

        # First attempt with default parameters
        try:
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,  # Reduced to prevent overfitting
                seasonality_mode='multiplicative',  # Better for volatile data
                seasonality_prior_scale=10,
                changepoint_range=0.8  # Allow changes in the last 80% of the series
            )
            model.fit(prophet_df)
        except Exception as e:
            error_messages.append(f"Default parameters failed: {str(e)}")

            # Second attempt with reduced seasonality
            try:
                model = Prophet(
                    yearly_seasonality=min(len(prophet_df)//365, 2) if len(prophet_df) >= 365 else False,
                    weekly_seasonality=min(len(prophet_df)//7, 3) if len(prophet_df) >= 14 else False,
                    daily_seasonality=False,
                    changepoint_prior_scale=0.05,
                    seasonality_mode='additive',
                    seasonality_prior_scale=5.0
                )
                model.fit(prophet_df)
            except Exception as e2:
                error_messages.append(f"Reduced seasonality failed: {str(e2)}")

                # Third attempt with minimal parameters
                try:
                    model = Prophet(
                        yearly_seasonality=False,
                        weekly_seasonality=False,
                        daily_seasonality=False,
                        changepoint_prior_scale=0.1,
                        seasonality_mode='additive',
                        seasonality_prior_scale=1.0
                    )
                    model.fit(prophet_df)
                except Exception as e3:
                    error_messages.append(f"Minimal parameters failed: {str(e3)}")

                    # Final attempt with very basic parameters
                    try:
                        # Ensure we have at least 2 data points
                        if len(prophet_df) < 2:
                            raise ValueError(f"Not enough data points after cleaning: {len(prophet_df)}")

                        # Use only the first and last points if very limited data
                        if len(prophet_df) < 10:
                            prophet_df = prophet_df.iloc[[0, -1]]

                        model = Prophet(
                            yearly_seasonality=False,
                            weekly_seasonality=False,
                            daily_seasonality=False,
                            changepoint_prior_scale=0.5,
                            seasonality_mode='additive',
                            seasonality_prior_scale=0.01
                        )
                        model.fit(prophet_df)
                    except Exception as e4:
                        error_messages.append(f"Final fallback failed: {str(e4)}")
                        raise ValueError(f"All attempts to train Prophet model failed for {ticker}. Error messages: {'; '.join(error_messages)}")

        # Perform champion-challenger evaluation
        should_promote = champion_challenger_evaluation(ticker, model, historical_df)

        if should_promote:
            # Log the model to MLflow as a candidate first
            run_id = log_model_to_mlflow(ticker, model, historical_df, stage="candidate")

            # Promote to production
            promote_model_to_production(run_id, ticker)

            # Save the model locally as well
            success = save_model(model, ticker)
            if success:
                logger.info(f"Successfully trained, evaluated, and promoted model for {ticker}")
                return True
            else:
                logger.error(f"Failed to save model for {ticker}")
                return False
        else:
            logger.info(f"Challenger model for {ticker} did not outperform champion, keeping current model")
            return True  # Return True since this is not an error, just no improvement

    except Exception as e:
        logger.error(f"Error training model for {ticker}: {str(e)}")
        return False

def train_all_models(use_expanding_window: bool = False) -> Dict[str, bool]:
    """
    Train models for all supported tickers with champion-challenger evaluation

    Args:
        use_expanding_window: Whether to use expanding window training approach

    Returns:
        Dictionary mapping ticker symbols to training success status
    """
    from src.utils.data_loader import get_available_tickers

    tickers = [item['value'] for item in get_available_tickers()]
    results = {}

    for ticker in tickers:
        logger.info(f"Training model for {ticker}")
        results[ticker] = train_single_model(ticker, use_expanding_window=use_expanding_window)

    return results