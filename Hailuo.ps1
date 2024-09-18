$OutputEncoding = [System.Text.Encoding]::UTF8
# [Console]::BackgroundColor = [ConsoleColor]::DarkGray
# $host.UI.RawUI.BackgroundColor = "DarkGray"
$host.UI.RawUI.ForegroundColor = "White"

$currentDateTime = Get-Date
Write-Host "Current Date and Time: $currentDateTime"

$scriptPath = "./venv/Scripts/Activate.ps1"
Invoke-Expression "& $scriptPath"

$pythonScriptPath = "./HaiLuoAI.py"
& python $pythonScriptPath