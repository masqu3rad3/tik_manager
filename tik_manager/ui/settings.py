import os
from copy import deepcopy
import re
import tik_manager.core.compatibility as compat
from tik_manager.core.environment import get_environment_data

ENV_DATA = get_environment_data()

# import Qt module depending on the DCC
from importlib import import_module
if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop":
    from PyQt5 import QtWidgets, QtCore, QtGui
else:
    from tik_manager.ui.Qt import QtWidgets, QtCore, QtGui

FORCE_QT5 = True if ENV_DATA["dcc"] == "standalone" or ENV_DATA["dcc"] == "photoshop" else False



class SettingsUI(object):
    def __init__(self):
        # super(SettingsUI, self).__init__()

        dirname = os.path.dirname(os.path.abspath(__file__))
        stylesheetFile = os.path.join(dirname, "../CSS", "tikManager.qss")

        try:
            with open(stylesheetFile, "r") as fh:
                self.setStyleSheet(fh.read())
        except IOError:
            pass

    def settingsUI(self):
        self.allSettingsDict = Settings()

        self.minSPBSize = (70, 25)

        settings_Dialog = QtWidgets.QDialog(parent=self, windowTitle="Settings")
        settings_Dialog.resize(960, 630)

        verticalLayout_2 = QtWidgets.QVBoxLayout(settings_Dialog)

        try:
            verticalLayout_2.setMargin(0)
        except AttributeError:
            pass
        verticalLayout_2.setContentsMargins(10, 10, 10, 10)

        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.setSpacing(6)

        splitter = QtWidgets.QSplitter(settings_Dialog)
        splitter.setChildrenCollapsible(False)

        splitter.setLineWidth(0)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        left_frame = QtWidgets.QFrame(splitter, minimumSize=QtCore.QSize(150, 0), frameShape=QtWidgets.QFrame.NoFrame,
                                      frameShadow=QtWidgets.QFrame.Plain, lineWidth=0)

        verticalLayout_4 = QtWidgets.QVBoxLayout(left_frame)
        verticalLayout_4.setSpacing(0)

        leftFrame_verticalLayout = QtWidgets.QVBoxLayout()
        leftFrame_verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        leftFrame_verticalLayout.setSpacing(6)

        self.settingsMenu_treeWidget = QtWidgets.QTreeWidget(left_frame, lineWidth=1, rootIsDecorated=True,
                                                             headerHidden=True)
        self.settingsMenu_treeWidget.setFont(self.headerBFont)

        self.userSettings_item = QtWidgets.QTreeWidgetItem(["User Settings"])
        self.settingsMenu_treeWidget.addTopLevelItem(self.userSettings_item)

        # TOP ITEM
        self.projectSettings_item = QtWidgets.QTreeWidgetItem(["Project Settings"])
        self.settingsMenu_treeWidget.addTopLevelItem(self.projectSettings_item)

        # children
        self.previewSettings_item = QtWidgets.QTreeWidgetItem(["Preview Settings"])
        self.projectSettings_item.addChild(self.previewSettings_item)

        self.categories_item = QtWidgets.QTreeWidgetItem(["Categories"])
        self.projectSettings_item.addChild(self.categories_item)

        self.importExport_item = QtWidgets.QTreeWidgetItem(["Import/Export Options"])
        self.projectSettings_item.addChild(self.importExport_item)

        # TOP ITEM
        self.sharedSettings_item = QtWidgets.QTreeWidgetItem(["Shared Settings"])
        self.settingsMenu_treeWidget.addTopLevelItem(self.sharedSettings_item)

        # children
        self.users_item = QtWidgets.QTreeWidgetItem(["Users"])
        self.sharedSettings_item.addChild(self.users_item)

        self.passwords_item = QtWidgets.QTreeWidgetItem(["Passwords"])
        self.sharedSettings_item.addChild(self.passwords_item)

        self.namingConventions_item = QtWidgets.QTreeWidgetItem(["Naming Conventions"])
        self.sharedSettings_item.addChild(self.namingConventions_item)

        leftFrame_verticalLayout.addWidget(self.settingsMenu_treeWidget)
        verticalLayout_4.addLayout(leftFrame_verticalLayout)

        self.contents_frame = QtWidgets.QFrame(splitter)
        self.contents_frame.setEnabled(True)

        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.contents_frame)
        self.contents_Layout = QtWidgets.QVBoxLayout()
        self.contents_Layout.setSpacing(0)

        self.scrollArea = QtWidgets.QScrollArea(self.contents_frame)

        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()

        self.contentsMaster_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.contents_Layout.addWidget(self.scrollArea)
        self.verticalLayout_5.addLayout(self.contents_Layout)
        verticalLayout.addWidget(splitter)

        ## CONTENTS START

        # Visibility Widgets for EACH page
        self.userSettings_vis = QtWidgets.QWidget()
        self.projectSettings_vis = QtWidgets.QWidget()
        self.previewSettings_vis = QtWidgets.QWidget()
        self.categories_vis = QtWidgets.QWidget()
        self.importExportOptions_vis = QtWidgets.QWidget()
        self.sharedSettings_vis = QtWidgets.QWidget()
        self.users_vis = QtWidgets.QWidget()
        self.passwords_vis = QtWidgets.QWidget()
        self.namingConventions_vis = QtWidgets.QWidget()

        def pageUpdate():
            if self.settingsMenu_treeWidget.currentItem().text(0) != "User Settings" and not self.superUser:
                passw, ok = QtWidgets.QInputDialog.getText(self, "Password Query",
                                                           "This Section requires Admin Password:",
                                                           QtWidgets.QLineEdit.Password)

                if ok:
                    if self.manager.checkPassword(passw):
                        self.superUser = True
                        pass
                    else:
                        self.infoPop(textTitle="Incorrect Password", textHeader="The Password is invalid")
                        self.settingsMenu_treeWidget.setCurrentItem(self.userSettings_item)
                        return
                else:
                    self.settingsMenu_treeWidget.setCurrentItem(self.userSettings_item)

                    return

            allPages = {"User Settings": self.userSettings_vis,
                        "Project Settings": self.projectSettings_vis,
                        "Preview Settings": self.previewSettings_vis,
                        "Categories": self.categories_vis,
                        "Import/Export Options": self.importExportOptions_vis,
                        "Shared Settings": self.sharedSettings_vis,
                        "Users": self.users_vis,
                        "Passwords": self.passwords_vis,
                        "Naming Conventions": self.namingConventions_vis}
            for item in allPages.items():
                isVisible = False if item[0] == self.settingsMenu_treeWidget.currentItem().text(0) else True
                item[1].setHidden(isVisible)

        self.softwareDB = self.manager.loadSoftwareDatabase()

        ## USER SETTINGS
        currentUserSettings = self.manager.loadUserSettings()
        # try: currentUserSettings["extraColumns"] # this moved to the root
        # except KeyError: currentUserSettings["extraColumns"] = ["Date"]
        self.allSettingsDict.add("userSettings", currentUserSettings, self.manager._pathsDict["userSettingsFile"])
        currentCommonFolder = self.manager._getCommonFolder()
        self.allSettingsDict.add("sharedSettingsDir", currentCommonFolder, self.manager._pathsDict["commonFolderFile"])
        self._userSettingsContent()

        ## PROJECT SETTINGS
        currentProjectSettings = self.manager.loadProjectSettings()
        self.allSettingsDict.add("projectSettings", currentProjectSettings,
                                 self.manager._pathsDict["projectSettingsFile"])
        self._projectSettingsContent()

        ## PREVIEW SETTINGS
        self.previewMasterLayout = QtWidgets.QVBoxLayout(self.previewSettings_vis)
        sw = ENV_DATA["dcc"].lower()

        if sw == "maya" or sw == "standalone":
            settingsFilePathMaya = os.path.join(self.manager._pathsDict["previewsRoot"],
                                                self.softwareDB["Maya"]["pbSettingsFile"])
            currentMayaSettings = self.manager.loadPBSettings(filePath=settingsFilePathMaya)
            # backward compatibility:
            try:
                currentMayaSettings["ConvertMP4"]
                currentMayaSettings["CrfValue"]
            except KeyError:
                currentMayaSettings["ConvertMP4"] = True
                currentMayaSettings["CrfValue"] = 23

            try:
                currentMayaSettings["ViewportAsItIs"]
                currentMayaSettings["HudsAsItIs"]
            except KeyError:
                currentMayaSettings["ViewportAsItIs"] = False
                currentMayaSettings["HudsAsItIs"] = False

            # update the settings dictionary
            self.allSettingsDict.add("preview_maya", currentMayaSettings, settingsFilePathMaya)

            self._previewSettingsContent_maya()
        if sw == "3dsmax" or sw == "standalone":
            settingsFilePathMax = os.path.join(self.manager._pathsDict["previewsRoot"],
                                               self.softwareDB["3dsMax"]["pbSettingsFile"])
            currentMaxSettings = self.manager.loadPBSettings(filePath=settingsFilePathMax)
            # backward compatibility:
            try:
                currentMaxSettings["ConvertMP4"]
                currentMaxSettings["CrfValue"]
            except KeyError:
                currentMaxSettings["ConvertMP4"] = True
                currentMaxSettings["CrfValue"] = 23

            try:
                currentMaxSettings["ViewportAsItIs"]
                currentMaxSettings["HudsAsItIs"]
            except KeyError:
                currentMaxSettings["ViewportAsItIs"] = False
                currentMaxSettings["HudsAsItIs"] = False

            # update the settings dictionary
            self.allSettingsDict.add("preview_max", currentMaxSettings, settingsFilePathMax)

            self._previewSettingsContent_max()
        if sw == "houdini" or sw == "standalone":
            settingsFilePathHou = os.path.join(self.manager._pathsDict["previewsRoot"],
                                               self.softwareDB["Houdini"]["pbSettingsFile"])
            currentHoudiniSettings = self.manager.loadPBSettings(filePath=settingsFilePathHou)
            # backward compatibility:
            try:
                currentHoudiniSettings["ConvertMP4"]
                currentHoudiniSettings["CrfValue"]
            except KeyError:
                currentHoudiniSettings["ConvertMP4"] = True
                currentHoudiniSettings["CrfValue"] = 23

            try:
                currentHoudiniSettings["ViewportAsItIs"]
                currentHoudiniSettings["HudsAsItIs"]
            except KeyError:
                currentHoudiniSettings["ViewportAsItIs"] = False
                currentHoudiniSettings["HudsAsItIs"] = False

            # update the settings dictionary
            self.allSettingsDict.add("preview_houdini", currentHoudiniSettings, settingsFilePathHou)

            self._previewSettingsContent_houdini()

        self.contentsMaster_layout.addWidget(self.previewSettings_vis)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.previewMasterLayout.addItem(spacerItem)

        ## CATEGORIES

        if sw == "standalone":
            # if it is standalone, get all categories for all softwares
            for value in self.softwareDB.values():
                niceName = value["niceName"]
                folderPath = os.path.normpath(os.path.join(self.manager._pathsDict["masterDir"], value["databaseDir"]))
                self.manager._folderCheck(folderPath)

                filePath = os.path.normpath(os.path.join(folderPath, value["categoriesFile"]))
                categoryData = self.manager.loadCategories(filePath=filePath, swName=niceName)
                self.allSettingsDict.add("categories_%s" % niceName, categoryData, filePath)
        else:
            currentCategories = self.manager.loadCategories()
            self.allSettingsDict.add("categories_%s" % self.manager.dcc, currentCategories,
                                     self.manager._pathsDict["categoriesFile"])

        self._categoriesContent()

        ## IMPORT/EXPORT OPTIONS
        currentImportSettings = self.manager.loadImportSettings()
        self.allSettingsDict.add("importSettings", currentImportSettings, self.manager._pathsDict["importSettingsFile"])
        currentExportSettings = self.manager.loadExportSettings()
        self.allSettingsDict.add("exportSettings", currentExportSettings, self.manager._pathsDict["exportSettingsFile"])
        self._importExportContent()

        self._sharedSettingsContent()

        ## USERS
        currentUsers = self.manager.loadUsers()
        self.allSettingsDict.add("users", currentUsers, self.manager._pathsDict["usersFile"])
        self._usersContent()

        ## PASSWORDS
        self._passwordsContent()

        ## NAMING CONVENTIONS
        currentConventions = self.manager.loadNameConventions()
        self.allSettingsDict.add("nameConventions", currentConventions, self.manager._pathsDict["tikConventions"])
        self._namingConventions()

        self.settingsButtonBox = QtWidgets.QDialogButtonBox(settings_Dialog)
        self.settingsButtonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Apply | QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
        self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))
        self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Apply).setMinimumSize(QtCore.QSize(100, 30))
        self.settingsOk_btn = self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.settingsOk_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        self.settingsApply_btn = self.settingsButtonBox.button(QtWidgets.QDialogButtonBox.Apply)
        self.settingsApply_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        verticalLayout.addWidget(self.settingsButtonBox)
        verticalLayout_2.addLayout(verticalLayout)

        settings_Dialog.setTabOrder(self.settingsButtonBox, self.settingsMenu_treeWidget)
        self.settingsApply_btn.setEnabled(False)

        def applySettingChanges():
            for x in self.allSettingsDict.apply():
                self.manager._dumpJson(x["data"], x["filepath"])
            self.settingsApply_btn.setEnabled(False)
            self.initMainUI()

        # # SIGNALS
        # # -------
        #
        self.settingsMenu_treeWidget.currentItemChanged.connect(pageUpdate)
        self.settingsMenu_treeWidget.setCurrentItem(self.userSettings_item)

        self.settingsButtonBox.accepted.connect(applySettingChanges)
        self.settingsButtonBox.accepted.connect(settings_Dialog.accept)
        self.settingsApply_btn.clicked.connect(applySettingChanges)

        self.settingsButtonBox.rejected.connect(settings_Dialog.reject)

        splitter.setStretchFactor(1, 20)
        settings_Dialog.show()


    def _userSettingsContent(self):
        userSettings_Layout = QtWidgets.QVBoxLayout(self.userSettings_vis)
        userSettings_Layout.setSpacing(6)
        userSettings = self.allSettingsDict.get("userSettings")

        def updateDictionary():
            userSettings["globalFavorites"] = globalFavorites_radiobutton.isChecked()
            userSettings["inheritRanges"] = inherit_range_combo.currentText()

            newExtraColumns = []
            if extra_date_cb.isChecked():
                newExtraColumns.append("Date")
            if extra_ref_cb.isChecked():
                newExtraColumns.append("Ref. Version")
            if extra_creator_cb.isChecked():
                newExtraColumns.append("Creator")
            if extra_versionCount_cb.isChecked():
                newExtraColumns.append("Version Count")
            userSettings["extraColumns"] = newExtraColumns

            # enteredPath = os.path.normpath(unicode(commonDir_lineEdit.text()).encode("utf-8"))
            enteredPath = os.path.normpath(compat.encode(commonDir_lineEdit.text()))
            if self.manager._checkCommonFolder(enteredPath):
                self.allSettingsDict["sharedSettingsDir"]["newSettings"] = enteredPath
            else:
                commonDir_lineEdit.setText(self.allSettingsDict["sharedSettingsDir"]["oldSettings"])
                return

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        userSettings_formLayout = QtWidgets.QFormLayout()
        userSettings_formLayout.setSpacing(6)
        userSettings_formLayout.setHorizontalSpacing(15)
        userSettings_formLayout.setVerticalSpacing(15)
        userSettings_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)

        userSettings_Layout.addLayout(userSettings_formLayout)

        # form item 0
        row = 0
        userSettings_label = QtWidgets.QLabel(font=self.headerAFont, text="User Settings")
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, userSettings_label)

        # form item 1
        row += 1
        favorites_label = QtWidgets.QLabel(text="Project Favorites:")
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, favorites_label)

        favorites_layout = QtWidgets.QHBoxLayout()
        globalFavorites_radiobutton = QtWidgets.QRadioButton(text="Global Favorites")
        globalFavorites_radiobutton.setToolTip("Projects added to the Favorites list in the Set Project Interface will be available for all software")
        globalFavorites_radiobutton.setChecked(self.manager.isGlobalFavorites())

        localFavorites_radiobutton = QtWidgets.QRadioButton(text="Software Specific")
        localFavorites_radiobutton.setToolTip("Projects added to the Favorites list in the Set Project Interface will be available only for that software")
        localFavorites_radiobutton.setChecked(not self.manager.isGlobalFavorites())


        favorites_buttonGroup = QtWidgets.QButtonGroup(self.userSettings_vis)
        favorites_buttonGroup.addButton(globalFavorites_radiobutton)
        favorites_buttonGroup.addButton(localFavorites_radiobutton)
        favorites_layout.addWidget(globalFavorites_radiobutton)
        favorites_layout.addWidget(localFavorites_radiobutton)
        userSettings_formLayout.setLayout(row, QtWidgets.QFormLayout.FieldRole, favorites_layout)

        #
        row += 1
        inherit_range_lb = QtWidgets.QLabel(text="Inherit Referenced Ranges")
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, inherit_range_lb)
        inherit_range_combo = QtWidgets.QComboBox()
        inherit_range_combo.addItems(["Ask", "Always", "Never"])
        inherit_range_combo.setCurrentText(userSettings["inheritRanges"])
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.FieldRole, inherit_range_combo)

        # form item 2 - Extra Columns
        row += 1
        extraColumns_label = QtWidgets.QLabel(text="Base Scenes Extra Columns:")
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, extraColumns_label)

        extraColumns_layout = QtWidgets.QHBoxLayout()
        extraColumns_layout.setSpacing(2)

        extra_date_cb = QtWidgets.QCheckBox(text="Date")
        extra_date_cb.setToolTip("Adds Date Column to the Base Software List which shows the creation dates of Base Scenes")
        extraColumns_layout.addWidget(extra_date_cb)
        extra_date_cb.setChecked("Date" in userSettings["extraColumns"])

        extra_ref_cb = QtWidgets.QCheckBox(text="Reference Version")
        extra_ref_cb.setToolTip("Adds Ref. Version Column to the Base Software List which shows the currently referenced version of the Base Scenes.\nKeep in mind this option may create performance issues with crowded categories")
        extraColumns_layout.addWidget(extra_ref_cb)
        extra_ref_cb.setChecked("Ref. Version" in userSettings["extraColumns"])

        extra_creator_cb = QtWidgets.QCheckBox(text="Creator")
        extra_creator_cb.setToolTip("Adds Creator Column to the Base Software List")
        extraColumns_layout.addWidget(extra_creator_cb)
        extra_creator_cb.setChecked("Creator" in userSettings["extraColumns"])

        extra_versionCount_cb = QtWidgets.QCheckBox(text="Version Count")
        extra_versionCount_cb.setToolTip("Adds Version Count Column to the Base Software List")
        extraColumns_layout.addWidget(extra_versionCount_cb)
        extra_versionCount_cb.setChecked("Version Count" in userSettings["extraColumns"])

        userSettings_formLayout.setLayout(row, QtWidgets.QFormLayout.FieldRole, extraColumns_layout)


        # form item 3 - Common Settings Directory
        row += 1
        commonDir_label = QtWidgets.QLabel(text="Common Settings Directory:")
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, commonDir_label)

        commonDir_layout = QtWidgets.QHBoxLayout()
        commonDir_layout.setSpacing(2)

        commonDir_lineEdit = QtWidgets.QLineEdit(text=self.manager.getSharedSettingsDir(), minimumWidth=350)
        commonDir_layout.addWidget(commonDir_lineEdit)

        setCommon_button = QtWidgets.QPushButton(text="...")
        commonDir_layout.addWidget(setCommon_button)
        userSettings_formLayout.setLayout(row, QtWidgets.QFormLayout.FieldRole, commonDir_layout)

        # form item 4
        row += 1
        colorCoding_label = QtWidgets.QLabel(text="Color Codes: ")
        userSettings_formLayout.setWidget(row, QtWidgets.QFormLayout.LabelRole, colorCoding_label)

        colorCoding_formlayout = QtWidgets.QFormLayout()
        colorCoding_formlayout.setSpacing(2)
        colorCoding_formlayout.setVerticalSpacing(5)
        userSettings_formLayout.setLayout(row, QtWidgets.QFormLayout.FieldRole, colorCoding_formlayout)

        # Executable paths
        # header lbl
        executables_lbl = QtWidgets.QLabel(font=self.headerBFont, text="Executable Paths")
        userSettings_formLayout.addRow(executables_lbl)

        executablesInfo_lbl = QtWidgets.QLabel(font=self.infoFont,
                                               text="Defined executables will be used to run corresponding items. "
                                                    "When left blank, system defaults will be used.\n\n"
                                                    "If arguments want to be passed <itemPath> token can be used",
                                               wordWrap=True)
        userSettings_formLayout.addRow(executablesInfo_lbl)
        # images
        exeImages_lbl = QtWidgets.QLabel(text="Image viewer: ")
        exeImages_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeImages_le = QtWidgets.QLineEdit(minimumWidth=350,
                                           placeholderText="Define an executable for images (Optional) ")
        exeImages_le.setObjectName("image_exec") # DO NOT DELETE THIS
        try:
            exeImages_le.setText(userSettings["executables"]["image_exec"])
        except KeyError:
            pass
        exeImages_hlay.addWidget(exeImages_le)
        exeImages_btn = QtWidgets.QPushButton(text="...")
        exeImages_hlay.addWidget(exeImages_btn)
        userSettings_formLayout.addRow(exeImages_lbl, exeImages_hlay)
        # imageSeq
        exeImageSeq_lbl = QtWidgets.QLabel(text="Sequence viewer: ")
        exeImageSeq_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeImageSeq_le = QtWidgets.QLineEdit(minimumWidth=350,
                                             placeholderText="Define an executable for imageSeq (Optional) ")
        exeImageSeq_le.setObjectName("imageSeq_exec")  # DO NOT DELETE THIS
        try:
            exeImageSeq_le.setText(userSettings["executables"]["imageSeq_exec"])
        except KeyError:
            pass
        exeImageSeq_hlay.addWidget(exeImageSeq_le)
        exeImageSeq_btn = QtWidgets.QPushButton(text="...")
        exeImageSeq_hlay.addWidget(exeImageSeq_btn)
        userSettings_formLayout.addRow(exeImageSeq_lbl, exeImageSeq_hlay)
        # Video Files
        exeVideo_lbl = QtWidgets.QLabel(text="Video viewer: ")
        exeVideo_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeVideo_le = QtWidgets.QLineEdit(minimumWidth=350,
                                          placeholderText="Define an executable for Video (Optional) ")
        exeVideo_le.setObjectName("video_exec")  # DO NOT DELETE THIS
        try:
            exeVideo_le.setText(userSettings["executables"]["video_exec"])
        except KeyError:
            pass
        exeVideo_hlay.addWidget(exeVideo_le)
        exeVideo_btn = QtWidgets.QPushButton(text="...")
        exeVideo_hlay.addWidget(exeVideo_btn)
        userSettings_formLayout.addRow(exeVideo_lbl, exeVideo_hlay)
        # Obj
        exeObj_lbl = QtWidgets.QLabel(text="Obj viewer: ")
        exeObj_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeObj_le = QtWidgets.QLineEdit(minimumWidth=350, placeholderText="Define an executable for obj (Optional) ")
        exeObj_le.setObjectName("obj_exec")  # DO NOT DELETE THIS
        try:
            exeObj_le.setText(userSettings["executables"]["obj_exec"])
        except KeyError:
            pass
        exeObj_hlay.addWidget(exeObj_le)
        exeObj_btn = QtWidgets.QPushButton(text="...")
        exeObj_hlay.addWidget(exeObj_btn)
        userSettings_formLayout.addRow(exeObj_lbl, exeObj_hlay)
        # Fbx
        exeFbx_lbl = QtWidgets.QLabel(text="Fbx viewer: ")
        exeFbx_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeFbx_le = QtWidgets.QLineEdit(minimumWidth=350, placeholderText="Define an executable for fbx (Optional) ")
        exeFbx_le.setObjectName("fbx_exec")  # DO NOT DELETE THIS
        try:
            exeFbx_le.setText(userSettings["executables"]["fbx_exec"])
        except KeyError:
            pass
        exeFbx_hlay.addWidget(exeFbx_le)
        exeFbx_btn = QtWidgets.QPushButton(text="...")
        exeFbx_hlay.addWidget(exeFbx_btn)
        userSettings_formLayout.addRow(exeFbx_lbl, exeFbx_hlay)
        # Abc
        exeAbc_lbl = QtWidgets.QLabel(text="Alembic viewer: ")
        exeAbc_hlay = QtWidgets.QHBoxLayout(spacing=2)
        exeAbc_le = QtWidgets.QLineEdit(minimumWidth=350, placeholderText="Define an executable for abc (Optional) ")
        exeAbc_le.setObjectName("alembic_exec")  # DO NOT DELETE THIS
        try:
            exeAbc_le.setText(userSettings["executables"]["alembic_exec"])
        except KeyError:
            pass
        exeAbc_hlay.addWidget(exeAbc_le)
        exeAbc_btn = QtWidgets.QPushButton(text="...")
        exeAbc_hlay.addWidget(exeAbc_btn)
        userSettings_formLayout.addRow(exeAbc_lbl, exeAbc_hlay)

        def colorSet(button, niceName):
            color = QtWidgets.QColorDialog.getColor()
            if color:
                button.setStyleSheet("background-color: %s; min-width: 80px;" % color.name())
                userSettings["colorCoding"][niceName] = "rgb%s" % str(color.getRgb())
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def resetColors():
            try:
                defaults = deepcopy(self.manager._sceneManagerDefaults["defaultColorCoding"])
                for key in list(userSettings["colorCoding"]):
                    userSettings["colorCoding"][key] = defaults[key]
            except KeyError:
                self.infoPop(textTitle="Cannot get default database",
                             textHeader="Default Color Coding Database cannot be found")
                return
            for item in userSettings["colorCoding"].items():
                niceName = item[0]
                color = item[1]
                try:
                    pushbutton = self.findChild(QtWidgets.QPushButton, "cc_%s" % niceName)
                    pushbutton.setStyleSheet("background-color:%s; min-width: 80px;" % color)
                except AttributeError:
                    pass
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def browseCommonDatabase():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                # selectedroot = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                selectedroot = os.path.normpath(compat.encode(dlg.selectedFiles()[0]))
                if self.manager._checkCommonFolder(selectedroot):
                    commonDir_lineEdit.setText(selectedroot)
                else:
                    return
            updateDictionary()
            return

        def editExecutable(lineEdit):
            # dbItem = (unicode(lineEdit.text()).encode("utf-8"))
            dbItem = (compat.encode(lineEdit.text()))
            try:
                userSettings["executables"][str(lineEdit.objectName())] = dbItem
            except KeyError:
                userSettings["executables"] = {"image_exec": "",
                                               "imageSeq_exec": "",
                                               "video_exec": "",
                                               "obj_exec": "",
                                               "fbx_exec": "",
                                               "alembic_exec": ""}
                userSettings["executables"][str(lineEdit.objectName())] = dbItem
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            return

        def browseExecutable(lineEdit):
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)

            if dlg.exec_():
                # selectedFile = os.path.normpath(unicode(dlg.selectedFiles()[0])).encode("utf-8")
                selectedFile = os.path.normpath(compat.encode(dlg.selectedFiles()[0]))
                # dbItem = (unicode(selectedFile).encode("utf-8"))
                dbItem = (compat.encode(selectedFile))
                lineEdit.setText(dbItem)
                try:
                    userSettings["executables"][str(lineEdit.objectName())] = dbItem
                except KeyError:
                    userSettings["executables"] = {"image_exec": "",
                                                   "imageSeq_exec": "",
                                                   "video_exec": "",
                                                   "obj_exec": "",
                                                   "fbx_exec": "",
                                                   "alembic_exec": ""}
                    userSettings["executables"][str(lineEdit.objectName())] = dbItem
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            return

        for item in userSettings["colorCoding"].items():
            cclabel = QtWidgets.QLabel()
            if item[0] == "":
                cclabel.setText("      Standalone:  ")
            else:
                cclabel.setText("      %s:  " % item[0])
            ccpushbutton = QtWidgets.QPushButton()
            ccpushbutton.setObjectName("cc_%s" % item[0])
            ccpushbutton.setStyleSheet("background-color:%s; min-width: 80px;" % item[1])
            ccpushbutton.setMinimumSize(80, 20)

            colorCoding_formlayout.addRow(cclabel, ccpushbutton)
            ccpushbutton.clicked.connect(
                lambda ignore=item[0], button=ccpushbutton, item=item[0]: colorSet(button, item))

        ccReset_button = QtWidgets.QPushButton()
        ccReset_button.setText("Reset Colors")
        ccReset_button.setMinimumSize(80, 30)
        colorCoding_formlayout.setWidget((len(userSettings["colorCoding"].items())) + 1,
                                         QtWidgets.QFormLayout.FieldRole, ccReset_button)

        # end of form

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        userSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.userSettings_vis)

        # SIGNALS USER SETTINGS
        # ---------------------
        ccReset_button.clicked.connect(resetColors)
        setCommon_button.clicked.connect(browseCommonDatabase)
        globalFavorites_radiobutton.clicked.connect(updateDictionary)
        inherit_range_combo.currentIndexChanged.connect(updateDictionary)
        extra_date_cb.stateChanged.connect(updateDictionary)
        extra_ref_cb.stateChanged.connect(updateDictionary)
        extra_creator_cb.stateChanged.connect(updateDictionary)
        extra_versionCount_cb.stateChanged.connect(updateDictionary)
        localFavorites_radiobutton.clicked.connect(updateDictionary)
        commonDir_lineEdit.editingFinished.connect(updateDictionary)

        exeImages_btn.clicked.connect(lambda: browseExecutable(exeImages_le))
        exeImageSeq_btn.clicked.connect(lambda: browseExecutable(exeImageSeq_le))
        exeVideo_btn.clicked.connect(lambda: browseExecutable(exeVideo_le))
        exeObj_btn.clicked.connect(lambda: browseExecutable(exeObj_le))
        exeFbx_btn.clicked.connect(lambda: browseExecutable(exeFbx_le))
        exeAbc_btn.clicked.connect(lambda: browseExecutable(exeAbc_le))

        exeImages_le.textChanged.connect(lambda: editExecutable(exeImages_le))
        exeImageSeq_le.textChanged.connect(lambda: editExecutable(exeImageSeq_le))
        exeVideo_le.textChanged.connect(lambda: editExecutable(exeVideo_le))
        exeObj_le.textChanged.connect(lambda: editExecutable(exeObj_le))
        exeFbx_le.textChanged.connect(lambda: editExecutable(exeFbx_le))
        exeAbc_le.textChanged.connect(lambda: editExecutable(exeAbc_le))

    def _projectSettingsContent(self):
        settings = self.allSettingsDict.get("projectSettings")

        def updateDictionary():
            settings["Resolution"] = [resolutionX_spinBox.value(), resolutionY_spinBox.value()]
            settings["FPS"] = float(fps_comboBox.currentText())

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        projectSettings_Layout = QtWidgets.QVBoxLayout(self.projectSettings_vis)
        projectSettings_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel(self.projectSettings_vis, font=self.headerAFont, text="Project Settings")
        h1_horizontalLayout.addWidget(h1_label)
        projectSettings_Layout.addLayout(h1_horizontalLayout)

        projectSettings_formLayout = QtWidgets.QFormLayout()
        projectSettings_formLayout.setSpacing(6)
        projectSettings_formLayout.setHorizontalSpacing(15)
        projectSettings_formLayout.setVerticalSpacing(5)
        projectSettings_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)

        projectSettings_formLayout.setContentsMargins(-1, 15, -1, -1)

        currentProject_lbl = QtWidgets.QLabel(text="Project")
        project_hLayout = QtWidgets.QHBoxLayout()
        currentProject_le = QtWidgets.QLineEdit(text=self.manager.getProjectDir(), readOnly=True, minimumWidth=500)
        project_hLayout.addWidget(currentProject_le)

        projectSettings_formLayout.addRow(currentProject_lbl, project_hLayout)

        resolution_label = QtWidgets.QLabel(self.projectSettings_vis, text="Resolution: ", minimumWidth=70,
                                            minimumHeight=25)

        resolution_hLay = QtWidgets.QHBoxLayout()
        resolution_hLay.setSpacing(5)

        resolutionX_spinBox = QtWidgets.QSpinBox(self.projectSettings_vis,
                                                 buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons,
                                                 minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                 minimum=1, maximum=99999, value=settings["Resolution"][0])
        resolution_hLay.addWidget(resolutionX_spinBox)
        resolutionY_spinBox = QtWidgets.QSpinBox(self.projectSettings_vis,
                                                 buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons,
                                                 minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                 minimum=1, maximum=99999, value=settings["Resolution"][1])
        resolution_hLay.addWidget(resolutionY_spinBox)

        projectSettings_formLayout.addRow(resolution_label, resolution_hLay)

        fps_label = QtWidgets.QLabel(self.projectSettings_vis, text="FPS: ", alignment=(
                QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter))

        fps_comboBox = QtWidgets.QComboBox(self.projectSettings_vis)
        fps_comboBox.addItems(self.manager.fpsList)
        try:
            index = self.manager.fpsList.index(str(settings["FPS"]))
        except:
            index = 13
        fps_comboBox.setCurrentIndex(index)

        projectSettings_formLayout.addRow(fps_label, fps_comboBox)

        projectSettings_Layout.addLayout(projectSettings_formLayout)

        cmdButtons_layout = QtWidgets.QVBoxLayout()
        cmdButtons_layout.setContentsMargins(-1, 15, -1, -1)
        projectSettings_Layout.addLayout(cmdButtons_layout)

        previewSettings_cmdButton = QtWidgets.QCommandLinkButton(text="Preview Settings")
        cmdButtons_layout.addWidget(previewSettings_cmdButton)

        categories_cmdButton = QtWidgets.QCommandLinkButton(text="Categories")
        cmdButtons_layout.addWidget(categories_cmdButton)

        importExportOptions_cmdButton = QtWidgets.QCommandLinkButton(text="Import/Export Options")
        cmdButtons_layout.addWidget(importExportOptions_cmdButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        projectSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.projectSettings_vis)

        # SIGNALS
        resolutionX_spinBox.valueChanged.connect(updateDictionary)
        resolutionY_spinBox.valueChanged.connect(updateDictionary)
        fps_comboBox.currentIndexChanged.connect(updateDictionary)

        previewSettings_cmdButton.clicked.connect(
            lambda: self.settingsMenu_treeWidget.setCurrentItem(self.previewSettings_item))
        categories_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.categories_item))
        importExportOptions_cmdButton.clicked.connect(
            lambda: self.settingsMenu_treeWidget.setCurrentItem(self.importExport_item))

    def _previewSettingsContent_maya(self):
        settings = self.allSettingsDict.get("preview_maya")

        def updateMayaCodecs():
            codecList = self.manager.getFormatsAndCodecs()[self.format_Maya_comboBox.currentText()]
            self.codec_Maya_comboBox.clear()
            self.codec_Maya_comboBox.addItems(codecList)
            self.codec_Maya_comboBox.setCurrentText(settings["Codec"])

        previewSettings_MAYA_Layout = QtWidgets.QVBoxLayout()
        previewSettings_MAYA_Layout.setSpacing(0)

        def toggleMp4():
            state = self.convertMP4_Maya_chb.isChecked()
            self.crf_Maya_spinBox.setEnabled(state)
            self.format_Maya_comboBox.setDisabled(state)
            self.codec_Maya_comboBox.setDisabled(state)
            self.quality_Maya_spinBox.setDisabled(state)

        def updateDictionary():

            settings["ConvertMP4"] = self.convertMP4_Maya_chb.isChecked()
            settings["CrfValue"] = self.crf_Maya_spinBox.value()
            settings["Format"] = self.format_Maya_comboBox.currentText()
            settings["Codec"] = self.codec_Maya_comboBox.currentText()
            settings["Quality"] = self.quality_Maya_spinBox.value()
            settings["Resolution"] = [self.resX_Maya_spinBox.value(), self.resY_Maya_spinBox.value()]
            settings["PolygonOnly"] = self.polygonOnly_Maya_chb.isChecked()
            settings["ShowGrid"] = self.showGrid_Maya_chb.isChecked()
            settings["ClearSelection"] = self.clearSelection_Maya_chb.isChecked()
            settings["DisplayTextures"] = self.displayTextures_Maya_chb.isChecked()
            settings["WireOnShaded"] = self.wireOnShaded_Maya_chb.isChecked()
            settings["UseDefaultMaterial"] = self.useDefaultMaterial_Maya_chb.isChecked()
            settings["ShowFrameNumber"] = self.frameNumber_Maya_chb.isChecked()
            settings["ShowCategory"] = self.category_Maya_chb.isChecked()
            settings["ShowSceneName"] = self.sceneName_Maya_chb.isChecked()
            settings["ShowFPS"] = self.fps_Maya_chb.isChecked()
            settings["ShowFrameRange"] = self.frameRange_Maya_chb.isChecked()
            settings["ViewportAsItIs"] = self.viewportAsItIs_chb.isChecked()
            settings["HudsAsItIs"] = self.hudsAsItIs_chb.isChecked()

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        ## HEADER
        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel(font=self.headerAFont, text="Maya Playblast Settings")
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_MAYA_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel(font=self.headerBFont, text="Video Properties  ")
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel(indent=0, maximumHeight=1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setProperty("seperator", True)
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try:
            h1_s1_line.setMargin(0)
        except AttributeError:
            pass
        previewSettings_MAYA_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout(horizontalSpacing=15, verticalSpacing=10, fieldGrowthPolicy=(
            QtWidgets.QFormLayout.FieldsStayAtSizeHint))
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Maya_chb = QtWidgets.QCheckBox(text="Convert To MP4", minimumWidth=100,
                                                       layoutDirection=QtCore.Qt.LeftToRight)
        videoProperties_formLayout.addRow(self.convertMP4_Maya_chb)

        if not self.manager.checkFFMPEG():
            self.convertMP4_Maya_chb.setChecked(False)
            self.convertMP4_Maya_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Maya_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Maya_chb.setChecked(True)

        crf_Maya_label = QtWidgets.QLabel(text="Compression (0-51)")

        self.crf_Maya_spinBox = QtWidgets.QSpinBox(minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                   minimum=0, maximum=51, value=settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Maya_label, self.crf_Maya_spinBox)

        format_label = QtWidgets.QLabel(text="Format: ")
        self.format_Maya_comboBox = QtWidgets.QComboBox()
        videoProperties_formLayout.addRow(format_label, self.format_Maya_comboBox)

        formatsAndCodecs = self.manager.getFormatsAndCodecs()
        if not formatsAndCodecs:
            self.format_Maya_comboBox.setEnabled(False)
        else:
            try:
                self.format_Maya_comboBox.addItems(list(formatsAndCodecs))
                # get the index number from the name in the settings file and make that index active
                ffindex = self.format_Maya_comboBox.findText(settings["Format"], QtCore.Qt.MatchFixedString)
                if ffindex >= 0:
                    self.format_Maya_comboBox.setCurrentIndex(ffindex)
            except:
                pass

        codec_label = QtWidgets.QLabel(text="Codec: ")
        self.codec_Maya_comboBox = QtWidgets.QComboBox()
        videoProperties_formLayout.addRow(codec_label, self.codec_Maya_comboBox)

        if not formatsAndCodecs:
            self.codec_Maya_comboBox.setEnabled(False)
        else:
            updateMayaCodecs()

        self.format_Maya_comboBox.currentIndexChanged.connect(updateMayaCodecs)

        quality_label = QtWidgets.QLabel(text="Quality: ")
        self.quality_Maya_spinBox = QtWidgets.QSpinBox(minimumWidth=self.minSPBSize[0],
                                                       minimumHeight=self.minSPBSize[1], minimum=1, maximum=100,
                                                       value=settings["Quality"])
        videoProperties_formLayout.addRow(quality_label, self.quality_Maya_spinBox)

        resolution_label = QtWidgets.QLabel(text="Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout()
        resolution_horizontalLayout.setSpacing(5)
        self.resX_Maya_spinBox = QtWidgets.QSpinBox(minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                    minimum=1, maximum=99999, value=settings["Resolution"][0],
                                                    buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolution_horizontalLayout.addWidget(self.resX_Maya_spinBox)
        self.resY_Maya_spinBox = QtWidgets.QSpinBox(minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                    minimum=1, maximum=99999, value=settings["Resolution"][1],
                                                    buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolution_horizontalLayout.addWidget(self.resY_Maya_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_MAYA_Layout.addLayout(h1_s2_horizontalLayout)

        ## VIEWPORT OPTIONS
        h1_s3_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s3_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s3_label = QtWidgets.QLabel(font=self.headerBFont, text="Viewport Options  ")
        h1_s3_horizontalLayout.addWidget(h1_s3_label)

        h1_s3_line = QtWidgets.QLabel(indent=0, maximumHeight=1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s3_line.setSizePolicy(sizePolicy)
        h1_s3_line.setProperty("seperator", True)
        h1_s3_horizontalLayout.addWidget(h1_s3_line)
        try:
            h1_s3_line.setMargin(0)
        except AttributeError:
            pass
        previewSettings_MAYA_Layout.addLayout(h1_s3_horizontalLayout)

        h1_s4_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s4_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        viewportOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s4_horizontalLayout.addLayout(viewportOptions_gridLayout)

        self.viewportAsItIs_chb = QtWidgets.QCheckBox(text="Use Active Viewport Settings",
                                                      checked=settings["ViewportAsItIs"])
        viewportOptions_gridLayout.addWidget(self.viewportAsItIs_chb, 0, 0)

        self.polygonOnly_Maya_chb = QtWidgets.QCheckBox(text="Polygon Only", checked=settings["PolygonOnly"])
        viewportOptions_gridLayout.addWidget(self.polygonOnly_Maya_chb, 1, 0)

        self.showGrid_Maya_chb = QtWidgets.QCheckBox(text="Show Grid", checked=settings["ShowGrid"])
        viewportOptions_gridLayout.addWidget(self.showGrid_Maya_chb, 1, 1)

        self.clearSelection_Maya_chb = QtWidgets.QCheckBox(text="Clear Selection", checked=settings["ClearSelection"])
        viewportOptions_gridLayout.addWidget(self.clearSelection_Maya_chb, 2, 0)

        self.displayTextures_Maya_chb = QtWidgets.QCheckBox(text="Display Textures",
                                                            checked=settings["DisplayTextures"])
        viewportOptions_gridLayout.addWidget(self.displayTextures_Maya_chb, 2, 1)

        self.wireOnShaded_Maya_chb = QtWidgets.QCheckBox(text="Wire On Shaded", checked=settings["WireOnShaded"])
        viewportOptions_gridLayout.addWidget(self.wireOnShaded_Maya_chb, 3, 0)

        self.useDefaultMaterial_Maya_chb = QtWidgets.QCheckBox(text="Use Default Material",
                                                               checked=settings["UseDefaultMaterial"])
        viewportOptions_gridLayout.addWidget(self.useDefaultMaterial_Maya_chb, 3, 1)

        previewSettings_MAYA_Layout.addLayout(h1_s4_horizontalLayout)

        ## HUD OPTIONS
        h1_s5_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s5_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s5_label = QtWidgets.QLabel(font=self.headerBFont, text="Heads Up Display Options  ")
        h1_s5_horizontalLayout.addWidget(h1_s5_label)

        h1_s5_line = QtWidgets.QLabel(indent=0, maximumHeight=1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s5_line.setSizePolicy(sizePolicy)
        h1_s5_line.setProperty("seperator", True)
        h1_s5_horizontalLayout.addWidget(h1_s5_line)
        try:
            h1_s5_line.setMargin(0)
        except AttributeError:
            pass
        previewSettings_MAYA_Layout.addLayout(h1_s5_horizontalLayout)

        h1_s6_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s6_horizontalLayout.setContentsMargins(20, 10, -1, 30)

        hudOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s6_horizontalLayout.addLayout(hudOptions_gridLayout)

        self.hudsAsItIs_chb = QtWidgets.QCheckBox(text="Use Active Huds", checked=settings["HudsAsItIs"])
        hudOptions_gridLayout.addWidget(self.hudsAsItIs_chb, 0, 0)

        self.frameNumber_Maya_chb = QtWidgets.QCheckBox(text="Frame Number", checked=settings["ShowFrameNumber"])
        hudOptions_gridLayout.addWidget(self.frameNumber_Maya_chb, 1, 0)

        self.category_Maya_chb = QtWidgets.QCheckBox(text="Category", checked=settings["ShowCategory"])
        hudOptions_gridLayout.addWidget(self.category_Maya_chb, 1, 1)

        self.sceneName_Maya_chb = QtWidgets.QCheckBox(text="Scene Name", checked=settings["ShowSceneName"])
        hudOptions_gridLayout.addWidget(self.sceneName_Maya_chb, 2, 0)

        self.fps_Maya_chb = QtWidgets.QCheckBox(text="FPS", checked=settings["ShowFPS"])
        hudOptions_gridLayout.addWidget(self.fps_Maya_chb, 2, 1)

        self.frameRange_Maya_chb = QtWidgets.QCheckBox(text="Frame Range", checked=settings["ShowFrameRange"])
        hudOptions_gridLayout.addWidget(self.frameRange_Maya_chb, 3, 0)

        previewSettings_MAYA_Layout.addLayout(h1_s6_horizontalLayout)

        self.previewMasterLayout.addLayout(previewSettings_MAYA_Layout)

        toggleMp4()

        ## SIGNALS
        ## -------

        self.convertMP4_Maya_chb.stateChanged.connect(toggleMp4)
        self.convertMP4_Maya_chb.stateChanged.connect(updateDictionary)

        self.crf_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.format_Maya_comboBox.currentIndexChanged.connect(updateDictionary)
        self.codec_Maya_comboBox.currentIndexChanged.connect(updateDictionary)
        self.quality_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.resX_Maya_spinBox.valueChanged.connect(updateDictionary)
        self.resY_Maya_spinBox.valueChanged.connect(updateDictionary)

        self.viewportAsItIs_chb.stateChanged.connect(updateDictionary)
        self.polygonOnly_Maya_chb.stateChanged.connect(updateDictionary)
        self.showGrid_Maya_chb.stateChanged.connect(updateDictionary)
        self.clearSelection_Maya_chb.stateChanged.connect(updateDictionary)
        self.displayTextures_Maya_chb.stateChanged.connect(updateDictionary)
        self.wireOnShaded_Maya_chb.stateChanged.connect(updateDictionary)
        self.useDefaultMaterial_Maya_chb.stateChanged.connect(updateDictionary)

        self.hudsAsItIs_chb.stateChanged.connect(updateDictionary)
        self.frameNumber_Maya_chb.stateChanged.connect(updateDictionary)
        self.category_Maya_chb.stateChanged.connect(updateDictionary)
        self.sceneName_Maya_chb.stateChanged.connect(updateDictionary)
        self.fps_Maya_chb.stateChanged.connect(updateDictionary)
        self.frameRange_Maya_chb.stateChanged.connect(updateDictionary)

    def _previewSettingsContent_max(self):
        settings = self.allSettingsDict.get("preview_max")

        previewSettings_MAX_Layout = QtWidgets.QVBoxLayout()
        previewSettings_MAX_Layout.setSpacing(0)

        def updateDictionary():
            settings["ConvertMP4"] = self.convertMP4_Max_chb.isChecked()
            settings["CrfValue"] = self.crf_Max_spinBox.value()
            settings["Resolution"] = [self.resX_Max_spinBox.value(), self.resY_Max_spinBox.value()]
            settings["PolygonOnly"] = self.polygonOnly_Max_chb.isChecked()
            settings["ShowGrid"] = self.showGrid_Max_chb.isChecked()
            settings["ClearSelection"] = self.clearSelection_Max_chb.isChecked()
            settings["WireOnShaded"] = self.wireOnShaded_Max_chb.isChecked()
            settings["ShowFrameNumber"] = self.frameNumber_Max_chb.isChecked()

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        ## HEADER
        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel(self.previewSettings_vis, font=self.headerAFont,
                                    text="3ds Max Preview Animation Settings")
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_MAX_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel(font=self.headerBFont, text="Video Properties  ")
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel(indent=0, maximumHeight=1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setProperty("seperator", True)
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try:
            h1_s1_line.setMargin(0)
        except AttributeError:
            pass
        previewSettings_MAX_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout(horizontalSpacing=15, verticalSpacing=10,
                                                           fieldGrowthPolicy=QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Max_chb = QtWidgets.QCheckBox(text="Convert To MP4", minimumWidth=100,
                                                      layoutDirection=QtCore.Qt.LeftToRight)
        videoProperties_formLayout.addRow(self.convertMP4_Max_chb)

        if not self.manager.checkFFMPEG():
            self.convertMP4_Max_chb.setChecked(False)
            self.convertMP4_Max_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Max_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Max_chb.setChecked(True)

        crf_Max_label = QtWidgets.QLabel(text="Compression (0-51)")

        self.crf_Max_spinBox = QtWidgets.QSpinBox()
        self.crf_Max_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.crf_Max_spinBox.setMinimum(0)
        self.crf_Max_spinBox.setMaximum(51)
        self.crf_Max_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Max_label, self.crf_Max_spinBox)

        resolution_label = QtWidgets.QLabel()
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout()
        self.resX_Max_spinBox = QtWidgets.QSpinBox(minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                   minimum=1, maximum=99999, value=settings["Resolution"][0],
                                                   buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolution_horizontalLayout.addWidget(self.resX_Max_spinBox)
        self.resY_Max_spinBox = QtWidgets.QSpinBox(minimumWidth=self.minSPBSize[0], minimumHeight=self.minSPBSize[1],
                                                   minimum=1, maximum=99999, value=settings["Resolution"][1],
                                                   buttonSymbols=QtWidgets.QAbstractSpinBox.NoButtons)
        resolution_horizontalLayout.addWidget(self.resY_Max_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_MAX_Layout.addLayout(h1_s2_horizontalLayout)

        ## VIEWPORT OPTIONS
        h1_s3_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s3_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s3_label = QtWidgets.QLabel()
        h1_s3_label.setText("Viewport Options  ")
        h1_s3_label.setFont(self.headerBFont)
        h1_s3_horizontalLayout.addWidget(h1_s3_label)

        h1_s3_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s3_line.setSizePolicy(sizePolicy)
        h1_s3_line.setProperty("seperator", True)
        h1_s3_horizontalLayout.addWidget(h1_s3_line)
        try:
            h1_s3_line.setMargin(0)
        except AttributeError:
            pass
        h1_s3_line.setIndent(0)
        h1_s3_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s3_horizontalLayout)

        h1_s4_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s4_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        viewportOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s4_horizontalLayout.addLayout(viewportOptions_gridLayout)

        self.polygonOnly_Max_chb = QtWidgets.QCheckBox()
        self.polygonOnly_Max_chb.setText("Polygon Only")
        viewportOptions_gridLayout.addWidget(self.polygonOnly_Max_chb, 0, 0)
        self.polygonOnly_Max_chb.setChecked(settings["PolygonOnly"])

        self.showGrid_Max_chb = QtWidgets.QCheckBox()
        self.showGrid_Max_chb.setText("Show Grid")
        viewportOptions_gridLayout.addWidget(self.showGrid_Max_chb, 0, 1)
        self.showGrid_Max_chb.setChecked(settings["ShowGrid"])

        self.clearSelection_Max_chb = QtWidgets.QCheckBox()
        self.clearSelection_Max_chb.setText("Clear Selection")
        viewportOptions_gridLayout.addWidget(self.clearSelection_Max_chb, 1, 0)
        self.clearSelection_Max_chb.setChecked(settings["ClearSelection"])

        self.wireOnShaded_Max_chb = QtWidgets.QCheckBox()
        self.wireOnShaded_Max_chb.setText("Wire On Shaded")
        viewportOptions_gridLayout.addWidget(self.wireOnShaded_Max_chb, 1, 1)
        self.wireOnShaded_Max_chb.setChecked(settings["WireOnShaded"])

        previewSettings_MAX_Layout.addLayout(h1_s4_horizontalLayout)

        ## HUD OPTIONS
        h1_s5_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s5_horizontalLayout.setContentsMargins(-1, 30, -1, -1)
        h1_s5_label = QtWidgets.QLabel()
        h1_s5_label.setText("Heads Up Display Options  ")
        h1_s5_label.setFont(self.headerBFont)
        h1_s5_horizontalLayout.addWidget(h1_s5_label)

        h1_s5_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s5_line.setSizePolicy(sizePolicy)
        h1_s5_line.setProperty("seperator", True)
        h1_s5_horizontalLayout.addWidget(h1_s5_line)
        try:
            h1_s5_line.setMargin(0)
        except AttributeError:
            pass
        h1_s5_line.setIndent(0)
        h1_s5_line.setMaximumHeight(1)
        previewSettings_MAX_Layout.addLayout(h1_s5_horizontalLayout)

        h1_s6_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s6_horizontalLayout.setContentsMargins(20, 10, -1, -1)

        hudOptions_gridLayout = QtWidgets.QGridLayout()
        h1_s6_horizontalLayout.addLayout(hudOptions_gridLayout)

        self.frameNumber_Max_chb = QtWidgets.QCheckBox()
        self.frameNumber_Max_chb.setText("Frame Number")
        hudOptions_gridLayout.addWidget(self.frameNumber_Max_chb, 0, 0)
        self.frameNumber_Max_chb.setChecked(settings["ShowFrameNumber"])

        previewSettings_MAX_Layout.addLayout(h1_s6_horizontalLayout)

        self.previewMasterLayout.addLayout(previewSettings_MAX_Layout)

        ## SIGNALS
        ## -------

        self.convertMP4_Max_chb.stateChanged.connect(updateDictionary)
        self.convertMP4_Max_chb.stateChanged.connect(
            lambda: self.crf_Max_spinBox.setEnabled(self.convertMP4_Max_chb.isChecked()))

        self.crf_Max_spinBox.valueChanged.connect(updateDictionary)
        self.resX_Max_spinBox.valueChanged.connect(updateDictionary)
        self.resY_Max_spinBox.valueChanged.connect(updateDictionary)
        self.polygonOnly_Max_chb.stateChanged.connect(updateDictionary)
        self.showGrid_Max_chb.stateChanged.connect(updateDictionary)
        self.clearSelection_Max_chb.stateChanged.connect(updateDictionary)
        self.wireOnShaded_Max_chb.stateChanged.connect(updateDictionary)
        self.frameNumber_Max_chb.stateChanged.connect(updateDictionary)

        # spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.previewMasterLayout.addItem(spacerItem)

        # self.contentsMaster_layout.addWidget(self.previewSettings_vis)

    def _previewSettingsContent_houdini(self):
        # manager = self._getManager()
        # settings = self.allSettingsDict["preview_houdini"]["oldSettings"]
        settings = self.allSettingsDict.get("preview_houdini")

        previewSettings_HOU_Layout = QtWidgets.QVBoxLayout()
        previewSettings_HOU_Layout.setSpacing(0)

        def updateDictionary():
            settings["ConvertMP4"] = self.convertMP4_Houdini_chb.isChecked()
            settings["CrfValue"] = self.crf_Houdini_spinBox.value()
            settings["Resolution"] = [self.resX_Houdini_spinBox.value(), self.resY_Houdini_spinBox.value()]

            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            # self._isSettingsChanged()

        ## HEADER
        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        # h1_horizontalLayout.setContentsMargins(-1, -1, -1, 10)
        h1_label = QtWidgets.QLabel(self.previewSettings_vis)
        h1_label.setText("Houdini Flipbook Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        previewSettings_HOU_Layout.addLayout(h1_horizontalLayout)

        ## VIDEO PROPERTIES
        h1_s1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s1_horizontalLayout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_label = QtWidgets.QLabel()
        h1_s1_label.setText("Video Properties  ")
        h1_s1_label.setFont(self.headerBFont)
        h1_s1_horizontalLayout.addWidget(h1_s1_label)

        h1_s1_line = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        h1_s1_line.setSizePolicy(sizePolicy)
        h1_s1_line.setProperty("seperator", True)
        h1_s1_horizontalLayout.addWidget(h1_s1_line)
        try:
            h1_s1_line.setMargin(0)
        except AttributeError:
            pass
        h1_s1_line.setIndent(0)
        h1_s1_line.setMaximumHeight(1)
        previewSettings_HOU_Layout.addLayout(h1_s1_horizontalLayout)

        h1_s2_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_s2_horizontalLayout.setContentsMargins(20, 10, -1, -1)
        h1_s2_horizontalLayout.setSpacing(6)

        videoProperties_formLayout = QtWidgets.QFormLayout()
        videoProperties_formLayout.setSpacing(6)
        videoProperties_formLayout.setHorizontalSpacing(15)
        videoProperties_formLayout.setVerticalSpacing(10)
        videoProperties_formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        h1_s2_horizontalLayout.addLayout(videoProperties_formLayout)

        self.convertMP4_Houdini_chb = QtWidgets.QCheckBox()
        self.convertMP4_Houdini_chb.setText("Convert To MP4")
        self.convertMP4_Houdini_chb.setMinimumSize(QtCore.QSize(100, 0))
        self.convertMP4_Houdini_chb.setLayoutDirection(QtCore.Qt.LeftToRight)
        # videoProperties_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.convertMP4_Houdini_chb)
        videoProperties_formLayout.addRow(self.convertMP4_Houdini_chb)

        if not self.manager.checkFFMPEG():
            self.convertMP4_Houdini_chb.setChecked(False)
            self.convertMP4_Houdini_chb.setEnabled(False)
        else:
            try:
                self.convertMP4_Houdini_chb.setChecked(settings["ConvertMP4"])
            except KeyError:
                self.convertMP4_Houdini_chb.setChecked(True)

        crf_Houdini_label = QtWidgets.QLabel()
        crf_Houdini_label.setText("Compression (0-51)")

        self.crf_Houdini_spinBox = QtWidgets.QSpinBox()
        self.crf_Houdini_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.crf_Houdini_spinBox.setMinimum(0)
        self.crf_Houdini_spinBox.setMaximum(51)
        self.crf_Houdini_spinBox.setValue(settings["CrfValue"])
        videoProperties_formLayout.addRow(crf_Houdini_label, self.crf_Houdini_spinBox)

        resolution_label = QtWidgets.QLabel()
        resolution_label.setText("Resolution: ")
        resolution_horizontalLayout = QtWidgets.QHBoxLayout()
        self.resX_Houdini_spinBox = QtWidgets.QSpinBox()
        self.resX_Houdini_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resX_Houdini_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resX_Houdini_spinBox.setMinimum(1)
        self.resX_Houdini_spinBox.setMaximum(99999)
        self.resX_Houdini_spinBox.setValue(settings["Resolution"][0])
        resolution_horizontalLayout.addWidget(self.resX_Houdini_spinBox)
        self.resY_Houdini_spinBox = QtWidgets.QSpinBox()
        self.resY_Houdini_spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resY_Houdini_spinBox.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
        self.resY_Houdini_spinBox.setMinimum(1)
        self.resY_Houdini_spinBox.setMaximum(99999)
        self.resY_Houdini_spinBox.setValue(settings["Resolution"][1])
        resolution_horizontalLayout.addWidget(self.resY_Houdini_spinBox)
        videoProperties_formLayout.addRow(resolution_label, resolution_horizontalLayout)

        previewSettings_HOU_Layout.addLayout(h1_s2_horizontalLayout)

        self.previewMasterLayout.addLayout(previewSettings_HOU_Layout)

        ## SIGNALS
        ## -------

        self.convertMP4_Houdini_chb.stateChanged.connect(updateDictionary)
        self.convertMP4_Houdini_chb.stateChanged.connect(
            lambda: self.crf_Houdini_spinBox.setEnabled(self.convertMP4_Houdini_chb.isChecked()))

        self.crf_Houdini_spinBox.valueChanged.connect(updateDictionary)
        self.resX_Houdini_spinBox.valueChanged.connect(updateDictionary)
        self.resY_Houdini_spinBox.valueChanged.connect(updateDictionary)

    def _categoriesContent(self):
        # manager = self._getManager()
        categorySwList = [key for key in self.allSettingsDict.listNames() if key.startswith("categories")]

        categories_Layout = QtWidgets.QVBoxLayout(self.categories_vis)
        categories_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Add/Remove Categories")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        categories_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        swTabs = QtWidgets.QTabWidget()
        swTabs.setMaximumSize(QtCore.QSize(16777215, 167777))
        swTabs.setTabPosition(QtWidgets.QTabWidget.North)
        swTabs.setElideMode(QtCore.Qt.ElideNone)
        swTabs.setUsesScrollButtons(False)

        def onMoveCategory(settingKey, listWidget, direction):
            row = listWidget.currentRow()
            if row == -1:
                return
            dir = 1 if direction == "down" else -1

            categories = self.allSettingsDict.get(settingKey)
            item_name = categories[row]
            # all_items = [str(listWidget.item(i).text()) for i in range(listWidget.count())]

            new_row = row + dir
            if not (0 <= new_row <= len(categories)):
                return

            item_at_new_row = categories[new_row]

            categories[new_row] = item_name
            categories[row] = item_at_new_row

            listWidget.clear()
            listWidget.addItems(categories)
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            listWidget.setCurrentRow(new_row)

        def onRemove(settingKey, listWidget):
            row = listWidget.currentRow()
            if row == -1:
                return
            # trashCategory = unicode(listWidget.currentItem().text()).decode("utf-8")
            trashCategory = compat.decode(listWidget.currentItem().text())
            categories = self.allSettingsDict.get(settingKey)
            ## check if this is the last category
            if len(categories) == 1:
                self.infoPop(textTitle="Cannot Remove Category",
                             textHeader="Last Category cannot be removed")
            ## Check if this category is REALLY trash
            niceName = settingKey.replace("categories_", "")
            dbPath = os.path.normpath(
                os.path.join(self.manager._pathsDict["masterDir"], self.softwareDB[niceName]["databaseDir"]))
            manager = self._getManager()
            if manager.isCategoryTrash(trashCategory, dbPath=dbPath):
                categories.remove(trashCategory)
                listWidget.clear()
                listWidget.addItems(categories)
            else:
                self.infoPop(textTitle="Cannot Remove Category",
                             textHeader="%s Category is not empty. Aborting..." % trashCategory)
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def onAdd(settingKey, listWidget):
            addCategory_Dialog = QtWidgets.QDialog(parent=self)
            addCategory_Dialog.resize(260, 114)
            addCategory_Dialog.setMaximumSize(QtCore.QSize(16777215, 150))
            addCategory_Dialog.setFocusPolicy(QtCore.Qt.ClickFocus)
            addCategory_Dialog.setWindowTitle(("Add New Category"))

            verticalLayout = QtWidgets.QVBoxLayout(addCategory_Dialog)

            addNewCategory_label = QtWidgets.QLabel(addCategory_Dialog)
            addNewCategory_label.setText("Add New Category:")
            verticalLayout.addWidget(addNewCategory_label)

            categoryName_lineEdit = QtWidgets.QLineEdit(addCategory_Dialog)
            categoryName_lineEdit.setPlaceholderText("e.g \'Shading\'")
            verticalLayout.addWidget(categoryName_lineEdit)

            buttonBox = QtWidgets.QDialogButtonBox(addCategory_Dialog)
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
            verticalLayout.addWidget(buttonBox)
            addCategory_Dialog.show()

            buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))

            def addCategory():
                # newCategory = unicode(categoryName_lineEdit.text()).decode("utf-8")
                newCategory = compat.decode(categoryName_lineEdit.text())
                categories = self.allSettingsDict.get(settingKey)
                for x in categories:
                    if newCategory.lower() == x.lower():
                        self.infoPop(textTitle="Cannot Add Category",
                                     textHeader="%s category already exist" % newCategory)
                        return False

                categories.append(newCategory)
                listWidget.clear()
                listWidget.addItems(categories)
                addCategory_Dialog.accept()
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

            buttonBox.accepted.connect(addCategory)
            buttonBox.rejected.connect(addCategory_Dialog.reject)

        for cat in sorted(categorySwList):
            tabWidget = QtWidgets.QWidget()
            horizontalLayout = QtWidgets.QHBoxLayout(tabWidget)
            categories_listWidget = QtWidgets.QListWidget()
            horizontalLayout.addWidget(categories_listWidget)

            verticalLayout = QtWidgets.QVBoxLayout()
            verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

            add_pushButton = QtWidgets.QPushButton()
            add_pushButton.setText(("Add..."))
            verticalLayout.addWidget(add_pushButton)

            remove_pushButton = QtWidgets.QPushButton()
            remove_pushButton.setText(("Remove"))
            verticalLayout.addWidget(remove_pushButton)

            move_up_pb = QtWidgets.QPushButton()
            move_up_pb.setText(("Move Up"))
            verticalLayout.addWidget(move_up_pb)

            move_down_pb = QtWidgets.QPushButton()
            move_down_pb.setText(("Move Down"))
            verticalLayout.addWidget(move_down_pb)

            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            verticalLayout.addItem(spacerItem)

            horizontalLayout.addLayout(verticalLayout)

            swTabs.addTab(tabWidget, cat.replace("categories_", ""))

            categories_listWidget.addItems(self.allSettingsDict[cat]["newSettings"])
            add_pushButton.clicked.connect(
                lambda ignore=1, settingKey=cat, listWidget=categories_listWidget: onAdd(settingKey, listWidget))
            # add_pushButton.clicked.connect(lambda: onAdd(cat, categories_listWidget))
            remove_pushButton.clicked.connect(
                lambda ignore=1, settingKey=cat, listWidget=categories_listWidget: onRemove(settingKey, listWidget))
            # remove_pushButton.clicked.connect(lambda: onRemove(cat, categories_listWidget))
            move_up_pb.clicked.connect(lambda ignore=1, settingKey=cat, listWidget=categories_listWidget: onMoveCategory(settingKey, listWidget, "up"))
            move_down_pb.clicked.connect(lambda ignore=1, settingKey=cat, listWidget=categories_listWidget: onMoveCategory(settingKey, listWidget, "down"))

        h1_s1_layout.addWidget(swTabs)
        categories_Layout.addLayout(h1_s1_layout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        categories_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.categories_vis)

    def _importExportContent(self):

        sw = ENV_DATA["dcc"].lower()
        exportSettings = self.allSettingsDict.get("exportSettings")
        importSettings = self.allSettingsDict.get("importSettings")

        def updateImportDictionary(sw, key, value):
            importSettings[sw][key] = value
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def updateExportDictionary(sw, key, value):
            exportSettings[sw][key] = value
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
            pass

        importExport_Layout = QtWidgets.QVBoxLayout(self.importExportOptions_vis)
        importExport_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Import/Export Geometry Settings")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        importExport_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        softwaresTabWidget = QtWidgets.QTabWidget()
        softwaresTabWidget.setMaximumSize(QtCore.QSize(16777215, 167777))
        softwaresTabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        softwaresTabWidget.setElideMode(QtCore.Qt.ElideNone)
        softwaresTabWidget.setUsesScrollButtons(False)

        ## TEMP
        # sw="standalone"

        if sw == "maya" or sw == "standalone":
            mayaTab = QtWidgets.QWidget()
            maya_verticalLayout = QtWidgets.QVBoxLayout(mayaTab)
            maya_verticalLayout.setSpacing(0)

            softwaresTabWidget.addTab(mayaTab, "Maya")

            formatsTabWidget = QtWidgets.QTabWidget(mayaTab)
            objTab = QtWidgets.QWidget(mayaTab)
            fbxTab = QtWidgets.QWidget(mayaTab)
            alembicTab = QtWidgets.QWidget(mayaTab)
            vrayProxyTab = QtWidgets.QWidget(mayaTab)
            formatsTabWidget.addTab(objTab, "Obj")
            formatsTabWidget.addTab(fbxTab, "FBX")
            formatsTabWidget.addTab(alembicTab, "Alembic")
            formatsTabWidget.addTab(vrayProxyTab, "VrayProxy")
            maya_verticalLayout.addWidget(formatsTabWidget)

            ## MAYA OBJ
            ## --------
            def _maya_obj():
                obj_horizontal_layout = QtWidgets.QHBoxLayout(objTab)
                obj_import_layout = QtWidgets.QVBoxLayout()
                obj_seperator = QtWidgets.QLabel()
                obj_seperator.setProperty("seperator", True)
                obj_seperator.setMaximumWidth(2)
                obj_export_layout = QtWidgets.QVBoxLayout()

                obj_horizontal_layout.addLayout(obj_import_layout)
                obj_horizontal_layout.addWidget(obj_seperator)
                obj_horizontal_layout.addLayout(obj_export_layout)

                ## MAYA OBJ IMPORT WIDGETS
                obj_import_label = QtWidgets.QLabel()
                obj_import_label.setText("Obj Import Settings")
                obj_import_label.setFont(self.headerBFont)
                obj_import_layout.addWidget(obj_import_label)

                obj_import_formlayout = QtWidgets.QFormLayout()
                obj_import_formlayout.setSpacing(6)
                obj_import_formlayout.setHorizontalSpacing(15)
                obj_import_formlayout.setVerticalSpacing(10)
                obj_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_import_layout.addLayout(obj_import_formlayout)

                mayaObjImpCreateDict = [
                    {"NiceName": "Legacy Vertex Ordering", "DictName": "LegacyVertexOrdering", "Type": "chb",
                     "asFlag": "lo="},
                    {"NiceName": "Multiple Objects", "DictName": "MultipleObjects", "Type": "chb", "asFlag": "mo="},
                ]
                self._createFormWidgets(mayaObjImpCreateDict, importSettings, "objImportMaya",
                                        obj_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_import_layout.addItem(spacerItem)

                ## MAYA OBJ EXPORT WIDGETS
                obj_export_label = QtWidgets.QLabel()
                obj_export_label.setText("Obj Export Settings")
                obj_export_label.setFont(self.headerBFont)
                obj_export_layout.addWidget(obj_export_label)

                obj_export_formlayout = QtWidgets.QFormLayout()
                obj_export_formlayout.setSpacing(6)
                obj_export_formlayout.setHorizontalSpacing(15)
                obj_export_formlayout.setVerticalSpacing(10)
                obj_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_export_layout.addLayout(obj_export_formlayout)

                mayaObjExpCreateDict = [
                    {"NiceName": "Normals", "DictName": "normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Materials", "DictName": "materials", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Point Groups", "DictName": "ptgroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Groups", "DictName": "groups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing", "DictName": "smoothing", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(mayaObjExpCreateDict, exportSettings, "objExportMaya",
                                        obj_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_export_layout.addItem(spacerItem)

            ## MAYA FBX
            ## --------
            def _maya_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setProperty("seperator", True)
                fbx_seperator.setMaximumWidth(2)
                fbx_export_layout = QtWidgets.QVBoxLayout()

                fbx_horizontal_layout.addLayout(fbx_import_layout)
                fbx_horizontal_layout.addWidget(fbx_seperator)
                fbx_horizontal_layout.addLayout(fbx_export_layout)

                ## MAYA FBX IMPORT WIDGETS
                fbx_import_label = QtWidgets.QLabel()
                fbx_import_label.setText("Fbx Import Settings")
                fbx_import_label.setFont(self.headerBFont)
                fbx_import_layout.addWidget(fbx_import_label)

                fbx_import_formlayout = QtWidgets.QFormLayout()
                fbx_import_formlayout.setSpacing(6)
                fbx_import_formlayout.setHorizontalSpacing(15)
                fbx_import_formlayout.setVerticalSpacing(10)
                fbx_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_import_layout.addLayout(fbx_import_formlayout)

                mayaFbxImpCreateDict = [
                    {"NiceName": "Up Axis: ", "DictName": "FBXImportUpAxis", "Type": "combo", "items": ["y", "z"],
                     "asFlag": ""},
                    {"NiceName": "Import Mode: ", "DictName": "FBXImportMode", "Type": "combo",
                     "items": ["add", "merge", "exmerge"], "asFlag": "-v "},
                    {"NiceName": "Scale Factor: ", "DictName": "FBXImportScaleFactor", "Type": "spbDouble",
                     "asFlag": ""},
                    {"NiceName": "Treat Quaternions: ", "DictName": "FBXImportQuaternion", "Type": "combo",
                     "items": ["quaternion", "euler", "resample"], "asFlag": "-v "},
                    {"NiceName": "Resampling Rate Source: ", "DictName": "FBXImportResamplingRateSource",
                     "Type": "combo", "items": ["Scene", "File"], "asFlag": "-v "},
                    {"NiceName": "Merge Back Null Pivots: ", "DictName": "FBXImportMergeBackNullPivots", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Set Locked Attribute: ", "DictName": "FBXImportSetLockedAttribute", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Unlock Normals: ", "DictName": "FBXImportUnlockNormals", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Protect Driven Keys: ", "DictName": "FBXImportProtectDrivenKeys", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Shapes: ", "DictName": "FBXImportShapes", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Cameras: ", "DictName": "FBXImportCameras", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Set Maya Frame Rate: ", "DictName": "FBXImportSetMayaFrameRate", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Generate Log: ", "DictName": "FBXImportGenerateLog", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Constraints: ", "DictName": "FBXImportConstraints", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Lights: ", "DictName": "FBXImportLights", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Convert Nulls to Joints: ", "DictName": "FBXImportConvertDeformingNullsToJoint",
                     "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Fill Timeline: ", "DictName": "FBXImportFillTimeline", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Merge Animation Layers: ", "DictName": "FBXImportMergeAnimationLayers", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Hard Edges: ", "DictName": "FBXImportHardEdges", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Axis Conversion Enable: ", "DictName": "FBXImportAxisConversionEnable", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Cache File: ", "DictName": "FBXImportCacheFile", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Skins: ", "DictName": "FBXImportSkins", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Convert Unit String: ", "DictName": "FBXImportConvertUnitString", "Type": "chb",
                     "asFlag": "-v "},
                ]
                self._createFormWidgets(mayaFbxImpCreateDict, importSettings, "fbxImportMaya", fbx_import_formlayout,
                                        updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## MAYA FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_formlayout.setSpacing(6)
                fbx_export_formlayout.setHorizontalSpacing(15)
                fbx_export_formlayout.setVerticalSpacing(10)
                fbx_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_export_layout.addLayout(fbx_export_formlayout)

                mayaFbxExpCreateDict = [
                    {"NiceName": "Up Axis: ", "DictName": "FBXExportUpAxis", "Type": "combo", "items": ["y", "z"],
                     "asFlag": ""},
                    {"NiceName": "Axis Conversion Method: ", "DictName": "FBXExportAxisConversionMethod",
                     "Type": "combo", "items": ["none", "convertAnimation", "addFbxRoot"], "asFlag": ""},
                    {"NiceName": "Bake Step: ", "DictName": "FBXExportBakeComplexStep", "Type": "spbInt",
                     "asFlag": "-v "},
                    {"NiceName": "Convert Units: ", "DictName": "FBXExportConvertUnitString", "Type": "combo",
                     "items": ["mm", "dm", "cm", "m", "km", "In", "ft", "yd", "mi"], "asFlag": ""},
                    {"NiceName": "Treat Quaternion: ", "DictName": "FBXExportQuaternion", "Type": "combo",
                     "items": ["quaternion", "euler", "resample"], "asFlag": "-v "},
                    {"NiceName": "FBX Version: ", "DictName": "FBXExportFileVersion", "Type": "str", "asFlag": "-v "},
                    {"NiceName": "Scale Factor: ", "DictName": "FBXExportScaleFactor", "Type": "spbDouble",
                     "asFlag": ""},
                    {"NiceName": "Apply Constant Key Reducer: ", "DictName": "FBXExportApplyConstantKeyReducer",
                     "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Shapes: ", "DictName": "FBXExportShapes", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Use Scene Name: ", "DictName": "FBXExportUseSceneName", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Skeleton Definitions: ", "DictName": "FBXExportSkeletonDefinitions", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Instances: ", "DictName": "FBXExportInstances", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Cameras: ", "DictName": "FBXExportCameras", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "FBXExportTangents: ", "DictName": "FBXExportTangents", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Ascii: ", "DictName": "FBXExportInAscii", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Lights: ", "DictName": "FBXExportLights", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Referenced Assets: ", "DictName": "FBXExportReferencedAssetsContent", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Constraints: ", "DictName": "FBXExportConstraints", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Smooth Mesh: ", "DictName": "FBXExportSmoothMesh", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Hard Edges: ", "DictName": "FBXExportHardEdges", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Input Connections: ", "DictName": "FBXExportInputConnections", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Embed Textures: ", "DictName": "FBXExportEmbeddedTextures", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Bake Animation: ", "DictName": "FBXExportBakeComplexAnimation", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Cache File: ", "DictName": "FBXExportCacheFile", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Smoothing Groups: ", "DictName": "FBXExportSmoothingGroups", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Resample Animation: ", "DictName": "FBXExportBakeResampleAnimation", "Type": "chb",
                     "asFlag": "-v "},
                    {"NiceName": "Triangulate: ", "DictName": "FBXExportTriangulate", "Type": "chb", "asFlag": "-v "},
                    {"NiceName": "Skins: ", "DictName": "FBXExportSkins", "Type": "chb", "asFlag": "-v "},
                ]
                self._createFormWidgets(mayaFbxExpCreateDict, exportSettings, "fbxExportMaya", fbx_export_formlayout,
                                        updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## MAYA ALEMBIC
            ## ------------
            def _maya_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setProperty("seperator", True)
                alembic_seperator.setMaximumWidth(2)
                alembic_export_layout = QtWidgets.QVBoxLayout()

                alembic_horizontal_layout.addLayout(alembic_import_layout)
                alembic_horizontal_layout.addWidget(alembic_seperator)
                alembic_horizontal_layout.addLayout(alembic_export_layout)

                ## MAYA ALEMBIC IMPORT WIDGETS
                alembic_import_label = QtWidgets.QLabel()
                alembic_import_label.setText("Alembic Import Settings")
                alembic_import_label.setFont(self.headerBFont)
                alembic_import_layout.addWidget(alembic_import_label)

                alembic_import_formlayout = QtWidgets.QFormLayout()
                alembic_import_formlayout.setSpacing(6)
                alembic_import_formlayout.setHorizontalSpacing(15)
                alembic_import_formlayout.setVerticalSpacing(10)
                alembic_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_import_layout.addLayout(alembic_import_formlayout)

                mayaAlembicImpCreateDict = [
                    {"NiceName": "Fit Time Range: ", "DictName": "fitTimeRange", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Set To Start Frame: ", "DictName": "setToStartFrame", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(mayaAlembicImpCreateDict, importSettings, "alembicImportMaya",
                                        alembic_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## MAYA ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_formlayout.setSpacing(6)
                alembic_export_formlayout.setHorizontalSpacing(15)
                alembic_export_formlayout.setVerticalSpacing(10)
                alembic_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_export_layout.addLayout(alembic_export_formlayout)

                mayaAlembicExpCreateDict = [
                    {"NiceName": "Step: ", "DictName": "step", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Data Format: ", "DictName": "dataFormat", "Type": "combo", "items": ["Ogawa", "HDF5"],
                     "asFlag": ""},
                    {"NiceName": "Face Sets: ", "DictName": "writeFaceSets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Uv Sets: ", "DictName": "writeUVSets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "No Normals: ", "DictName": "noNormals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Auto Subdivide: ", "DictName": "autoSubd", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Strip Namespaces: ", "DictName": "stripNamespaces", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Whole Frame Geo: ", "DictName": "wholeFrameGeo", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Renderable Only: ", "DictName": "renderableOnly", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Worldspace: ", "DictName": "worldSpace", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Visibility: ", "DictName": "writeVisibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Euler Filter: ", "DictName": "eulerFilter", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Color Sets: ", "DictName": "writeColorSets", "Type": "chb", "asFlag": ""},
                    {"NiceName": "UV: ", "DictName": "uvWrite", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(mayaAlembicExpCreateDict, exportSettings, "alembicExportMaya",
                                        alembic_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            ## MAYA vrayProxy
            ## ------------
            def _maya_vrayProxy():
                vrayProxy_horizontal_layout = QtWidgets.QHBoxLayout(vrayProxyTab)
                vrayProxy_import_layout = QtWidgets.QVBoxLayout()
                vrayProxy_seperator = QtWidgets.QLabel()
                vrayProxy_seperator.setProperty("seperator", True)
                vrayProxy_seperator.setMaximumWidth(2)
                vrayProxy_export_layout = QtWidgets.QVBoxLayout()

                vrayProxy_horizontal_layout.addLayout(vrayProxy_import_layout)
                vrayProxy_horizontal_layout.addWidget(vrayProxy_seperator)
                vrayProxy_horizontal_layout.addLayout(vrayProxy_export_layout)

                ## MAYA vrayProxy IMPORT WIDGETS
                vrayProxy_import_label = QtWidgets.QLabel()
                vrayProxy_import_label.setText("vrayProxy Import Settings")
                vrayProxy_import_label.setFont(self.headerBFont)
                vrayProxy_import_layout.addWidget(vrayProxy_import_label)

                vrayProxy_import_formlayout = QtWidgets.QFormLayout()
                vrayProxy_import_formlayout.setSpacing(6)
                vrayProxy_import_formlayout.setHorizontalSpacing(15)
                vrayProxy_import_formlayout.setVerticalSpacing(10)
                vrayProxy_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                vrayProxy_import_layout.addLayout(vrayProxy_import_formlayout)

                mayavrayProxyImpCreateDict = [
                ]
                self._createFormWidgets(mayavrayProxyImpCreateDict, importSettings, "vrayImportMaya",
                                        vrayProxy_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                vrayProxy_import_layout.addItem(spacerItem)

                ## MAYA vrayProxy EXPORT WIDGETS
                vrayProxy_export_label = QtWidgets.QLabel()
                vrayProxy_export_label.setText("vrayProxy Export Settings")
                vrayProxy_export_label.setFont(self.headerBFont)
                vrayProxy_export_layout.addWidget(vrayProxy_export_label)

                vrayProxy_export_formlayout = QtWidgets.QFormLayout()
                vrayProxy_export_formlayout.setSpacing(6)
                vrayProxy_export_formlayout.setHorizontalSpacing(15)
                vrayProxy_export_formlayout.setVerticalSpacing(10)
                vrayProxy_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                vrayProxy_export_layout.addLayout(vrayProxy_export_formlayout)

                mayavrayProxyExpCreateDict = [
                    {"NiceName": "Export Type: ", "DictName": "exportType", "Type": "combo", "items": ["Single_File", "Seperate_Files"], "asFlag": ""},
                    {"NiceName": "Export Velocity: ", "DictName": "velocityOn", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Velocity Interval Start: ", "DictName": "velocityIntervalStart", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Velocity Interval End: ", "DictName": "velocityIntervalEnd", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Lowest Level Point Size: ", "DictName": "pointSize", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Faces in Preview: ", "DictName": "previewFaces", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Preview Type: ", "DictName": "previewType", "Type": "combo", "items": ["clustering", "edge_collapse", "face_sampling", "combined"], "asFlag": ""},
                    {"NiceName": "Export Vertex Colors: ", "DictName": "vertexColorsOn", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Ignore Hidden and templated objects: ", "DictName": "ignoreHiddenObjects", "Type": "chb", "asFlag": ""},
                    {"NiceName": "One voxel per mesh: ", "DictName": "oneVoxelPerMesh", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Faces Per Voxel: ", "DictName": "facesPerVoxel", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Automatically Create Proxies: ", "DictName": "createProxyNode", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Make backup: ", "DictName": "makeBackup", "Type": "chb", "asFlag": ""}
                ]
                self._createFormWidgets(mayavrayProxyExpCreateDict, exportSettings, "vrayExportMaya",
                                        vrayProxy_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                vrayProxy_export_layout.addItem(spacerItem)

            _maya_obj()
            _maya_fbx()
            _maya_alembic()
            _maya_vrayProxy()

        if sw == "3dsmax" or sw == "standalone":
            maxTab = QtWidgets.QWidget()
            max_verticalLayout = QtWidgets.QVBoxLayout(maxTab)
            max_verticalLayout.setSpacing(0)

            softwaresTabWidget.addTab(maxTab, "3dsMax")

            formatsTabWidget = QtWidgets.QTabWidget(maxTab)
            objTab = QtWidgets.QWidget(maxTab)
            fbxTab = QtWidgets.QWidget(maxTab)
            alembicTab = QtWidgets.QWidget(maxTab)
            formatsTabWidget.addTab(objTab, "Obj")
            formatsTabWidget.addTab(fbxTab, "FBX")
            formatsTabWidget.addTab(alembicTab, "Alembic")
            max_verticalLayout.addWidget(formatsTabWidget)

            ## MAX OBJ
            ## --------
            def _max_obj():
                obj_horizontal_layout = QtWidgets.QHBoxLayout(objTab)
                obj_import_layout = QtWidgets.QVBoxLayout()
                obj_seperator = QtWidgets.QLabel()
                obj_seperator.setProperty("seperator", True)
                obj_seperator.setMaximumWidth(2)
                obj_export_layout = QtWidgets.QVBoxLayout()

                obj_horizontal_layout.addLayout(obj_import_layout)
                obj_horizontal_layout.addWidget(obj_seperator)
                obj_horizontal_layout.addLayout(obj_export_layout)

                ## MAX OBJ IMPORT WIDGETS
                obj_import_label = QtWidgets.QLabel()
                obj_import_label.setText("Obj Import Settings")
                obj_import_label.setFont(self.headerBFont)
                obj_import_layout.addWidget(obj_import_label)

                obj_import_formlayout = QtWidgets.QFormLayout()
                obj_import_formlayout.setSpacing(6)
                obj_import_formlayout.setHorizontalSpacing(15)
                obj_import_formlayout.setVerticalSpacing(10)
                obj_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_import_layout.addLayout(obj_import_formlayout)

                # CREATE WIDGETS
                maxObjImpCreateDict = [
                    {"NiceName": "General", "DictName": "General", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Use Logging", "DictName": "UseLogging", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Reset Scene", "DictName": "ResetScene", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Objects", "DictName": "Objects", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Import as single mesh", "DictName": "SingleMesh", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import as Editable Poly", "DictName": "AsEditablePoly", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Retriangulate", "DictName": "Retriangulate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Flip ZY-axis", "DictName": "FlipZyAxis", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Center Pivots", "DictName": "CenterPivots", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shapes/Lines", "DictName": "Shapes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Texture coordinates", "DictName": "TextureCoords", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing groups", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals Type: ", "DictName": "NormalsType", "Type": "combo",
                     "items": ["Import from file", "From SM group", "Auto Smooth", "Faceted"], "asFlag": ""},
                    {"NiceName": "Smooth Angle: ", "DictName": "SmoothAngle", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Flip Normals: ", "DictName": "FlipNormals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Units/Scale", "DictName": "Units/Scale", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Convert", "DictName": "Convert", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert From: ", "DictName": "ConvertFrom", "Type": "combo",
                     "items": ["Inches", "Feet", "Miles", "Millimeters", "Centimeters", "Meters", "Kilometers"],
                     "asFlag": ""},
                    {"NiceName": "Object Scale: ", "DictName": "ObjScale", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Material", "DictName": "Material", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Unique Wire Color", "DictName": "UniqueWireColor", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Materials", "DictName": "ImportMaterials", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Default Bump: ", "DictName": "DefaultBump", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Force Black Ambient", "DictName": "ForceBlackAmbient", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Into Mat-Editor", "DictName": "ImportIntoMatEditor", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Show maps in viewport", "DictName": "ShowMapsInViewport", "Type": "chb", "asFlag": ""}
                ]
                self._createFormWidgets(maxObjImpCreateDict, importSettings, "objImportMax", obj_import_formlayout,
                                        updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_import_layout.addItem(spacerItem)

                ## MAX OBJ EXPORT WIDGETS

                obj_export_label = QtWidgets.QLabel()
                obj_export_label.setText("Obj Export Settings")
                obj_export_label.setFont(self.headerBFont)
                obj_export_layout.addWidget(obj_export_label)

                obj_export_formlayout = QtWidgets.QFormLayout()
                obj_export_formlayout.setSpacing(6)
                obj_export_formlayout.setHorizontalSpacing(15)
                obj_export_formlayout.setVerticalSpacing(10)
                obj_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                obj_export_layout.addLayout(obj_export_formlayout)

                maxObjExpCreateDict = [
                    {"NiceName": "Geometry", "DictName": "Geometry", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Flip ZY-axis", "DictName": "FlipZyAxis", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shapes/Lines", "DictName": "Shapes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hidden Objects", "DictName": "ExportHiddenObjects", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Faces: ", "DictName": "FaceType", "Type": "combo",
                     "items": ["Triangles", "Quads", "Polygons"], "asFlag": ""},
                    {"NiceName": "Texture Coordinates", "DictName": "TextureCoords", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals", "DictName": "Normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing Groups", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Object Scale: ", "DictName": "ObjScale", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Output", "DictName": "Output", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Relative Numbers", "DictName": "RelativeIndex", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Target: ", "DictName": "Target", "Type": "combo", "items": ["PC/Win", "Unix", "Mac"],
                     "asFlag": ""},
                    {"NiceName": "Precision: ", "DictName": "Precision", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Optimize", "DictName": "Optimize", "Type": "inf", "asFlag": ""},
                    {"NiceName": "Optimize Vertex", "DictName": "optVertex", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Optimize Normals", "DictName": "optNormals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Optimize Texture Coordinates", "DictName": "optTextureCoords", "Type": "chb",
                     "asFlag": ""},
                ]
                self._createFormWidgets(maxObjExpCreateDict, exportSettings, "objExportMax", obj_export_formlayout,
                                        updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                obj_export_layout.addItem(spacerItem)

            ## MAX FBX
            ## --------
            def _max_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setProperty("seperator", True)
                fbx_seperator.setMaximumWidth(2)
                fbx_export_layout = QtWidgets.QVBoxLayout()

                fbx_horizontal_layout.addLayout(fbx_import_layout)
                fbx_horizontal_layout.addWidget(fbx_seperator)
                fbx_horizontal_layout.addLayout(fbx_export_layout)

                ## MAX FBX IMPORT WIDGETS
                fbx_import_label = QtWidgets.QLabel()
                fbx_import_label.setText("Fbx Import Settings")
                fbx_import_label.setFont(self.headerBFont)
                fbx_import_layout.addWidget(fbx_import_label)

                fbx_import_formlayout = QtWidgets.QFormLayout()
                fbx_import_formlayout.setSpacing(6)
                fbx_import_formlayout.setHorizontalSpacing(15)
                fbx_import_formlayout.setVerticalSpacing(10)
                fbx_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_import_layout.addLayout(fbx_import_formlayout)

                maxFbxImpCreateDict = [
                    {"NiceName": "Mode", "DictName": "Mode", "Type": "combo", "items": ["create", "exmerge", "merge"],
                     "asFlag": ""},
                    {"NiceName": "Skin", "DictName": "Skin", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Unit", "DictName": "ConvertUnit", "Type": "combo",
                     "items": ["mm", "cm", "dm", "m", "km", "in", "ft", "yd"], "asFlag": ""},
                    {"NiceName": "Markers", "DictName": "Markers", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Bake Animation Layers", "DictName": "BakeAnimationLayers", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Filter Key Reducer", "DictName": "FilterKeyReducer", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Fill Timeline", "DictName": "FillTimeline", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Cameras", "DictName": "Cameras", "Type": "chb", "asFlag": ""},
                    {"NiceName": "GenerateLog", "DictName": "GenerateLog", "Type": "chb", "asFlag": ""},
                    {"NiceName": "FilterKeySync", "DictName": "FilterKeySync", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Resampling: ", "DictName": "Resampling", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Lights: ", "DictName": "Lights", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape: ", "DictName": "Shape", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Axis Conversion: ", "DictName": "AxisConversion", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Bone As Dummy: ", "DictName": "ImportBoneAsDummy", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Scale Conversion: ", "DictName": "ScaleConversion", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing Groups: ", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Point Cache: ", "DictName": "PointCache", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Scale Factor: ", "DictName": "ScaleFactor", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Keep Frame Rate: ", "DictName": "KeepFrameRate", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(maxFbxImpCreateDict, importSettings, "fbxImportMax", fbx_import_formlayout,
                                        updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## MAX FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_formlayout.setSpacing(6)
                fbx_export_formlayout.setHorizontalSpacing(15)
                fbx_export_formlayout.setVerticalSpacing(10)
                fbx_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_export_layout.addLayout(fbx_export_formlayout)

                maxFbxExpCreateDict = [
                    {"NiceName": "CAT2HIK", "DictName": "CAT2HIK", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Bake Animation", "DictName": "BakeAnimation", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Tangent Space Export", "DictName": "TangentSpaceExport", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Lights", "DictName": "Lights", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Use Scene Name", "DictName": "UseSceneName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smoothing Groups", "DictName": "SmoothingGroups", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Axis Conversion Method", "DictName": "AxisConversionMethod", "Type": "combo",
                     "items": ["None", "Animation", "Fbx_Root"], "asFlag": ""},
                    {"NiceName": "Bake Frame Step", "DictName": "BakeFrameStep", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "FBX Version", "DictName": "FileVersion", "Type": "str", "asFlag": ""},
                    {"NiceName": "Remove single keys", "DictName": "Removesinglekeys", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Up Axis", "DictName": "UpAxis", "Type": "combo", "items": ["Y", "Z"], "asFlag": ""},
                    {"NiceName": "Generate Log", "DictName": "GenerateLog", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Preserve instances", "DictName": "Preserveinstances", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Selection Set Export", "DictName": "SelectionSetExport", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert to Tiff", "DictName": "Convert2Tiff", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Show Warnings", "DictName": "ShowWarnings", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Collada Triangulate", "DictName": "ColladaTriangulate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Filter Key Reducer", "DictName": "FilterKeyReducer", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Triangulate", "DictName": "Triangulate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals Per Poly", "DictName": "NormalsPerPoly", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Smooth Mesh Export", "DictName": "SmoothMeshExport", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Collada Single Matrix", "DictName": "ColladaSingleMatrix", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Convert Unit", "DictName": "ConvertUnit", "Type": "combo",
                     "items": ["mm", "cm", "dm", "m", "km", "in", "ft", "mi", "yd"], "asFlag": ""},
                    {"NiceName": "ASCII", "DictName": "ASCII", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Geometry As Bone", "DictName": "GeomAsBone", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape", "DictName": "Shape", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Embed Textures", "DictName": "EmbedTextures", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Point Cache", "DictName": "PointCache", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Skin", "DictName": "Skin", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Scale Factor", "DictName": "ScaleFactor", "Type": "spbDouble", "asFlag": ""},
                    {"NiceName": "Resample Animation Factor", "DictName": "BakeResampleAnimation", "Type": "chb",
                     "asFlag": ""},
                ]

                self._createFormWidgets(maxFbxExpCreateDict, exportSettings, "fbxExportMax", fbx_export_formlayout,
                                        updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## MAX ALEMBIC
            ## ------------
            def _max_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setProperty("seperator", True)
                alembic_seperator.setMaximumWidth(2)
                alembic_export_layout = QtWidgets.QVBoxLayout()

                alembic_horizontal_layout.addLayout(alembic_import_layout)
                alembic_horizontal_layout.addWidget(alembic_seperator)
                alembic_horizontal_layout.addLayout(alembic_export_layout)

                ## MAX ALEMBIC IMPORT WIDGETS
                alembic_import_label = QtWidgets.QLabel()
                alembic_import_label.setText("Alembic Import Settings")
                alembic_import_label.setFont(self.headerBFont)
                alembic_import_layout.addWidget(alembic_import_label)

                alembic_import_formlayout = QtWidgets.QFormLayout()
                alembic_import_formlayout.setSpacing(6)
                alembic_import_formlayout.setHorizontalSpacing(15)
                alembic_import_formlayout.setVerticalSpacing(10)
                alembic_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_import_layout.addLayout(alembic_import_formlayout)

                maxAlembicImpCreateDict = [
                    {"NiceName": "Fit Time Range", "DictName": "FitTimeRange", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Object ID", "DictName": "ObjectID", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Vertex Colors", "DictName": "VertexColors", "Type": "chb", "asFlag": ""},
                    {"NiceName": "UV's", "DictName": "UVs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Coordinate System", "DictName": "CoordinateSystem", "Type": "combo",
                     "items": ["YUp", "ZUp"], "asFlag": ""},
                    {"NiceName": "Visibility", "DictName": "Visibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Custom Attributes", "DictName": "CustomAttributes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Set Start Time", "DictName": "SetStartTime", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material ID's", "DictName": "MaterialIDs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals", "DictName": "Normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import To Root", "DictName": "ImportToRoot", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Velocity", "DictName": "Velocity", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hidden", "DictName": "Hidden", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Layer Name", "DictName": "LayerName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape Suffix", "DictName": "ShapeSuffix", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material Name", "DictName": "MaterialName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Samples Per Frame", "DictName": "SamplesPerFrame", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Extra Channels", "DictName": "ExtraChannels", "Type": "spbInt", "asFlag": ""},
                ]
                self._createFormWidgets(maxAlembicImpCreateDict, importSettings, "alembicImportMax",
                                        alembic_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## MAX ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_formlayout.setSpacing(6)
                alembic_export_formlayout.setHorizontalSpacing(15)
                alembic_export_formlayout.setVerticalSpacing(10)
                alembic_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_export_layout.addLayout(alembic_export_formlayout)

                maxAlembicExpCreateDict = [
                    {"NiceName": "Particle As Mesh", "DictName": "ParticleAsMesh", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Object ID", "DictName": "ObjectID", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Vertex Colors", "DictName": "VertexColors", "Type": "chb", "asFlag": ""},
                    {"NiceName": "UV's", "DictName": "UVs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Coordinate System", "DictName": "CoordinateSystem", "Type": "combo",
                     "items": ["YUp", "ZUp"], "asFlag": ""},
                    {"NiceName": "Visibility", "DictName": "Visibility", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Archive Type", "DictName": "ArchiveType", "Type": "combo", "items": ["Ogawa", "HDF5"],
                     "asFlag": ""},
                    {"NiceName": "Custom Attributes", "DictName": "CustomAttributes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Shape Suffix", "DictName": "ShapeSuffix", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material ID's", "DictName": "MaterialIDs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Normals", "DictName": "Normals", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Velocity", "DictName": "Velocity", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hidden", "DictName": "Hidden", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Layer Name", "DictName": "LayerName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material Name", "DictName": "MaterialName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Material Name", "DictName": "MaterialName", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Samples Per Frame", "DictName": "SamplesPerFrame", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Extra Channels", "DictName": "ExtraChannels", "Type": "spbInt", "asFlag": ""},
                ]
                self._createFormWidgets(maxAlembicExpCreateDict, exportSettings, "alembicExportMax",
                                        alembic_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            _max_obj()
            _max_fbx()
            _max_alembic()

        if sw == "houdini" or sw == "standalone":
            houdiniTab = QtWidgets.QWidget()
            houdini_verticalLayout = QtWidgets.QVBoxLayout(houdiniTab)
            houdini_verticalLayout.setSpacing(0)

            softwaresTabWidget.addTab(houdiniTab, "Houdini")

            formatsTabWidget = QtWidgets.QTabWidget(houdiniTab)
            # objTab = QtWidgets.QWidget(houdiniTab)
            fbxTab = QtWidgets.QWidget(houdiniTab)
            alembicTab = QtWidgets.QWidget(houdiniTab)
            # formatsTabWidget.addTab(objTab, "Obj")
            formatsTabWidget.addTab(fbxTab, "FBX")
            formatsTabWidget.addTab(alembicTab, "Alembic")
            houdini_verticalLayout.addWidget(formatsTabWidget)

            ## HOUDINI FBX
            ## --------
            def _houdini_fbx():
                fbx_horizontal_layout = QtWidgets.QHBoxLayout(fbxTab)
                fbx_import_layout = QtWidgets.QVBoxLayout()
                fbx_seperator = QtWidgets.QLabel()
                fbx_seperator.setProperty("seperator", True)
                fbx_seperator.setMaximumWidth(2)
                fbx_export_layout = QtWidgets.QVBoxLayout()

                fbx_horizontal_layout.addLayout(fbx_import_layout)
                fbx_horizontal_layout.addWidget(fbx_seperator)
                fbx_horizontal_layout.addLayout(fbx_export_layout)

                ## HOUDINI FBX IMPORT WIDGETS
                fbx_import_label = QtWidgets.QLabel()
                fbx_import_label.setText("Fbx Import Settings")
                fbx_import_label.setFont(self.headerBFont)
                fbx_import_layout.addWidget(fbx_import_label)

                fbx_import_formlayout = QtWidgets.QFormLayout()
                fbx_import_formlayout.setSpacing(6)
                fbx_import_formlayout.setHorizontalSpacing(15)
                fbx_import_formlayout.setVerticalSpacing(10)
                fbx_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_import_layout.addLayout(fbx_import_formlayout)

                houdiniFbxImpCreateDict = [
                    {"NiceName": "Import Lights", "DictName": "import_lights", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Resample Interval Lights", "DictName": "resample_interval", "Type": "spbDouble",
                     "asFlag": ""},
                    {"NiceName": "Import Global Ambient Light", "DictName": "import_global_ambient_light",
                     "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Geometry", "DictName": "import_geometry", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Triangulate Patches", "DictName": "triangulate_patches", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert File Paths to Relative", "DictName": "convert_file_paths_to_relative",
                     "Type": "chb", "asFlag": ""},
                    {"NiceName": "Single Precision Vertex Caches", "DictName": "single_precision_vertex_caches",
                     "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Joints and Skin", "DictName": "import_joints_and_skin", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Resample Animation", "DictName": "resample_animation", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Override Framerate", "DictName": "override_framerate", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Animation", "DictName": "import_animation", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Cameras", "DictName": "import_cameras", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Segment Scale Already Baked-in", "DictName": "segment_scale_already_baked_in",
                     "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Y Up", "DictName": "convert_into_y_up_coordinate_system", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Import Materials", "DictName": "import_materials", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Unlock Geometry", "DictName": "unlock_geometry", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import into object subnet", "DictName": "import_into_object_subnet", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Triangulate Nurbs", "DictName": "triangulate_nurbs", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Import Nulls as subnets", "DictName": "import_nulls_as_subnets", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Blend deformers as blend sops", "DictName": "import_blend_deformers_as_blend_sops",
                     "Type": "chb", "asFlag": ""},
                    {"NiceName": "Hide attached Joints", "DictName": "hide_joints_attached_to_skin", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Unlock Deformations", "DictName": "unlock_deformations", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert joints to zyx rotation order",
                     "DictName": "convert_joints_to_zyx_rotation_order", "Type": "chb", "asFlag": ""}
                ]
                self._createFormWidgets(houdiniFbxImpCreateDict, importSettings, "fbxImportHoudini",
                                        fbx_import_formlayout,
                                        updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_import_layout.addItem(spacerItem)

                ## HOUDINI FBX EXPORT WIDGETS
                fbx_export_label = QtWidgets.QLabel()
                fbx_export_label.setText("Fbx Export Settings")
                fbx_export_label.setFont(self.headerBFont)
                fbx_export_layout.addWidget(fbx_export_label)

                fbx_export_formlayout = QtWidgets.QFormLayout()
                fbx_export_formlayout.setSpacing(6)
                fbx_export_formlayout.setHorizontalSpacing(15)
                fbx_export_formlayout.setVerticalSpacing(10)
                fbx_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                fbx_export_layout.addLayout(fbx_export_formlayout)

                houdiniFbxExpCreateDict = [
                    {"NiceName": "FBX Version", "DictName": "sdkversion", "Type": "str", "asFlag": ""},
                    {"NiceName": "Export Invisible Objects as: ", "DictName": "invisobj", "Type": "combo",
                     "items": ["nullnodes", "fullnodes"], "asFlag": ""},
                    {"NiceName": "Detect Constant Point Cloud Dynamic Objects", "DictName": "detectconstpointobjs",
                     "Type": "chb", "asFlag": ""},
                    {"NiceName": "Export Deforms as Vertex Caches", "DictName": "deformsasvcs", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Vertex Cache Format", "DictName": "vcformat", "Type": "combo",
                     "items": ["mayaformat", "maxformat"], "asFlag": ""},
                    {"NiceName": "Force Skin Deform", "DictName": "forceskindeform", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Convert Surfaces", "DictName": "convertsurfaces", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Force Blend Shape Export", "DictName": "forceblendshape", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Export End Effectors", "DictName": "exportendeffectors", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Conserve memory", "DictName": "conservemem", "Type": "chb", "asFlag": ""},
                ]

                self._createFormWidgets(houdiniFbxExpCreateDict, exportSettings, "fbxExportHoudini",
                                        fbx_export_formlayout,
                                        updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                fbx_export_layout.addItem(spacerItem)

            ## HOUDINI ALEMBIC
            ## ------------
            def _houdini_alembic():
                alembic_horizontal_layout = QtWidgets.QHBoxLayout(alembicTab)
                alembic_import_layout = QtWidgets.QVBoxLayout()
                alembic_seperator = QtWidgets.QLabel()
                alembic_seperator.setProperty("seperator", True)
                alembic_seperator.setMaximumWidth(2)
                alembic_export_layout = QtWidgets.QVBoxLayout()

                alembic_horizontal_layout.addLayout(alembic_import_layout)
                alembic_horizontal_layout.addWidget(alembic_seperator)
                alembic_horizontal_layout.addLayout(alembic_export_layout)

                ## HOUDINI ALEMBIC IMPORT WIDGETS
                alembic_import_label = QtWidgets.QLabel()
                alembic_import_label.setText("Alembic Import Settings")
                alembic_import_label.setFont(self.headerBFont)
                alembic_import_layout.addWidget(alembic_import_label)

                alembic_import_formlayout = QtWidgets.QFormLayout()
                alembic_import_formlayout.setSpacing(6)
                alembic_import_formlayout.setHorizontalSpacing(15)
                alembic_import_formlayout.setVerticalSpacing(10)
                alembic_import_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_import_layout.addLayout(alembic_import_formlayout)

                houdiniAlembicImpCreateDict = [
                    {"NiceName": "Display As", "DictName": "viewportlod", "Type": "combo",
                     "items": ["full", "points", "box", "centroid", "hidden"], "asFlag": ""},
                    {"NiceName": "Flatten Visibility Evaluation", "DictName": "flattenVisibility", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Hierarchy with Channel References", "DictName": "channelRef", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Single Geometry", "DictName": "buildSingleGeoNode", "Type": "chb", "asFlag": ""},
                    {"NiceName": "User Properties", "DictName": "loadUserProps", "Type": "combo",
                     "items": ["none", "data", "both"], "asFlag": ""},
                    {"NiceName": "Load As", "DictName": "loadmode", "Type": "combo",
                     "items": ["alembic", "houdini", "hpoints", "hboxes"], "asFlag": ""},
                    {"NiceName": "Hierarchy using Subnetworks", "DictName": "buildSubnet", "Type": "chb", "asFlag": ""},
                ]
                self._createFormWidgets(houdiniAlembicImpCreateDict, importSettings, "alembicImportHoudini",
                                        alembic_import_formlayout, updateImportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_import_layout.addItem(spacerItem)

                ## HOUDINI ALEMBIC EXPORT WIDGETS
                alembic_export_label = QtWidgets.QLabel()
                alembic_export_label.setText("Alembic Export Settings")
                alembic_export_label.setFont(self.headerBFont)
                alembic_export_layout.addWidget(alembic_export_label)

                alembic_export_formlayout = QtWidgets.QFormLayout()
                alembic_export_formlayout.setSpacing(6)
                alembic_export_formlayout.setHorizontalSpacing(15)
                alembic_export_formlayout.setVerticalSpacing(10)
                alembic_export_formlayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
                alembic_export_layout.addLayout(alembic_export_formlayout)

                houdiniAlembicExpCreateDict = [
                    {"NiceName": "Create Shape Nodes", "DictName": "shape_nodes", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Format", "DictName": "format", "Type": "combo", "items": ["default", "hdf5", "ogawa"],
                     "asFlag": ""},
                    {"NiceName": "Face Sets", "DictName": "facesets", "Type": "combo",
                     "items": ["no", "nonempty", "all"], "asFlag": ""},
                    {"NiceName": "Use Instancing", "DictName": "use_instancing", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Save Attributes Instancing", "DictName": "save_attributes", "Type": "chb",
                     "asFlag": ""},
                    {"NiceName": "Motion Blur", "DictName": "motionBlur", "Type": "chb", "asFlag": ""},
                    {"NiceName": "Samples", "DictName": "samples", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Shutter Open", "DictName": "shutter1", "Type": "spbInt", "asFlag": ""},
                    {"NiceName": "Shutter Close", "DictName": "shutter2", "Type": "spbInt", "asFlag": ""},
                ]
                self._createFormWidgets(houdiniAlembicExpCreateDict, exportSettings, "alembicExportHoudini",
                                        alembic_export_formlayout, updateExportDictionary)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                   QtWidgets.QSizePolicy.Expanding)
                alembic_export_layout.addItem(spacerItem)

            # _houdini_obj()
            _houdini_fbx()
            _houdini_alembic()

        h1_s1_layout.addWidget(softwaresTabWidget)
        importExport_Layout.addLayout(h1_s1_layout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        importExport_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.importExportOptions_vis)

    def _sharedSettingsContent(self):
        sharedSettings_Layout = QtWidgets.QVBoxLayout(self.sharedSettings_vis)
        sharedSettings_Layout.setSpacing(6)

        sharedSettings_label = QtWidgets.QLabel()
        sharedSettings_label.setText("Shared Settings")
        sharedSettings_label.setFont(self.headerAFont)
        sharedSettings_label.setIndent(10)
        sharedSettings_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        sharedSettings_Layout.addWidget(sharedSettings_label)

        users_cmdButton = QtWidgets.QCommandLinkButton()
        users_cmdButton.setText("Users")
        sharedSettings_Layout.addWidget(users_cmdButton)

        passwords_cmdButton = QtWidgets.QCommandLinkButton()
        passwords_cmdButton.setText("Passwords")
        sharedSettings_Layout.addWidget(passwords_cmdButton)

        namingConventions_cmdButton = QtWidgets.QCommandLinkButton()
        namingConventions_cmdButton.setText("Naming Conventions")
        sharedSettings_Layout.addWidget(namingConventions_cmdButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sharedSettings_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.sharedSettings_vis)

        # SIGNALS
        users_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.users_item))
        passwords_cmdButton.clicked.connect(lambda: self.settingsMenu_treeWidget.setCurrentItem(self.passwords_item))
        namingConventions_cmdButton.clicked.connect(
            lambda: self.settingsMenu_treeWidget.setCurrentItem(self.namingConventions_item))

    def _usersContent(self):
        # manager = self._getManager()
        userList = self.allSettingsDict.get("users")

        users_Layout = QtWidgets.QVBoxLayout(self.users_vis)
        users_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Add/Remove Users")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        users_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)

        ################################################

        users_hLayout = QtWidgets.QHBoxLayout()
        users_hLayout.setSpacing(10)

        users_treeWidget = QtWidgets.QTreeWidget()
        users_treeWidget.setRootIsDecorated(False)

        ### THIS MAY BE CAUSING THE CRASH ###
        # header = users_treeWidget.header()
        # if FORCE_QT5:
        #     header.setResizeMode(QtWidgets.QHeaderView.Stretch)
        # else:
        #     header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ### THIS MAY BE CAUSING THE CRASH ### -end

        users_treeWidget.setSortingEnabled(True)
        headerItem = QtWidgets.QTreeWidgetItem(["Full Name", "Initials"])

        users_treeWidget.setHeaderItem(headerItem)
        users_treeWidget.sortItems(1, QtCore.Qt.AscendingOrder)  # 1 is Date Column, 0 is Ascending order
        users_hLayout.addWidget(users_treeWidget)

        users_treeWidget.setColumnWidth(1000, 10)

        users_vLayout = QtWidgets.QVBoxLayout()
        users_vLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        add_pushButton = QtWidgets.QPushButton()
        add_pushButton.setText(("Add..."))
        users_vLayout.addWidget(add_pushButton)

        remove_pushButton = QtWidgets.QPushButton()
        remove_pushButton.setText(("Remove"))
        users_vLayout.addWidget(remove_pushButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        users_vLayout.addItem(spacerItem)

        users_hLayout.addLayout(users_vLayout)

        ################################################

        h1_s1_layout.addLayout(users_hLayout)
        users_Layout.addLayout(h1_s1_layout)

        def updateUsers():
            users_treeWidget.clear()
            for item in userList.items():
                name = item[0]
                initial = item[1]
                QtWidgets.QTreeWidgetItem(users_treeWidget, [name, initial])

        def addNewUserUI():
            addUser_Dialog = QtWidgets.QDialog(parent=self)
            addUser_Dialog.resize(260, 114)
            addUser_Dialog.setMaximumSize(QtCore.QSize(16777215, 150))
            addUser_Dialog.setFocusPolicy(QtCore.Qt.ClickFocus)
            addUser_Dialog.setWindowTitle(("Add New User"))

            verticalLayout = QtWidgets.QVBoxLayout(addUser_Dialog)

            addNewUser_label = QtWidgets.QLabel(addUser_Dialog)
            addNewUser_label.setText("Add New User:")
            verticalLayout.addWidget(addNewUser_label)

            formLayout = QtWidgets.QFormLayout()
            formLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
            formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
            formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
            formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            formLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

            fullname_label = QtWidgets.QLabel(addUser_Dialog)
            fullname_label.setFocusPolicy(QtCore.Qt.StrongFocus)
            fullname_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            fullname_label.setText("Full Name:")
            formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, fullname_label)

            fullname_lineEdit = QtWidgets.QLineEdit(addUser_Dialog)
            fullname_lineEdit.setPlaceholderText("e.g \'Jon Snow\'")
            formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, fullname_lineEdit)

            initials_label = QtWidgets.QLabel(addUser_Dialog)
            initials_label.setText("Initials:")
            formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, initials_label)

            initials_lineEdit = QtWidgets.QLineEdit(addUser_Dialog)
            initials_lineEdit.setPlaceholderText("e.g \'js\' (must be unique)")
            formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, initials_lineEdit)
            verticalLayout.addLayout(formLayout)

            buttonBox = QtWidgets.QDialogButtonBox(addUser_Dialog)
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
            verticalLayout.addWidget(buttonBox)
            addUser_Dialog.show()

            buttonBox.setMaximumSize(QtCore.QSize(16777215, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setMinimumSize(QtCore.QSize(100, 30))
            buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setMinimumSize(QtCore.QSize(100, 30))

            def onAddUser():
                userList[str(fullname_lineEdit.text())] = str(initials_lineEdit.text())
                updateUsers()
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
                addUser_Dialog.close()

            buttonBox.accepted.connect(onAddUser)
            buttonBox.rejected.connect(addUser_Dialog.reject)

        def onRemoveUser():
            getSelected = users_treeWidget.selectedItems()
            if not getSelected:
                return
            for item in getSelected:
                # del userList[unicode(item.text(0)).decode("utf-8")]
                del userList[compat.decode(item.text(0))]
            updateUsers()
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        updateUsers()

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        users_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.users_vis)

        ## SIGNALS

        add_pushButton.clicked.connect(addNewUserUI)
        remove_pushButton.clicked.connect(onRemoveUser)

    def _passwordsContent(self):

        passwords_Layout = QtWidgets.QVBoxLayout(self.passwords_vis)
        passwords_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Change Admin Password")
        h1_label.setFont(self.headerAFont)
        h1_horizontalLayout.addWidget(h1_label)
        passwords_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_layout.setSpacing(8)

        ################################################

        formLayout = QtWidgets.QFormLayout()
        formLayout.setSpacing(6)
        formLayout.setHorizontalSpacing(15)
        formLayout.setVerticalSpacing(10)
        formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldsStayAtSizeHint)
        formLayout.setSpacing(8)
        oldPass_label = QtWidgets.QLabel()
        oldPass_label.setText("Old Password: ")
        oldPass_lineEdit = QtWidgets.QLineEdit()
        oldPass_lineEdit.setMinimumWidth(200)
        oldPass_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(oldPass_label, oldPass_lineEdit)

        newPass_label = QtWidgets.QLabel()
        newPass_label.setText("New Password: ")
        newPass_lineEdit = QtWidgets.QLineEdit()
        newPass_lineEdit.setMinimumWidth(200)
        newPass_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(newPass_label, newPass_lineEdit)

        newPassAgain_label = QtWidgets.QLabel()
        newPassAgain_label.setText("New Password Again: ")
        newPassAgain_lineEdit = QtWidgets.QLineEdit()
        newPassAgain_lineEdit.setMinimumWidth(200)
        newPassAgain_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(newPassAgain_label, newPassAgain_lineEdit)

        changePass_btn = QtWidgets.QPushButton()
        changePass_btn.setText("Change Password")
        changePass_btn.setMinimumWidth(200)
        changePass_btn.setMaximumWidth(200)
        formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, changePass_btn)

        ################################################

        h1_s1_layout.addLayout(formLayout)

        passwords_Layout.addLayout(h1_s1_layout)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        passwords_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.passwords_vis)

        def changePass():

            if not self.manager.checkPassword(oldPass_lineEdit.text()):
                self.infoPop(textTitle="Incorrect Password", textHeader="Invalid Old Password", type="C")
            if newPass_lineEdit.text() == "" or newPassAgain_lineEdit.text() == "":
                self.infoPop(textTitle="Error", textHeader="Admin Password cannot be blank", type="C")
            if newPass_lineEdit.text() != newPassAgain_lineEdit.text():
                self.infoPop(textTitle="Error", textHeader="New passwords are not matching", type="C")
            if self.manager.changePassword(oldPass_lineEdit.text(), newPass_lineEdit.text()):
                self.infoPop(textTitle="Success", textHeader="Success!\nPassword Changed", type="I")
            oldPass_lineEdit.setText("")
            newPass_lineEdit.setText("")
            newPassAgain_lineEdit.setText("")
            return

        ## SIGNALS
        changePass_btn.clicked.connect(changePass)

    def _namingConventions(self):
        # manager = self._getManager()
        settings = self.allSettingsDict.get("nameConventions")

        validFileNameTokens = ["<date>", "<subproject>", "<baseName>", "<categoryName>", "<userInitials>"]
        validProjectNameTokens = ["<brandName>", "<projectName>", "<clientName>", "<yy>", "<mm>", "<dd>"]

        namingConv_Layout = QtWidgets.QVBoxLayout(self.namingConventions_vis)
        namingConv_Layout.setSpacing(0)

        h1_horizontalLayout = QtWidgets.QHBoxLayout()
        h1_label = QtWidgets.QLabel()
        h1_label.setText("Naming Conventions")
        h1_label.setFont(self.headerAFont)
        h1_label.setFocusPolicy(QtCore.Qt.StrongFocus)
        h1_horizontalLayout.addWidget(h1_label)
        namingConv_Layout.addLayout(h1_horizontalLayout)

        h1_s1_layout = QtWidgets.QVBoxLayout()
        h1_s1_layout.setContentsMargins(-1, 15, -1, -1)
        h1_s1_layout.setSpacing(8)
        # h1_s1_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        ################################################
        formLayout = QtWidgets.QFormLayout()
        formLayout.setSpacing(8)

        fileNameConv_lbl = QtWidgets.QLabel()
        fileNameConv_lbl.setText("Scene Name Convention: ")
        fileNameConv_le = QtWidgets.QLineEdit()
        fileNameConv_le.setText(settings["fileName"])

        formLayout.addRow(fileNameConv_lbl, fileNameConv_le)

        infoLabel = QtWidgets.QLabel()
        infoLabel.setText("Valid Scene Name tokens: %s\n" % (", ".join(validFileNameTokens)))
        infoLabel.setWordWrap(True)
        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, infoLabel)

        newProjectNameConv_lbl = QtWidgets.QLabel()
        newProjectNameConv_lbl.setText("Project Name Convention: ")
        newProjectNameConv_le = QtWidgets.QLineEdit()
        newProjectNameConv_le.setText(settings["newProjectName"])

        formLayout.addRow(newProjectNameConv_lbl, newProjectNameConv_le)

        infoLabel_newProjectConv = QtWidgets.QLabel()
        infoLabel_newProjectConv.setText("Valid Project Name tokens: %s\n" % (", ".join(validProjectNameTokens)))
        infoLabel_newProjectConv.setWordWrap(True)
        formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, infoLabel_newProjectConv)

        templateFolder_lbl = QtWidgets.QLabel()
        templateFolder_lbl.setText("Template Folder: ")
        templateFolder_hLayout = QtWidgets.QHBoxLayout()
        templateFolder_le = QtWidgets.QLineEdit()
        templateFolder_le.setPlaceholderText("Define Template Folder")
        templateFolder_le.setText(settings["templateFolder"])
        templateFolderBrowse_pb = QtWidgets.QPushButton()
        templateFolderBrowse_pb.setText("...")
        templateFolder_hLayout.addWidget(templateFolder_le)
        templateFolder_hLayout.addWidget(templateFolderBrowse_pb)
        formLayout.addRow(templateFolder_lbl, templateFolder_hLayout)
        infoLabel = QtWidgets.QLabel()
        infoLabel.setText(
            "While creating a new project, all contents of the template folder will be copied into the project folder")
        infoLabel.setWordWrap(True)
        formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, infoLabel)

        h1_s1_layout.addLayout(formLayout)

        namingConv_Layout.addLayout(h1_s1_layout)

        def browseTemplateFolder():
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.Directory)

            if dlg.exec_():
                selectedroot = os.path.normpath(compat.encode(dlg.selectedFiles()[0]))
                folderSize_inMB = get_size(selectedroot) / (1024 * 1024)
                if folderSize_inMB > settings["warningSizeLimit"]:
                    msg = "Selected Folder size is %s\n\nFrom now on this data will be copied EACH new project created with Tik Manager.\n\n Do you want to continue?" % folderSize_inMB
                    q = self.queryPop(type="yesNo", textTitle="Large Folder Size", textHeader=msg)
                    if q == "no":
                        return

                settings["templateFolder"] = selectedroot
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())
                templateFolder_le.setText(selectedroot)
            return

        def updateTemplateFolder():
            folder = compat.encode(templateFolder_le.text())
            if not os.path.isdir(folder) and folder != "":
                msg = "Entered path is invalid. Resetting to default"
                self.infoPop(textTitle="Invalid Path", textHeader=msg)
                templateFolder_le.setText(settings["templateFolder"])
            else:
                settings["templateFolder"] = folder
                self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def updateFileName():
            template = compat.encode(fileNameConv_le.text())
            items = re.findall(r'<(.*?)\>', template)
            for x in items:
                if ("<%s>" % x) not in validFileNameTokens:
                    msg = "%s token is invalid\nValid tokens are: %s" % (x, ",".join(validFileNameTokens))
                    self.infoPop(textTitle="Invalid Token", textHeader=msg)
                    fileNameConv_le.setText(settings["fileName"])
                    return
            settings["fileName"] = template
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())

        def updateProjectName():
            template = compat.encode(newProjectNameConv_le.text())
            items = re.findall(r'<(.*?)\>', template)
            for x in items:
                if ("<%s>" % x) not in validProjectNameTokens:
                    msg = "%s token is invalid\nValid tokens are: %s" % (x, ",".join(validProjectNameTokens))
                    self.infoPop(textTitle="Invalid Token", textHeader=msg)
                    newProjectNameConv_le.setText(settings["newProjectName"])
                    return
            settings["newProjectName"] = template
            self.settingsApply_btn.setEnabled(self.allSettingsDict.isChanged())


        def get_size(start_path='.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        namingConv_Layout.addItem(spacerItem)
        self.contentsMaster_layout.addWidget(self.namingConventions_vis)

        ## SIGNALS
        templateFolderBrowse_pb.clicked.connect(browseTemplateFolder)
        templateFolder_le.textChanged.connect(updateTemplateFolder)
        fileNameConv_le.textChanged.connect(updateFileName)
        newProjectNameConv_le.textChanged.connect(updateProjectName)

    def _createFormWidgets(self, loopList, settingsDict, formattingType, formlayout, dictUpdateMethod):
        """Creates widgets for the given form layout"""
        convertDict = {"true": True,
                       "True": True,
                       "false": False,
                       "False": False,
                       "0": False,
                       "1": True}

        if formattingType == "objImportMax" or \
                formattingType == "objExportMax" or \
                formattingType == "objImportMaya" or \
                formattingType == "objExportMaya" or \
                formattingType == "fbxImportMaya" or \
                formattingType == "fbxExportMaya":
            databaseType = "String"
        else:
            databaseType = "Direct"

        for widget in loopList:
            ## if the setting item is missing, skip its widget
            try:
                settingsDict[formattingType][widget["DictName"]]
            except KeyError:
                if widget["Type"] == "inf":
                    pass
                else:
                    continue

            if widget["Type"] == "inf":
                infoLabel = QtWidgets.QLabel()
                infoLabel.setText(widget["NiceName"])
                infoLabel.setFont(self.headerBFont)
                formlayout.addRow(infoLabel)
            elif widget["Type"] == "chb":
                chb = QtWidgets.QCheckBox()
                chb.setText(widget["NiceName"])
                chb.setObjectName(widget["DictName"])
                formlayout.addRow(chb)
                if databaseType == "String":
                    chb.setChecked(
                        convertDict[settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], "")])
                    if formattingType == "fbxImportMaya" or formattingType == "fbxExportMaya":
                        chb.stateChanged.connect(
                            lambda state, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(
                                formattingType, dict, "%s%s" % (flag, str(bool(state)).lower()))
                        )
                    else:
                        chb.stateChanged.connect(
                            lambda state, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(
                                formattingType, dict, "%s%s" % (flag, int(bool(state))))
                        )
                else:
                    chb.setChecked(settingsDict[formattingType][widget["DictName"]])
                    chb.stateChanged.connect(
                        lambda state, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict,
                                                                                bool(int((state))))
                    )

            elif widget["Type"] == "combo":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                combo = QtWidgets.QComboBox()
                combo.setFocusPolicy(QtCore.Qt.NoFocus)
                combo.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, combo)
                combo.addItems(widget["items"])
                if databaseType == "String":

                    if formattingType == "fbxImportMaya" or formattingType == "fbxExportMaya":
                        ffindex = combo.findText(
                            settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], ""),
                            QtCore.Qt.MatchFixedString)
                        combo.setCurrentIndex(ffindex)
                        combo.currentIndexChanged[str].connect(
                            lambda arg, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType,
                                                                                                         dict,
                                                                                                         "%s%s" % (
                                                                                                             flag, arg))
                        )
                    else:
                        combo.setCurrentIndex(
                            int(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], "")))
                        combo.currentIndexChanged.connect(
                            # lambda index, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, unicode(index).encode("utf-8"))
                            lambda index, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, compat.encode(index))
                        )
                else:
                    ffindex = combo.findText(settingsDict[formattingType][widget["DictName"]],
                                             QtCore.Qt.MatchFixedString)
                    combo.setCurrentIndex(ffindex)
                    combo.currentIndexChanged[str].connect(
                        # lambda text, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, unicode(text).encode("utf-8"))
                        lambda text, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, compat.encode(text))
                    )

            elif widget["Type"] == "spbDouble":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                spb = QtWidgets.QDoubleSpinBox()
                spb.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
                spb.setFocusPolicy(QtCore.Qt.NoFocus)
                spb.setMinimumWidth(60)
                spb.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, spb)
                if databaseType == "String":
                    spb.setValue(float(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], "")))
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType,
                                                                                                       dict,
                                                                                                       "%s%s" % (
                                                                                                           flag, value))
                    )
                else:
                    spb.setValue(settingsDict[formattingType][widget["DictName"]])
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, value)
                    )

            elif widget["Type"] == "spbInt":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                spb = QtWidgets.QSpinBox(maximum=9999999)
                spb.setMinimumSize(self.minSPBSize[0], self.minSPBSize[1])
                spb.setFocusPolicy(QtCore.Qt.NoFocus)
                spb.setMinimumWidth(60)
                spb.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, spb)
                if databaseType == "String":
                    spb.setValue(int(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], "")))
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType,
                                                                                                       dict, "%s%s" % (
                                                                                                           flag, value))
                    )
                else:
                    spb.setValue(settingsDict[formattingType][widget["DictName"]])
                    spb.valueChanged.connect(
                        lambda value, dict=widget["DictName"]: dictUpdateMethod(formattingType, dict, value)
                    )

            elif widget["Type"] == "str":
                lbl = QtWidgets.QLabel()
                lbl.setText(widget["NiceName"])
                le = QtWidgets.QLineEdit()
                le.setObjectName(widget["DictName"])
                formlayout.addRow(lbl, le)
                le.setText(settingsDict[formattingType][widget["DictName"]].replace(widget["asFlag"], ""))
                le.textEdited.connect(
                    lambda text, dict=widget["DictName"], flag=widget["asFlag"]: dictUpdateMethod(formattingType, dict,
                                                                                                  "%s%s" % (flag, text))
                )

class Settings(dict):
    def __init__(self):
        super(Settings, self).__init__()

    def isChanged(self):
        """Checks for differences between old and new settings"""
        for key in self.listNames():
            if self[key]["newSettings"] != self[key]["oldSettings"]:
                return True
        return False

    def apply(self):
        """Equals original settings to the new settings"""
        applyList = []
        for key in self.listNames():
            newSettings = self[key]["newSettings"]
            oldSettings = self[key]["oldSettings"]
            if newSettings != oldSettings:
                self[key]["oldSettings"] = deepcopy(newSettings)
                applyInfo = {"data": newSettings,
                             "filepath": self[key]["databaseFilePath"]}
                applyList.append(applyInfo)
        return applyList

    def add(self, name, data, filePath):
        """Adds a new setting database"""
        # self[name] = {"oldSettings": type(data)(data),
        #               "newSettings": type(data)(data),
        #               "databaseFilePath": filePath}
        self[name] = {"oldSettings": deepcopy(data),
                      "newSettings": deepcopy(data),
                      "databaseFilePath": filePath}
        return True

    def listNames(self):
        """Returns all setting names"""
        return list(self)

    def getOriginal(self, settingName):
        return self[settingName]["oldSettings"]

    def setOriginal(self, settingName, data):
        self[settingName]["oldSettings"] = deepcopy(data)

    def get(self, settingName):
        return self[settingName]["newSettings"]

    def set(self, settingName, data):
        self[settingName]["newSettings"] = deepcopy(data)