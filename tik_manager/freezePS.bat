@echo OFF
set sourcePath=%~dp0
PyInstaller %sourcePath%\\SmPhotoshop.py -w -i %sourcePath%\\icons\\osicon_smPhotoshop_icon.ico -y --paths %sourcePath% --distpath %sourcePath%\\dist --workpath %sourcePath%\\build --win-private-assemblies --clean