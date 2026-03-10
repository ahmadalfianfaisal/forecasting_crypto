#!/usr/bin/env python3
"""
Script untuk meng-update import statements di semua file Python
agar sesuai dengan struktur folder baru
"""

import os
import re

def update_imports_in_file(file_path):
    """Update import statements dalam satu file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Mapping lama ke baru
    import_mapping = {
        'from forecast_model import': 'from src.models.forecast_model import',
        'from model_trainer import': 'from src.models.model_trainer import',
        'from model_evaluation import': 'from src.models.model_evaluation import',
        'from model_storage import': 'from src.models.model_storage import',
        'from expanding_window_trainer import': 'from src.models.expanding_window_trainer import',
        'from data_loader import': 'from src.utils.data_loader import',
        'from metrics import': 'from src.utils.metrics import',
        'from scheduler import': 'from src.services.scheduler import',
        'import forecast_model': 'from src.models import forecast_model',
        'import model_trainer': 'from src.models import model_trainer',
        'import model_evaluation': 'from src.models import model_evaluation',
        'import model_storage': 'from src.models import model_storage',
        'import expanding_window_trainer': 'from src.models import expanding_window_trainer',
        'import data_loader': 'from src.utils import data_loader',
        'import metrics': 'from src.utils import metrics',
        'import scheduler': 'from src.services import scheduler',
    }
    
    original_content = content
    
    # Update import statements
    for old_import, new_import in import_mapping.items():
        content = content.replace(old_import, new_import)
    
    # Jika ada perubahan, tulis kembali file
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated imports in: {file_path}")
        return True
    else:
        print(f"No import changes needed in: {file_path}")
        return False

def main():
    """Main function untuk meng-update semua file Python"""
    root_dir = "."
    
    # Cari semua file Python
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Lewati folder __pycache__ dan node_modules
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                # Hanya proses file di root directory
                if root == root_dir:
                    python_files.append(full_path)
    
    print(f"Found {len(python_files)} Python files to process")
    
    for py_file in python_files:
        print(f"Processing: {py_file}")
        update_imports_in_file(py_file)
    
    print("Import update completed!")

if __name__ == "__main__":
    main()