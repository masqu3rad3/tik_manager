"""Customized Widgets"""

from tik_manager.core.environment import get_environment_data

ENV_DATA = get_environment_data()

# import Qt module depending on the DCC
from importlib import import_module
QtWidgets = import_module("%s.QtWidgets" % ENV_DATA["qt_module"])
QtCore = import_module("%s.QtCore" % ENV_DATA["qt_module"])
QtGui = import_module("%s.QtGui" % ENV_DATA["qt_module"])

FORCE_QT5 = True if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop" else False

class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""

    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h / self.aspectRatio)
        self.setMaximumHeight(h / self.aspectRatio)


class DropListWidget(QtWidgets.QListWidget):
    """Custom List Widget which accepts drops"""

    # PyInstaller and Standalone version compatibility
    if FORCE_QT5:
        dropped = QtCore.pyqtSignal(str)
    else:
        dropped = QtCore.Signal(str)

    # dropped = QtCore.Signal(str)

    def __init__(self, type, parent=None):
        super(DropListWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # rawPath = event.mimeData().data('text/uri-list').__str__()
        rawPath = event.mimeData().text()
        path = rawPath.replace("file:///", "").splitlines()[0]
        # path = path.replace("\\r\\n'", "")
        self.dropped.emit(path)