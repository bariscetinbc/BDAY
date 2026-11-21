@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Installing the packaging tool (first time only)...
python -m pip install --upgrade pyinstaller
echo Checking the calculations...
python selftest.py || goto :error
echo Building the Windows program...
pyinstaller --noconfirm --clean bday.spec || goto :error
echo.
echo Done. Your program is: dist\BDAY.exe
echo You can copy that single file anywhere on the computer and double-click it.
pause
exit /b 0
:error
echo The build did not finish. Please send this window's text to the person who made it.
pause
exit /b 1
