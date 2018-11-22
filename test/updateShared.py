import os, sys
from shutil import copyfile

tikManagerDir = os.path.normpath("C:\\Users\\User\\Documents\\maya\\scripts\\dev\\tik_manager\\tik_manager")
shareDir = "M:\\Projects\\__database\\scripts\\tik_manager"

smFiles = os.listdir(tikManagerDir)

validExtensions = [".pyc", ".png", ".stylesheet", ".ico", ".bmp", ".exe"]

for root, dirs, files in os.walk(tikManagerDir, topdown=False):
    for file in files:
        ext = os.path.splitext(file)[1]
        if ext in validExtensions:
            source = (os.path.join(root, file))
            relPath = os.path.relpath(root, tikManagerDir)
            relPathFix = "" if relPath == "." else relPath
            target = (os.path.join(shareDir, relPathFix, file))
            # print source, "\n", target, "\n\n"
            try:
                copyfile(source, target)
                print "success %s => %s" %(source, target)
            except:
                print "FAILED %s => %s" % (source, target)


