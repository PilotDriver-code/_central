@echo off
REM Gera dist\CentralRF.exe (um arquivo só, sem janela de console).
REM Rode a partir da pasta do projeto:  build_exe.bat

pip install --upgrade pyinstaller

REM As exclusoes abaixo evitam erro quando ha mais de um Qt instalado (ex.: PyQt5 + PySide6).
REM Se for empacotar com PyQt6 em vez de PySide6, troque por --exclude-module PySide6.

pyinstaller --noconfirm --clean --onefile --windowed ^
  --name CentralRF ^
  --icon assets\logo.ico ^
  --add-data "assets;assets" ^
  --exclude-module PyQt5 --exclude-module PyQt6 ^
  main.py

echo.
echo Pronto: dist\CentralRF.exe
echo Copie o .exe para a pasta onde ele vai ficar. As pastas de trabalho
echo (Cravar PU, Eventos SAC, Replicar Fluxo, Listas de ativos, Config)
echo serao criadas ao lado dele na primeira abertura.
pause
