@echo OFF
set sourcePath=%~dp0
PyInstaller %sourcePath%\\SmStandalone.py -w -i %sourcePath%\\icons\\osicon_scenemanager_EM0_icon.ico -y --distpath %sourcePath%\\dist --workpath %sourcePath%\\build --win-private-assemblies --clean
