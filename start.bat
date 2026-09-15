@echo off
chcp 65001 >nul
title FSOCIETY PC CONTROL — ЗАПУСК

cd /d "%~dp0"

echo ============================================================
echo           FSOCIETY PC CONTROL — ЗАПУСК
echo ============================================================
echo.

REM ===== ПУТЬ К PYTHON =====
set PYTHON=C:\Users\markm\AppData\Local\Programs\Python\Python312\pythonw.exe

REM ===== ПРОВЕРКА PYTHON =====
if not exist "%PYTHON%" (
    echo [X] Python не найден по пути: %PYTHON%
    echo Проверь путь через команду: where pythonw
    pause
    exit /b
)
echo [OK] Python найден
echo.

REM ===== ПРОВЕРКА ФАЙЛОВ =====
if not exist "commands.py" (
    echo [X] commands.py не найден!
    pause
    exit /b
)
echo [OK] commands.py найден

if not exist "server.pyw" (
    echo [X] server.pyw не найден!
    pause
    exit /b
)
echo [OK] server.pyw найден

if not exist "vk_bot.pyw" (
    echo [!] vk_bot.pyw не найден — VK-бот не будет запущен
) else (
    echo [OK] vk_bot.pyw найден
)
echo.

REM ===== ЗАПУСК СЕРВЕРА (скрыто) =====
echo [1/2] Запуск HTTP-сервера...
start /B "" "%PYTHON%" server.pyw
timeout /t 2 /nobreak >nul
echo [OK] Сервер запущен
echo.

REM ===== ЗАПУСК VK-БОТА (скрыто) =====
if exist "vk_bot.pyw" (
    echo [2/2] Запуск VK-бота...
    start /B "" "%PYTHON%" vk_bot.pyw
    timeout /t 2 /nobreak >nul
    echo [OK] VK-бот запущен
) else (
    echo [2/2] VK-бот пропущен
)
echo.

REM ===== ОТКРЫТИЕ САЙТА =====
echo ============================================================
echo   ВСЁ ЗАПУЩЕНО!
echo ============================================================
echo.
echo   Сервер:   http://localhost:8080
echo   VK-бот:   работает в фоне
echo.
echo   Что делать:
echo   1. Открой сайт на телефоне (http://IP_ПК:8080)
echo   2. Напиши боту в VK /start
echo.
echo   Чтобы ОСТАНОВИТЬ всё — запусти stop.bat
echo ============================================================
echo.

REM ===== ОТКРЫТИЕ БРАУЗЕРА =====
timeout /t 3 /nobreak >nul
start http://localhost:8080

echo Нажми любую клавишу для выхода из этого окна
echo (сервер и бот продолжат работать в фоне)
pause >nul
exit