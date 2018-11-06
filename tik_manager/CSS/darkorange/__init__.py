import os
import darkorange
# reload(darkorange)
# from tik_manager.Qt import QtWidgets, QtCore, QtGui

# PyInstaller and Standalone version compatibility
FORCE_QT4 = bool(os.getenv("FORCE_QT4"))
if FORCE_QT4:
    # from PyQt4 import QtCore, Qt
    from PyQt4 import QtCore
    # from PyQt4 import QtGui as QtWidgets
else:
	# from tik_manager.Qt import QtWidgets, QtCore, QtGui
	from tik_manager.Qt import QtCore

def getStyleSheet():
	stream = QtCore.QFile(':/darkorange.qss')
	if stream.open(QtCore.QFile.ReadOnly):
		st = str(stream.readAll())
		stream.close()
	else:
		print(stream.errorString())
	return st