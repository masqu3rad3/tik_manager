#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2017-2018, Arda Kutlu (ardakutlu@gmail.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------


"""Customized Widgets"""
import os
# import shutil
import unicodedata
import subprocess

from tik_manager.core.environment import get_environment_data

ENV_DATA = get_environment_data()

# import Qt module depending on the DCC
if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop":
    from PyQt5 import QtWidgets, QtCore, QtGui
else:
    from tik_manager.ui.Qt import QtWidgets, QtCore, QtGui

FORCE_QT5 = True if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop" else False

class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""

    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.aspectRatio = 1.78
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(h / self.aspectRatio)
        self.setMaximumHeight(h / self.aspectRatio)

class ImageViewer(QtWidgets.QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.
    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)
    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    if FORCE_QT5:
        leftMouseButtonPressed = QtCore.pyqtSignal(float, float)
        rightMouseButtonPressed = QtCore.pyqtSignal(float, float)
        leftMouseButtonReleased = QtCore.pyqtSignal(float, float)
        rightMouseButtonReleased = QtCore.pyqtSignal(float, float)
        leftMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
        rightMouseButtonDoubleClicked = QtCore.pyqtSignal(float, float)
    else:
        leftMouseButtonPressed = QtCore.Signal(float, float)
        rightMouseButtonPressed = QtCore.Signal(float, float)
        leftMouseButtonReleased = QtCore.Signal(float, float)
        rightMouseButtonReleased = QtCore.Signal(float, float)
        leftMouseButtonDoubleClicked = QtCore.Signal(float, float)
        rightMouseButtonDoubleClicked = QtCore.Signal(float, float)

    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = QtCore.Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QtGui.QPixmap:
            pixmap = image
        elif type(image) is QtGui.QImage:
            pixmap = QtGui.QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")

        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)

        self.setSceneRect(QtCore.QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QtCore.QT_VERSION_STR[0] == '5':
                fileName, dummy = QtWidgets.QFileDialog.getOpenFileName(self, "Open image file.")
            else:
                fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open image file.")

        if len(fileName) and os.path.isfile(fileName):
            image = QtWidgets.QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], QtCore.Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QtGui.QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)

class DropListWidget(QtWidgets.QListWidget):
    """Custom List Widget which accepts drops"""

    # PyInstaller and Standalone version compatibility
    if FORCE_QT5:
        dropped = QtCore.pyqtSignal(str)
    else:
        dropped = QtCore.Signal(str)

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

class DropPushButton(QtWidgets.QPushButton):
    """Custom LineEdit Class accepting drops"""
    # PyInstaller and Standalone version compatibility
    if FORCE_QT5:
        dropped = QtCore.pyqtSignal(list)
    else:
        dropped = QtCore.Signal(list)

    def __init__(self, type, parent=None):
        super(DropPushButton, self).__init__(parent)
        self.oldText = ""
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        # if event.mimeData().hasFormat('text/uri-list'):
        if event.mimeData().hasUrls():
            event.accept()
            self.oldText = (self.text())
            self.setText("Drop to add")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setText(self.oldText)

    def dragMoveEvent(self, event):
        # if event.mimeData().hasFormat('text/uri-list'):

        if event.mimeData().hasUrls:

            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):

        links = []

        for url in event.mimeData().urls():
            # links.append(str(url.toLocalFile()))

            links.append((url.toLocalFile()))
        self.dropped.emit(links)

class CopyProgress(QtWidgets.QWidget):
    """Custom Widget for visualizing progress of file transfer"""

    def __init__(self, logPath=None):
        super(CopyProgress, self).__init__()
        self.logPath = logPath
        self.logger = None
        # self.src = src
        # self.dest = dest
        self.build_ui()
        self.terminated = False
        self.cancelAll = False
        self.errorFlag = False

    def build_ui(self):

        hbox = QtWidgets.QVBoxLayout()

        vbox = QtWidgets.QHBoxLayout()

        lbl_src = QtWidgets.QLabel('Source: ')
        lbl_dest = QtWidgets.QLabel('Destination: ')
        lbl_overall = QtWidgets.QLabel('Overall Progress:')
        self.pb = QtWidgets.QProgressBar()
        self.pbOverall = QtWidgets.QProgressBar()
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelAllButton = QtWidgets.QPushButton("Cancel All")

        self.pb.setMinimum(0)
        self.pb.setMaximum(100)
        self.pb.setValue(0)

        self.pbOverall.setMinimum(0)
        self.pbOverall.setMaximum(100)
        self.pbOverall.setValue(0)

        hbox.addWidget(lbl_src)
        hbox.addWidget(lbl_dest)
        hbox.addWidget(self.pb)
        hbox.addWidget(lbl_overall)
        hbox.addWidget(self.pbOverall)
        vbox.addWidget(self.cancelButton)
        vbox.addWidget(self.cancelAllButton)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.setWindowTitle('File copy')
        self.cancelButton.clicked.connect(self.terminate)
        self.cancelAllButton.clicked.connect(lambda: self.terminate(all=True))
        self.show()

    def results_ui(self, status, color="white", logPath=None, destPath=None):

        self.msgDialog = QtWidgets.QDialog(parent=self)
        self.msgDialog.setModal(True)
        self.msgDialog.setObjectName("Result_Dialog")
        self.msgDialog.setWindowTitle("Transfer Results")
        self.msgDialog.resize(300, 120)
        layoutMain = QtWidgets.QVBoxLayout()
        self.msgDialog.setLayout(layoutMain)

        infoHeader = QtWidgets.QLabel(status)

        infoHeader.setStyleSheet(""
                                 "border: 18px solid black;"
                                 "background-color: black;"
                                 "font-size: 14px;"
                                 "color: {0}"
                                 "".format(color))

        layoutMain.addWidget(infoHeader)
        layoutH = QtWidgets.QHBoxLayout()
        layoutMain.addLayout(layoutH)
        if logPath:
            showLogButton = QtWidgets.QPushButton("Show Log File")
            layoutH.addWidget(showLogButton)
            showLogButton.clicked.connect(lambda x=logPath: os.startfile(x))
        showInExplorer = QtWidgets.QPushButton("Show in Explorer")
        layoutH.addWidget(showInExplorer)
        okButton = QtWidgets.QPushButton("OK")
        layoutH.addWidget(okButton)

        showInExplorer.clicked.connect(lambda x=destPath: self.onShowInExplorer(destPath))

        okButton.clicked.connect(self.msgDialog.close)

        self.msgDialog.show()

    def onShowInExplorer(self, tpath):
        """Opens the path in Windows Explorer(Windows) or Nautilus(Linux)"""
        if os.path.isfile(tpath):
            tpath = os.path.dirname(tpath)
        if self.currentPlatform == "Windows":
            os.startfile(tpath)
        elif self.currentPlatform == "Linux":
            subprocess.Popen(["xdg-open", tpath])
        else:
            subprocess.Popen(["open", tpath])

    def closeEvent(self, *args, **kwargs):
        """Override close behaviour"""
        self.terminated = True

    def terminate(self, all=False):
        """Terminate the progress"""
        self.terminated = True
        self.cancelAll = all

    def masterCopy(self, srcList, dst):

        totalCount = len(srcList)
        current = 0
        copiedPathList = []
        for sel in srcList:
            if self.cancelAll:
                break

            percent = (100 * current) / totalCount
            self.pbOverall.setValue(percent)
            current += 1

            if os.path.isdir(sel):
                # re-define dst starting from the folder name
                newDst = os.path.join(dst, os.path.basename(sel))
                newDst = self.strip_accents(newDst)

                copiedPathList.append(self.copyFolder(src=sel, dst=newDst))

            else:
                dst = self.strip_accents(dst)

                if not os.path.isdir(os.path.normpath(dst)):
                    os.makedirs(os.path.normpath(dst))

                copiedPathList.append(self.copyItem(src=sel, dst=dst))

        # self.deleteLogger(self.logger)

        self.close()
        if self.cancelAll:
            self.results_ui("Canceled by user", logPath=self.logPath, destPath=dst)
        elif self.errorFlag:
            self.results_ui("Finished with Error(s)", color="red", logPath=self.logPath, destPath=dst)
        else:
            self.results_ui("Success", logPath=self.logPath, destPath=dst)
        return copiedPathList

    def copyFolder(self, src, dst):

        dst = self.uniqueFolderName(os.path.normpath(dst.replace(" ", "_")))
        if not os.path.isdir(dst):
            os.makedirs(dst)

        self.pb.setValue(0)
        self.terminated = False  # reset the termination status
        totalCount = self.countFiles(src)
        current = 0
        QtWidgets.QApplication.processEvents()

        for path, dirs, filenames in os.walk(src):
            for directory in dirs:

                destDir = path.replace(src, dst)
                targetDir = os.path.join(destDir, directory)
                targetDir = self.strip_accents(targetDir)

                if not os.path.isdir(targetDir):
                    os.makedirs(targetDir)

            for sfile in filenames:
                srcFile = os.path.join(path, sfile)

                destFile = os.path.join(path.replace(src, dst), sfile)
                self.copyItem(srcFile, os.path.split(destFile)[0])

                percent = (100 * current) / totalCount
                # self.pb.setValue(percent)
                self.pbOverall.setValue(percent)
                current += 1
                QtWidgets.QApplication.processEvents()
                # self.safeLog("Success - {0}".format(targetPath))
                if self.terminated or self.cancelAll:
                    self.errorFlag = True
                    # self.safeLog("FAILED - skipped by user")
                    return None
                    # break

        return dst

    def copyItem(self, src, dst):
        src = os.path.normpath(src)
        dst = os.path.normpath(dst)
        length = 8*1024
        self.pb.setValue(0)
        self.terminated = False  # reset the termination status
        totalCount = self.countFiles(src)
        current = 0
        QtWidgets.QApplication.processEvents()

        # Prevent progress callback from being made each cycle
        c = 0
        c_max = 50

        # try:
        fileLocation = self.uniqueFileName(os.path.join(dst, os.path.basename(src)))
        fileLocation = self.strip_accents(fileLocation)
        with open(src, 'rb') as fsrc:
            with open(fileLocation, 'wb') as fdst:
                copied = 0
                while self.errorFlag==False:
                    buf = fsrc.read(length)
                    if not buf:
                        break
                    fdst.write(buf)
                    copied += len(buf)
                    c += 1
                    if c == c_max:
                        size_src = os.stat(fsrc.name).st_size
                        size_dst =os.stat(fdst.name).st_size
                        float_src = float(size_src)
                        float_dst = float(size_dst)
                        percentage = int(float_dst/float_src*100)
                        self.pb.setValue(percentage)
                        c = 0
                        QtWidgets.QApplication.processEvents()
                    if self.terminated or self.cancelAll:

                        self.errorFlag = True
        if self.errorFlag:
            os.remove(fileLocation)
            return None
        else:
            return fileLocation

    def uniqueFolderName(self, folderLocation):
        count = 0
        max_iter = 100
        while os.path.isdir(folderLocation) and count < max_iter:
            count += 1
            directory, baseName = os.path.split(folderLocation)
            niceName, ext = os.path.splitext(baseName)
            if niceName.endswith("_sm({0})".format(count - 1)):
                niceName = niceName.replace("_sm({0})".format(str(count - 1)), "_sm({0})".format(str(count)))
            else:
                niceName = "{0}_sm({1})".format(niceName, str(count))
            folderLocation = os.path.join(directory, "{0}{1}".format(niceName, ext))
        return folderLocation

    def uniqueFileName(self, fileLocation):
        count = 0
        max_iter = 100
        while os.path.isfile(fileLocation) and count < max_iter:
            count += 1
            directory, baseName = os.path.split(fileLocation)
            niceName, ext = os.path.splitext(baseName)
            if niceName.endswith("_sm({0})".format(count - 1)):
                niceName = niceName.replace("_sm({0})".format(str(count - 1)), "_sm({0})".format(str(count)))
            else:
                niceName = "{0}_sm({1})".format(niceName, str(count))
            fileLocation = os.path.join(directory, "{0}{1}".format(niceName, ext))
        return fileLocation

    def countFiles(self, directory):
        files = []

        if os.path.isdir(directory):
            for path, dirs, filenames in os.walk(directory):
                files.extend(filenames)
            return len(files)
        else:
            return 1

    def strip_accents(self, s):
        """
        Sanitarize the given unicode string and remove all special/localized
        characters from it.

        Category "Mn" stands for Nonspacing_Mark
        """

        if type(s) == str:
            try:
                s = unicode(s, "utf-8")
            except:
                pass

        newNameList = []
        for c in unicodedata.normalize('NFKD', s):
            if unicodedata.category(c) != 'Mn':
                if c == u'ı':
                    newNameList.append(u'i')
                else:
                    newNameList.append(c)
        return ''.join(newNameList)

class FileAndFolderDialog(QtWidgets.QFileDialog):
    def __init__(self, *args):
        QtWidgets.QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtWidgets.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtWidgets.QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                dir = str(self.directory().absolutePath())

                try:
                    unicode = unicode
                    if not type(i.data()) == unicode:
                        file = str(i.data().toString())
                    else:
                        file = str(i.data())
                except NameError:
                    file = str(i.data())
                path = os.path.normpath(os.path.join(dir, file))
                files.append(path)
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles