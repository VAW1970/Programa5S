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

:: Verificar dependencias
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

:: Mostrar IP local
echo  IPs disponiveis na rede:
ipconfig | findstr /R /C:"IPv4"

echo.
echo  Acesse pelo celular/tablet:
echo  http://SEU_IP:5001
echo  (substitua SEU_IP pelo IPv4 acima)
echo.
echo  Pressione CTRL+C para parar o servidor
echo  ============================================
echo.

:: Definir variaveis do Flask
set FLASK_APP=app.py
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=5001

:: Rodar Flask
flask run

pause
