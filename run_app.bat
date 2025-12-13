REM ========= Backend 起動 =========
start "BACKEND" cmd /k "call C:\dev\cases\portfolio\0043_Finance_app_V004\.venv\Scripts\activate.bat & cd /d C:\dev\cases\portfolio\0043_Finance_app_V004 & python app.py"


REM ========= Frontend 起動 =========
cd /d C:\dev\cases\portfolio\0043_Finance_app_V004\frontend
start "FRONTEND" cmd /k npm run dev
