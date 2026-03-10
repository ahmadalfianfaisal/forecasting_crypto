# PowerShell script untuk menjalankan aplikasi forecasting secara lokal dengan background jobs

Write-Host "Setting up local background jobs for forecast application..." -ForegroundColor Green

# Nama job
$AppJobName = "ForecastApp"
$SchedulerJobName = "ModelScheduler"

# Cek apakah virtual environment aktif
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Please activate your virtual environment first." -ForegroundColor Red
    exit 1
}

# Hapus job lama jika ada
Get-Job -Name $AppJobName -ErrorAction SilentlyContinue | Remove-Job -Force
Get-Job -Name $SchedulerJobName -ErrorAction SilentlyContinue | Remove-Job -Force

# Jalankan aplikasi Dash sebagai background job
Write-Host "Starting Forecast Application as background job..." -ForegroundColor Yellow
$AppScriptBlock = {
    Set-Location "C:\Users\admin\alibaba-cloud\forecast-vibecoding"
    & "venv\Scripts\Activate.ps1"
    python run_app.py
}
Start-Job -ScriptBlock $AppScriptBlock -Name $AppJobName

# Jalankan scheduler sebagai background job
Write-Host "Starting Model Scheduler as background job..." -ForegroundColor Yellow
$SchedulerScriptBlock = {
    Set-Location "C:\Users\admin\alibaba-cloud\forecast-vibecoding"
    & "venv\Scripts\Activate.ps1"
    python run_scheduler.py
}
Start-Job -ScriptBlock $SchedulerScriptBlock -Name $SchedulerJobName

# Tampilkan status
Write-Host "`nBackground jobs created:" -ForegroundColor Green
Get-Job

Write-Host "`nApplication is accessible at: http://localhost:8050" -ForegroundColor Cyan
Write-Host "Note: Jobs will stop when PowerShell session ends." -ForegroundColor Yellow
Write-Host "To keep jobs running after closing PowerShell, use a Windows service or scheduled task." -ForegroundColor Yellow

# Opsi untuk melihat output
Write-Host "`nTo see job output, use:" -ForegroundColor White
Write-Host "Receive-Job -Name '$AppJobName'" -ForegroundColor Gray
Write-Host "Receive-Job -Name '$SchedulerJobName'" -ForegroundColor Gray