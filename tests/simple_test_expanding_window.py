#!/usr/bin/env python
"""
Simple test script to verify the expanding window training functionality
"""

from expanding_window_trainer import expanding_window_training, train_single_model_expanding_window
from data_loader import get_available_tickers
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_simple_expanding_window():
    """Test the expanding window training with minimal parameters for quick verification"""
    tickers = get_available_tickers()
    
    print("="*80)
    print("SIMPLE TEST OF EXPANDING WINDOW TRAINING APPROACH")
    print("="*80)
    
    # Test with just 2 phases to verify functionality quickly
    for ticker_info in tickers[:1]:  # Just test with the first ticker
        ticker = ticker_info['value']
        ticker_name = ticker_info['label'].split(' — ')[1]  # Extract name like "Bitcoin"
        
        print(f"\nTesting {ticker} — {ticker_name}")
        print("-" * 60)
        
        try:
            # Test the expanding window training function with just 2 phases for quick test
            results = expanding_window_training(ticker, initial_train_months=18, total_train_months=20)
            
            print(f"Number of phases completed: {len(results)}")
            
            if results:
                for result in results:
                    print(f"Phase {result['phase']}: Train months={result['train_months']}, "
                          f"Test period={result['test_period']}, "
                          f"Met targets={result['met_targets']}")
                    print(f"  Metrics: MAE={result['metrics']['mae']:.4f}, "
                          f"RMSE={result['metrics']['rmse']:.4f}, "
                          f"MAPE={result['metrics']['mape']:.2f}%, "
                          f"Direction Acc={result['metrics']['direction_accuracy']:.2f}%")
            
            print(f"STATUS: SUCCESS - Expanding window training completed for {ticker}")
            
        except Exception as e:
            print(f"ERROR in expanding window training for {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"STATUS: FAILED - Could not complete expanding window training for {ticker}")
    
    print("\n" + "="*80)
    print("SIMPLE EXPANDING WINDOW TRAINING TESTS COMPLETE")
    print("="*80)


def test_full_pipeline_simple():
    """Test the full pipeline with the new expanding window approach (with limited phases)"""
    tickers = get_available_tickers()
    
    print("="*80)
    print("SIMPLE TEST OF FULL PIPELINE WITH EXPANDING WINDOW APPROACH")
    print("="*80)
    
    # For the full pipeline test, we'll modify the function to use fewer phases
    for ticker_info in tickers[:1]:  # Just test with the first ticker
        ticker = ticker_info['value']
        ticker_name = ticker_info['label'].split(' — ')[1]  # Extract name like "Bitcoin"
        
        print(f"\nTesting full pipeline for {ticker} — {ticker_name}")
        print("-" * 60)
        
        try:
            # For this simple test, we'll call the expanding window function directly with limited phases
            from expanding_window_trainer import expanding_window_training
            results = expanding_window_training(ticker, initial_train_months=18, total_train_months=19)
            
            if results:
                print(f"SUCCESS: Completed {len(results)} phases for {ticker}")
                # Simulate the rest of the pipeline
                from model_evaluation import champion_challenger_evaluation, log_model_to_mlflow, promote_model_to_production
                from model_storage import save_model
                from data_loader import download_data, prepare_prophet_df
                
                # Get the final model from the last phase
                final_model = results[-1]['model']
                historical_df = download_data(ticker, period="2y")
                
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
                        print(f"Successfully trained, evaluated, and promoted model for {ticker}")
                    else:
                        print(f"Failed to save model for {ticker}")
                else:
                    print(f"Expanding window model for {ticker} did not outperform champion, keeping current model")
                
                print(f"STATUS: SUCCESS - Full pipeline completed for {ticker}")
            else:
                print(f"STATUS: FAILED - No results returned for {ticker}")
            
        except Exception as e:
            print(f"ERROR in full pipeline for {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"STATUS: FAILED - Could not complete full pipeline for {ticker}")
    
    print("\n" + "="*80)
    print("SIMPLE FULL PIPELINE TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_simple_expanding_window()
    test_full_pipeline_simple()