#!/bin/bash

# AkShare Installation Script
# This script installs AkShare and its dependencies

echo "Installing AkShare..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 not found. Please install Python and pip first."
    exit 1
fi

# Install AkShare
pip3 install akshare pandas numpy matplotlib

# Verify installation
python3 -c "import akshare; print(f'AkShare version: {akshare.__version__}')"

echo "AkShare installed successfully!"
echo ""
echo "Quick test:"
python3 -c "import akshare as ak; print('Testing AkShare...'); df = ak.stock_zh_a_spot_em(); print(f'Loaded {len(df)} stocks')"

echo ""
echo "For more information, see:"
echo "  - https://akshare.akfamily.xyz/"
echo "  - https://github.com/akfamily/akshare"