@echo off
echo 🚀 Starting Solana Wallet P&L Tracker...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the tracker
python solana_pnl_tracker.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo ✅ Done! Check the generated Excel file for your P&L analysis.
pause