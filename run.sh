#!/bin/bash

# Quick run script for Solana P&L Tracker

echo "🚀 Starting Solana Wallet P&L Tracker..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the tracker
python solana_pnl_tracker.py

# Deactivate virtual environment
deactivate

echo "✅ Done! Check the generated Excel file for your P&L analysis."