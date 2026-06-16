@echo off
REM Discord-Minecraft Bot Startup Script
echo Starting Discord-Minecraft Bot...
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    pause
    exit /b 1
)

REM Run the bot
.venv\Scripts\python.exe bot.py

pause
