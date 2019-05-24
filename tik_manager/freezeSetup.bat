@echo OFF
set sourcePath=%~dp0
python -OO -m PyInstaller %sourcePath%\\setup.py --distpath %sourcePath%\\dist --workpath %sourcePath%\\build --onefile -y

