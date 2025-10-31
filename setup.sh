#!/bin/bash
# Setup script for Insolvency Study Assistant
# Phase 1: Environment Setup

echo "========================================="
echo "Insolvency Study Assistant - Setup"
echo "Phase 1: Environment Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment first:"
    echo "  source venv/bin/activate"
    echo "Then run this script again, or manually run:"
    echo "  pip install -r requirements.txt"
    exit 0
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ IMPORTANT: Edit .env file and add your Gemini API key!"
    echo "  Get your key from: https://aistudio.google.com/apikey"
else
    echo "✓ .env file already exists"
fi
echo ""

# Test CLI
echo "Testing CLI..."
python3 src/cli/main.py test

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ Setup Complete!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env file and add your Gemini API key"
    echo "  2. Run: python3 src/cli/main.py info"
    echo "  3. Run: python3 test_api.py  (to test API connection)"
    echo ""
else
    echo "❌ CLI test failed"
    exit 1
fi
