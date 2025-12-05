@echo off

REM 仮想環境を有効化
REM call C:\dev\cases\portfolio\0043_Finance_app_V004\.venv\Scripts\activate.bat

REM ========= Backend 起動 =========
REM start "BACKEND" cmd /k python C:\dev\cases\portfolio\0043_Finance_app_V004\app.py
start "BACKEND" cmd /k "call \"C:\dev\cases\portfolio\0043_Finance_app_V004\.venv\Scripts\activate.bat\" & cd /d C:\dev\cases\portfolio\0043_Finance_app_V004 & python app.py"

REM ========= Frontend 起動 =========
cd /d C:\dev\cases\portfolio\0043_Finance_app_V004\frontend
start "FRONTEND" cmd /k npm run dev
