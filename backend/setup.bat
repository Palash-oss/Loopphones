@echo off
echo Starting LoopPhones Backend Setup...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

echo Python found
python --version

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy .env if not exists
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please update .env with your configuration
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Update .env with your database credentials
echo 2. Install and start PostgreSQL
echo 3. Install and start Redis
echo 4. Run the backend: python main.py
echo.
echo Or use Docker:
echo   docker-compose up
echo.
echo API Documentation will be available at:
echo   http://localhost:8000/docs

pause
