@echo off
set FILE=main.tex
set LASTTIME=

echo Watching %FILE% for changes...

:loop
for %%A in (%FILE%) do set MODTIME=%%~tA

if not "%MODTIME%"=="%LASTTIME%" (
    set LASTTIME=%MODTIME%
    echo.
    echo Change detected. Compiling...
    pdflatex -interaction=nonstopmode %FILE%
)

timeout /t 1 >nul
goto loop