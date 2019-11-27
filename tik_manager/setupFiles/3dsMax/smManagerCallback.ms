
python.Execute "import sys"
python.Execute "import os"
python.Execute "import MaxPlus"
python.Execute "sys.path.append(os.path.normpath('PATH//TO//ROOT//OF//tik_manager'))"
python.Execute "def smUpdate(*args):\n    try:\n        from tik_manager import Sm3dsMax\n        m = Sm3dsMax.MaxManager()\n        m.saveCallback()\n    except:\n        pass"
python.Execute "MaxPlus.NotificationManager.Register(14, smUpdate)"
