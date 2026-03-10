"""
Test script untuk menguji penanganan nilai negatif dalam forecasting
"""
import pandas as pd
from forecast_model import clip_negative_forecast

def test_clip_negative_forecast():
    """Test fungsi clip_negative_forecast dengan data dummy yang mengandung nilai negatif"""
    
    # Buat data dummy yang mengandung nilai negatif
    test_data = pd.DataFrame({
        'ds': pd.date_range(start='2023-01-01', periods=5, freq='D'),
        'yhat': [100, -50, 75, -20, 120],  # Beberapa nilai negatif
        'yhat_lower': [-10, -80, 50, -30, 100],  # Beberapa nilai negatif
        'yhat_upper': [150, -10, 100, -5, 140]   # Beberapa nilai negatif
    })
    
    print("Data asli:")
    print(test_data)
    print("\n" + "="*50 + "\n")
    
    # Terapkan fungsi clipping
    clipped_data = clip_negative_forecast(test_data)
    
    print("Data setelah clipping:")
    print(clipped_data)
    print("\n" + "="*50 + "\n")
    
    # Periksa apakah semua nilai sekarang positif
    print("Pengecekan nilai negatif:")
    print(f"Ada nilai negatif di yhat: {(clipped_data['yhat'] < 0).any()}")
    print(f"Ada nilai negatif di yhat_lower: {(clipped_data['yhat_lower'] < 0).any()}")
    print(f"Ada nilai negatif di yhat_upper: {(clipped_data['yhat_upper'] < 0).any()}")
    
    print("\nNilai terkecil di masing-masing kolom:")
    print(f"yhat: {clipped_data['yhat'].min()}")
    print(f"yhat_lower: {clipped_data['yhat_lower'].min()}")
    print(f"yhat_upper: {clipped_data['yhat_upper'].min()}")

def test_with_positive_data():
    """Test fungsi dengan data yang sudah positif untuk memastikan tidak merusak data yang valid"""
    
    # Buat data dummy yang semua nilainya positif
    test_data = pd.DataFrame({
        'ds': pd.date_range(start='2023-01-01', periods=5, freq='D'),
        'yhat': [100, 150, 75, 200, 120],
        'yhat_lower': [90, 140, 70, 180, 110],
        'yhat_upper': [110, 160, 80, 220, 130]
    })
    
    print("Data positif asli:")
    print(test_data)
    print("\n" + "="*50 + "\n")
    
    # Terapkan fungsi clipping
    clipped_data = clip_negative_forecast(test_data)
    
    print("Data setelah clipping (seharusnya tidak berubah banyak):")
    print(clipped_data)
    print("\n" + "="*50 + "\n")
    
    # Periksa apakah semua nilai tetap positif dan relatif sama (abaikan kolom 'ds')
    numeric_cols = ['yhat', 'yhat_lower', 'yhat_upper']
    print("Pengecekan:")
    print(f"Semua nilai numerik tetap positif: {((clipped_data[numeric_cols] > 0).all().all())}")
    print(f"Data tidak berubah secara signifikan: {((test_data[numeric_cols] - clipped_data[numeric_cols]).abs().max().max() < 1e-10)}")

if __name__ == "__main__":
    print("Testing fungsi penanganan nilai negatif dalam forecasting\n")
    
    print("Test 1: Data dengan nilai negatif")
    test_clip_negative_forecast()
    
    print("\n" + "="*70 + "\n")
    
    print("Test 2: Data dengan nilai positif")
    test_with_positive_data()
    
    print("\nTesting selesai!")