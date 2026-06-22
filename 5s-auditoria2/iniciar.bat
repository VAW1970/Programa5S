@echo off
title Programa 5S - Sistema de Auditorias
echo.
echo  ============================================
echo   Programa 5S - Sistema de Auditorias
echo  ============================================
echo.

:: Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao foi encontrado!
    echo  Instale Python em: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Navegar para a pasta do projeto
cd /d "%~dp0"

:: Verificar se as dependencias estao instaladas
echo  [1/3] Verificando dependencias...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo  [2/3] Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo  [2/3] Dependencias ja instaladas.
)

echo.
echo  [3/3] Iniciando servidor...
echo  ============================================
echo   Acesse: http://127.0.0.1:5001
echo   Pressione CTRL+C para parar o servidor
echo  ============================================
echo.

:: Iniciar o Flask
python app.py

pause
