@echo off
:menu
cls
echo ===============================
echo   PHISHING CLASSIFIER DEMO
echo ===============================
echo.
echo Available sample files:
dir /b demo_assets\samples
echo.
set /p FNAME=Enter filename to scan (or Q to quit): 

if /I "%FNAME%"=="Q" goto end
if "%FNAME%"=="" goto menu

echo.
echo Scanning %FNAME% ...
python predict.py --file demo_assets/samples/%FNAME% --threshold 0.7

echo.
pause
goto menu

:end
echo Exiting demo.
pause
