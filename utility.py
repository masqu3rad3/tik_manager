# for auto compilation and clean-up purposes
import sys, os
import py_compile
from shutil import copyfile, rmtree
import subprocess
import tik_manager._version as versionInfo
import tarfile


class TMUtility(object):
    def __init__(self):
        super(TMUtility, self).__init__()
        self.location =  os.path.dirname(os.path.abspath(__file__))
        self.root_folder = os.path.join(self.location, "tik_manager")
        self.bin_folder= os.path.join(self.root_folder, "bin")




        # self.upx_folder = os.path.join(self.location, "upx")



    def cliMenu(self):
        menuItems = [
            {"Freeze Photoshop": self.freezePhotoshop},
            {"Freeze Standalone": self.freezeStandalone},
            {"Inno Setup Compile": self.innoSetupCompile},
            {"Exit": sys.exit}
        ]

    def freezeSetup(self):
        freezeSetup = os.path.join(self.root_folder, "freezeSetup.bat")

        # remove setup.exe if already exists
        try: os.remove(os.path.join(self.root_folder, "dist", "setup.exe"))
        except: pass

        res = subprocess.check_output(freezeSetup, cwd=self.root_folder, shell=True)
        # os.system(freezeSetup)


        copyList = [
            [os.path.join(self.root_folder, "dist", "setup.exe"), os.path.join(self.root_folder)]
        ]
        map(lambda x: self._copyfile(x[0], x[1]), copyList)

    def freezePhotoshop(self):
        freezePs = os.path.join(self.root_folder, "freezePs.bat")
        ps_folder = os.path.join(self.root_folder, "dist", "SmPhotoshop")

        # remove dir
        try: rmtree(ps_folder)
        except: pass

        res = subprocess.check_output(freezePs, cwd=self.root_folder, shell=True)
        print "PS Res",res
        copyList = [
            [os.path.join(ps_folder, "SmPhotoshop.exe"), self.bin_folder],
            [os.path.join(ps_folder, "SmPhotoshop.exe.manifest"), self.bin_folder]
        ]
        map(lambda x: self._copyfile(x[0], x[1]), copyList)

    def freezeStandalone(self):
        freezeStandalone = os.path.join(self.root_folder, "freezeStandalone.bat")
        standalone_folder = os.path.join(self.root_folder, "dist", "SmStandalone")
        # iconPath = os.path.join(self.root_folder, "icons", "osicon_scenemanager_EM0_icon.ico")

        # remove dir
        try: rmtree(standalone_folder)
        except: pass


        res = subprocess.check_output(freezeStandalone, cwd=self.root_folder, shell=True)
        print "ST Res",res
        copyList = [
            [os.path.join(standalone_folder, "SmStandalone.exe"), self.bin_folder],
            [os.path.join(standalone_folder, "SmStandalone.exe.manifest"), self.bin_folder],
            [os.path.join(self.root_folder, "CSS", "tikManager.qss"), os.path.join(self.bin_folder, "CSS")]
        ]
        map(lambda x: self._copyfile(x[0], x[1]), copyList)


    def forceCompile(self):
        """compiles every .py file under tik_manager folder"""
        # get py files
        pyFiles = [f for f in os.listdir(self.root_folder) if os.path.splitext(f)[1] == ".py"]
        map(lambda x: py_compile.compile(os.path.join(self.root_folder, x)), pyFiles)

    def _updateInnoSetupFile(self):
        filePath = os.path.join(self.root_folder, "innoSetup", "tikManager_aSetup.iss")


        #loadContents
        f = open(filePath, "r")
        if f.mode == "r":
            innoSetupContents = f.readlines()
        else:
            raise Exception("Inno Setup File is not readable")
        f.close()
        # print innoSetupContents

        for lineNumber in range(len(innoSetupContents)):
            if "#define appVersion" in innoSetupContents[lineNumber]:
                innoSetupContents[lineNumber] = '#define appVersion "%s"\n' %versionInfo.__version__

        backupFile = "tikManager_aSetup.bak".format(filePath)
        copyfile(filePath, backupFile)
        tempFile = "tikManager_aSetup_TMP.iss"
        f = open(tempFile, "w+")
        f.writelines(innoSetupContents)
        f.close()
        copyfile(tempFile, filePath)
        os.remove(tempFile)

    def innoSetupCompile(self):
        """
        compiles project into the setup file using Inno Setup
        Inno Setup must be installed for this to work
        """
        compiler = os.path.normpath("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe")
        innoSetupScript = os.path.join(self.root_folder, "innoSetup", "tikManager_aSetup.iss")

        print("Tik Manager v%s Auto Setup Creation Utility\n" %versionInfo.__version__)
        ## Preparations
        print("Starting Force Compilation...")
        self.forceCompile()
        print("Force compilation DONE...\n")
        print("Starting freezeSetup...")
        self.freezeSetup()
        print("freezeSetup DONE...\n")
        print("Starting freezePhotoshop...")
        self.freezePhotoshop()
        print("freezePhotoshop DONE...\n")
        print("Starting freezeStandalone...")
        self.freezeStandalone()
        print("freezeStandalone DONE...\n")

        print("Editing Inno Setup File with current version")
        self._updateInnoSetupFile()
        print("Editing DONE...\n")


        # TODO // INNO SETUP Commandline
        print("Compiling... Please wait")
        res = subprocess.check_output([compiler, innoSetupScript], cwd=self.root_folder, shell=False)
        if res == 0:
            raw_input("inno setup compilation completed...")
        pass

    def _copyfile(self, src, dst):
        targetPath = os.path.join(dst, os.path.basename(src))
        copyfile(src, targetPath)

    def prepareLinuxTar(self):

        print ("Preparing Linux Tarball...")

        # def tardir(build, path):
        #     for root, dirs, files in os.walk(path):
        #         for file in files:
        #             build.add(os.path.join(root, file))

        tarFileLocation = os.path.join(self.location, "tikManager_%s_linux.tar.gz" %versionInfo.__version__)
        build = tarfile.open(tarFileLocation, mode='w')

        # addList = [
        #     "coreFunctions\\__init__.pyc",
        #     "coreFunctions\\coreFunctions_Houdini.pyc",
        #     "coreFunctions\\coreFunctions_Maya.pyc",
        #     "coreFunctions\\coreFunctions_Nuke.pyc",
        #     "CSS\\tikManager.qss"
        #     "icons",
        #     "setupFiles",
        #     "__init__.pyc",
        #     "_version.pyc",
        #     "assetEditorHoudini.pyc",
        #     "assetEditorMaya.pyc",
        #     "assetLibrary.pyc",
        #     "iconsSource.pyc",
        #     "ImageViewer.pyc",
        #     "ImMaya.pyc",
        #     "projectMaterials.pyc",
        #     "pyseq.pyc",
        #     "Qt.pyc",
        #     "SmHoudini.pyc",
        #     "SmMaya.pyc",
        #     "SmNuke.pyc",
        #     "SmRoot.pyc",
        #     "SmStandalone.pyc",
        #     "SmUIRoot.pyc"
        # ]

        addList = [
            "coreFunctions\\__init__.py",
            "coreFunctions\\coreFunctions_Houdini.py",
            "coreFunctions\\coreFunctions_Maya.py",
            "coreFunctions\\coreFunctions_Nuke.py",
            "CSS\\tikManager.qss",
            "icons",
            "setupFiles",
            "__init__.py",
            "_version.py",
            "assetEditorHoudini.py",
            "assetEditorMaya.py",
            "assetLibrary.py",
            "iconsSource.py",
            "ImageViewer.py",
            "ImMaya.py",
            "projectMaterials.py",
            "pyseq.py",
            "Qt.py",
            "SmHoudini.py",
            "SmMaya.py",
            "SmNuke.py",
            "SmRoot.py",
            "SmStandalone.py",
            "SmUIRoot.py"
        ]

        for item in addList:

            # build.add(os.path.join(self.root_folder, item))
            build.add(os.path.join(self.root_folder, item), arcname=item)

        build.close()

        print ("Tarball is ready")


def main(argv):
    utility = TMUtility()
    utility.innoSetupCompile()
    utility.prepareLinuxTar()

if __name__ == "__main__":
    main(sys.argv[1:])

