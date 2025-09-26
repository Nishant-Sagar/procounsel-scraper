@echo off
SET VENV_NAME=scrape

REM Create venv if it doesn't exist
IF NOT EXIST "%VENV_NAME%" (
    echo Creating virtual environment...
    python -m venv %VENV_NAME%
) ELSE (
    echo Virtual environment already exists.
)

REM Activate venv
echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
IF EXIST requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) ELSE (
    echo No requirements.txt found!
)

echo Setup complete! Virtual environment '%VENV_NAME%' is ready.
pause
