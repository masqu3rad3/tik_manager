macroScript TIK_sm3dsMax
category: "Tik Works"
tooltip: "Scene Manager"
ButtonText: "SM"
icon: #("SceneManager",1)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().show()"
)


macroScript TIK_smSaveVersion
category: "Tik Works"
tooltip: "Scene Manager - Save Version"
ButtonText: "SM_SaveV"
icon: #("SceneManager",2)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().saveAsVersionDialog()"
)


macroScript TIK_smPreview
category: "Tik Works"
tooltip: "Scene Manager - Make Preview"
ButtonText: "SM_MakeP"
icon: #("SceneManager",5)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MaxManager().createPreview()"
)


# /*
# macroScript TIK_sceneManager
# category: "Tik Works"
# tooltip: "Scene Manager"
# ButtonText: "Scene Manager"
# */
#
# (
# 	python.Execute "from tik_manager import Sm3dsMax as man"
# 	python.Execute "reload(man)"
# 	python.Execute "r=man.MainUI().show()"
# )