#!/usr/bin/env python
"""
Test script to verify the expanding window training functionality
"""

from expanding_window_trainer import expanding_window_training, train_single_model_expanding_window
from data_loader import get_available_tickers
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_expanding_window():
    """Test the expanding window training with different assets"""
    tickers = get_available_tickers()
    
    print("="*80)
    print("TESTING EXPANDING WINDOW TRAINING APPROACH")
    print("="*80)
    
    for ticker_info in tickers:
        ticker = ticker_info['value']
        ticker_name = ticker_info['label'].split(' — ')[1]  # Extract name like "Bitcoin"
        
        print(f"\nTesting {ticker} — {ticker_name}")
        print("-" * 60)
        
        try:
            # Test the expanding window training function
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
    print("EXPANDING WINDOW TRAINING TESTS COMPLETE")
    print("="*80)


def test_full_pipeline():
    """Test the full pipeline with the new expanding window approach"""
    tickers = get_available_tickers()
    
    print("="*80)
    print("TESTING FULL PIPELINE WITH EXPANDING WINDOW APPROACH")
    print("="*80)
    
    for ticker_info in tickers:
        ticker = ticker_info['value']
        ticker_name = ticker_info['label'].split(' — ')[1]  # Extract name like "Bitcoin"
        
        print(f"\nTesting full pipeline for {ticker} — {ticker_name}")
        print("-" * 60)
        
        try:
            # Test the full pipeline training function
            success = train_single_model_expanding_window(ticker)
            
            if success:
                print(f"STATUS: SUCCESS - Full pipeline completed for {ticker}")
            else:
                print(f"STATUS: FAILED - Full pipeline failed for {ticker}")
            
        except Exception as e:
            print(f"ERROR in full pipeline for {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"STATUS: FAILED - Could not complete full pipeline for {ticker}")
    
    print("\n" + "="*80)
    print("FULL PIPELINE TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_expanding_window()
    test_full_pipeline()