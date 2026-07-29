@echo off
REM Launch the Hack Our Drone local server on Windows.
REM Usage: double-click this file, or run  serve.bat  from a terminal.
where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0serve.py" %*
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        py "%~dp0serve.py" %*
    ) else (
        echo Python 3 was not found. Install it from https://www.python.org/downloads/
        pause
    )
)
