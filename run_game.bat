@echo off
echo Running Goblinball...
echo.

:: Get the directory where the bat file is located
set SCRIPT_DIR=%~dp0

:: Go to the project root directory
cd %SCRIPT_DIR%

:: Run the game from the project root - this will find the goblinball module correctly
python -m goblinball.main

:: Pause to keep the window open in case of errors
echo.
if %ERRORLEVEL% NEQ 0 (
    echo Game exited with errors. Check the logs in goblinball/logs/ for details.
    pause
) else (
    echo Game closed successfully.
    timeout /t 3
) 