import darkorange
from tik_manager.Qt import QtWidgets, QtCore, QtGui

def getStyleSheet():
	stream = QtCore.QFile(':/darkorange.qss')
	if stream.open(QtCore.QFile.ReadOnly):
		st = str(stream.readAll())
		stream.close()
	else:
		print(stream.errorString())
		
	return st