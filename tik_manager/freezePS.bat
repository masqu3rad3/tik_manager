@echo OFF
set sourcePath=%~dp0
python -OO -m PyInstaller %sourcePath%\\SmPhotoshop.py -w -y --distpath %sourcePath%\\dist --workpath %sourcePath%\\build