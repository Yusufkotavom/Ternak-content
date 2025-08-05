@echo off
echo ========================================
echo Auto Content Generator - Windows Installer
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating directories...
if not exist "output" mkdir output
if not exist "output\images" mkdir output\images
if not exist "templates" mkdir templates
if not exist "static" mkdir static

echo.
echo Copying environment file...
if not exist ".env" (
    copy .env.example .env
    echo Please edit .env file with your API keys
) else (
    echo .env file already exists
)

echo.
echo Running Windows compatibility test...
python test_windows.py

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo To start the application:
echo   python run.py
echo.
echo To run system tests:
echo   python test_system.py
echo.
echo To test individual components:
echo   python test_windows.py
echo.
pause