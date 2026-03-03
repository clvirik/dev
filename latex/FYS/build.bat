@echo off
setlocal enabledelayedexpansion

echo Watching all .tex files in %CD%
echo Press Ctrl+C to stop.

REM ===============================
REM Initialize hashes for all .tex files
REM ===============================
for %%f in (*.tex) do (
    call :sethash "%%f"
)

:loop
set "CHANGED_FILE="

REM Detect new files and changes
for %%f in (*.tex) do (
    if not defined HASH_%%f (
        REM New file detected
        call :sethash "%%f"
        set "CHANGED_FILE=%%f"
    ) else (
        call :checkhash "%%f"
    )
)

if defined CHANGED_FILE (
    echo --------------------------------------
    echo Changes detected in !CHANGED_FILE! at %TIME%.
    echo Recompiling !CHANGED_FILE!...
    texify --pdf --clean "!CHANGED_FILE!"
    echo Done!
    echo --------------------------------------
)

timeout /t 1 /nobreak >nul
goto loop

REM ===============================
REM Subroutines
REM ===============================

:sethash
set "FILE=%~1"
for /f "skip=1 tokens=1" %%h in ('certutil -hashfile "%FILE%" MD5') do (
    if not defined HASH_%FILE% set "HASH_%FILE%=%%h"
)
exit /b

:checkhash
set "FILE=%~1"
set "CURHASH="
for /f "skip=1 tokens=1" %%h in ('certutil -hashfile "%FILE%" MD5') do (
    if not defined CURHASH set "CURHASH=%%h"
)

if NOT "!CURHASH!"=="!HASH_%FILE%!" (
    set "HASH_%FILE%=!CURHASH!"
    set "CHANGED_FILE=%FILE%"
)
exit /b