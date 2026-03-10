# INSTRUKSI LANGKAH DEMI LANGKAH - JALANKAN LOKAL

## LANGKAH 1: SETUP AWAL
1. Buka Command Prompt sebagai Administrator
2. Navigasi ke folder proyek:
   ```
   cd C:\Users\admin\alibaba-cloud\forecast-vibecoding
   ```
3. Jalankan setup:
   ```
   setup_windows.bat
   ```

## LANGKAH 2: JALANKAN APLIKASI DAN SCHEDULER
1. Pastikan Anda masih di folder proyek
2. Jalankan aplikasi dan scheduler bersamaan:
   ```
   start_both_apps.bat
   ```

## LANGKAH 3: AKSES APLIKASI
1. Buka browser
2. Akses: http://localhost:8050
3. Aplikasi akan berjalan di dua jendela Command Prompt:
   - Satu untuk aplikasi utama
   - Satu untuk scheduled training

## LANGKAH 4: MONITORING
- Jaga kedua jendela Command Prompt tetap terbuka
- Aplikasi akan terus berjalan selama komputer menyala
- Scheduled training akan berjalan otomatis di background

## CATATAN PENTING
- Jangan tutup jendela Command Prompt yang muncul
- Aplikasi hanya bisa diakses dari komputer lokal
- Scheduled training akan tetap berjalan selama aplikasi aktif
- Untuk menghentikan, tutup jendela Command Prompt atau tekan Ctrl+C di masing-masing jendela

## TROUBLESHOOTING
Jika aplikasi tidak bisa diakses di localhost:8050:
- Pastikan port 8050 tidak digunakan aplikasi lain
- Cek apakah kedua jendela Command Prompt berjalan tanpa error
- Restart aplikasi dengan menutup jendela dan jalankan ulang start_both_apps.bat

SELESAI! Aplikasi forecasting dengan scheduled training sekarang berjalan secara lokal di komputer Anda.