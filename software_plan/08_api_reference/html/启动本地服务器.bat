@echo off
rem Serve the docs at http://localhost:8899 for maximum fidelity.
rem Requires Python (py or python on PATH); otherwise opens the file directly.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    start "" http://localhost:8899/index.html
    py -m http.server 8899
    goto :eof
)
where python >nul 2>nul
if %errorlevel%==0 (
    start "" http://localhost:8899/index.html
    python -m http.server 8899
    goto :eof
)
echo Python was not found on PATH. Opening the file directly instead.
start "" "%~dp0index.html"
pause
