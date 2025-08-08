@echo off
title HoneyNet Enterprise API Server
echo.
echo ========================================
echo   🛡️  HoneyNet Enterprise API Server
echo ========================================
echo.

echo 📦 Installing Enterprise dependencies...
pip install -r requirements_enterprise.txt

echo.
echo 🚀 Starting Enterprise API server...
echo.
echo 📊 Enterprise Dashboard: http://localhost:8001/enterprise/docs
echo 🌐 API Documentation: http://localhost:8001/enterprise/redoc
echo 💼 Dashboard UI: Open enterprise_dashboard.html in browser
echo 💰 Pricing Page: Open pricing_page.html in browser
echo.

python enterprise_api.py

pause
