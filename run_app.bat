@echo off

REM 仮想環境を有効化
call C:\dev\cases\portfolio\0043_Fianance_app_V004\.venv\Scripts\activate.bat

REM ========= Backend 起動 =========
start "BACKEND" cmd /k python C:\dev\cases\portfolio\0043_Fianance_app_V004\app.py


REM ========= Frontend 起動 =========
cd /d C:\dev\cases\portfolio\0043_Fianance_app_V004\frontend
start "FRONTEND" cmd /k npm run dev
