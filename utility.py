# for auto compilation and clean-up purposes
import sys, os
import py_compile
from shutil import copyfile, rmtree
import subprocess

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
            [os.path.join(standalone_folder, "SmStandalone.exe.manifest"), self.bin_folder]
        ]
        map(lambda x: self._copyfile(x[0], x[1]), copyList)


    def forceCompile(self):
        """compiles every .py file under tik_manager folder"""
        # get py files
        pyFiles = [f for f in os.listdir(self.root_folder) if os.path.splitext(f)[1] == ".py"]
        map(lambda x: py_compile.compile(os.path.join(self.root_folder, x)), pyFiles)

    def innoSetupCompile(self):
        """
        compiles project into the setup file using Inno Setup
        Inno Setup must be installed for this to work
        """
        compiler = os.path.normpath("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe")
        innoSetupScript = os.path.join(self.root_folder, "innoSetup", "tikManager_aSetup.iss")

        ## Preparations
        print("Starting Force Compilation...")
        self.forceCompile()
        print("Force compilation DONE...")
        print("Starting freezeSetup...")
        self.freezeSetup()
        print("freezeSetup DONE...")
        print("Starting freezePhotoshop...")
        self.freezePhotoshop()
        print("freezePhotoshop DONE...")
        print("Starting freezeStandalone...")
        self.freezeStandalone()
        print("freezeStandalone DONE...")

        # TODO // INNO SETUP Commandline
        print("Compiling... Please wait")
        res = subprocess.check_output([compiler, innoSetupScript], cwd=self.root_folder, shell=False)
        if res == 0:
            raw_input("inno setup compilation completed...")
        pass

    def _copyfile(self, src, dst):
        targetPath = os.path.join(dst, os.path.basename(src))
        copyfile(src, targetPath)

def main(argv):
    z=TMUtility().innoSetupCompile()
    # subprocess.Popen(["python.exe"], shell=True)
    # subprocess.call("python", shell=True)
    # os.system("python.exe")
    print "eesof"
    pass

if __name__ == "__main__":
    main(sys.argv[1:])

