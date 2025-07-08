#!/usr/bin/env python3
"""
Setup script for Solana Wallet P&L Tracker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="solana-pnl-tracker",
    version="1.0.0",
    author="Solana P&L Tracker",
    description="Track profit and loss for all tokens in a Solana wallet and export to spreadsheet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/solana-pnl-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "solana-pnl=solana_pnl_tracker:main",
        ],
    },
)