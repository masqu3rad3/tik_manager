@echo OFF
set sourcePath=%~dp0
PyInstaller %sourcePath%\\SmStandalone.py -w -i %sourcePath%\\icons\\osicon_scenemanager_EM0_icon.ico -y --paths %sourcePath% --distpath %sourcePath%\\dist --workpath %sourcePath%\\build --win-private-assemblies --clean
