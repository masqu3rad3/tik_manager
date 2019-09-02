@echo OFF
set sourcePath=%~dp0
PyInstaller %sourcePath%\\setup.py --distpath %sourcePath%\\dist --workpath %sourcePath%\\build --onefile -y --clean

