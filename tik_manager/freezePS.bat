@echo OFF
set sourcePath=%~dp0
python -OO -m PyInstaller %sourcePath%\\SmPhotoshop.py -w -i %sourcePath%\\icons\\osicon_smPhotoshop_icon.ico -y --distpath %sourcePath%\\dist --workpath %sourcePath%\\build