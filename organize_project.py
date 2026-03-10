#!/usr/bin/env python3
"""
Script untuk mengorganisir file-file ke struktur folder yang lebih rapi
"""

import os
import shutil

def create_folder_structure():
    """Membuat struktur folder"""
    folders = [
        'src',
        'src/views',
        'src/models', 
        'src/utils',
        'src/services',
        'src/controllers',
        'config',
        'tests',
        'docs'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        # Buat file __init__.py di setiap folder Python
        init_file = os.path.join(folder, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Package initialization file"""\n')

def move_files():
    """Memindahkan file-file ke folder yang sesuai"""
    
    # Mapping file ke folder
    file_mapping = {
        # Views
        'app.py': 'src/views/',
        
        # Models
        'forecast_model.py': 'src/models/',
        'model_trainer.py': 'src/models/',
        'model_evaluation.py': 'src/models/',
        'model_storage.py': 'src/models/',
        'expanding_window_trainer.py': 'src/models/',
        
        # Utils
        'data_loader.py': 'src/utils/',
        'metrics.py': 'src/utils/',
        
        # Services
        'scheduler.py': 'src/services/',
        'scheduler_daemon.py': 'src/services/',
        
        # Config
        'gunicorn_config.py': 'config/',
        'wsgi.py': 'config/',
        'model_scheduler.service': 'config/',
        
        # Tests
        'test_forecast.py': 'tests/',
        'test_expanding_window.py': 'tests/',
        'test_negative_handling.py': 'tests/',
        'simple_test_expanding_window.py': 'tests/',
        
        # Docs
        'DEPLOY_TO_ALIBABA_CLOUD.md': 'docs/',
        'DEPLOYMENT_CHECKLIST.md': 'docs/',
    }
    
    moved_files = []
    
    for source_file, dest_folder in file_mapping.items():
        source_path = source_file
        dest_path = os.path.join(dest_folder, source_file)
        
        if os.path.exists(source_path):
            try:
                shutil.move(source_path, dest_path)
                print(f"Moved: {source_path} -> {dest_path}")
                moved_files.append((source_path, dest_path))
            except Exception as e:
                print(f"Error moving {source_path}: {e}")
        else:
            print(f"File not found: {source_path}")
    
    return moved_files

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
    
    # Juga update referensi ke file-file yang dipindahkan
    content = content.replace("'../config/", "'config/")
    content = content.replace("'config/", "'src/config/")
    
    # Jika ada perubahan, tulis kembali file
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated imports in: {file_path}")
        return True
    else:
        return False

def update_all_imports():
    """Update import statements di semua file yang dipindahkan"""
    
    # File-file yang kemungkinan besar mengandung import statements
    files_to_update = [
        'src/views/app.py',
        'src/services/scheduler_daemon.py',
        'src/services/scheduler.py',
        'src/models/model_trainer.py',
        'src/models/forecast_model.py',
        'config/wsgi.py'
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            update_imports_in_file(file_path)

def main():
    print("Creating folder structure...")
    create_folder_structure()
    
    print("Moving files to appropriate folders...")
    moved_files = move_files()
    
    print("Updating import statements...")
    update_all_imports()
    
    print("Organization completed!")
    print(f"Files moved: {len(moved_files)}")
    
    print("\nNext steps:")
    print("1. Verify all files are in correct locations")
    print("2. Test the application to ensure imports work correctly")
    print("3. Update any remaining hardcoded paths in the code")
    print("4. Run tests to ensure everything works properly")

if __name__ == "__main__":
    main()