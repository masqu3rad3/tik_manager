macroScript manager
category: "SceneManager"
tooltip: "Scene Manager"
ButtonText: "SM"
icon: #("SceneManager",1)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().show()"
)

macroScript saveVersion
category: "SceneManager"
tooltip: "Scene Manager - Save Version"
ButtonText: "SM_SaveV"
icon: #("SceneManager",2)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "Sm3dsMax.MainUI().saveAsVersionDialog()"
)

macroScript imageViewer
category: "SceneManager"
tooltip: "Scene Manager - Image Viewer"
ButtonText: "ImageViewer"
icon: #("SceneManager",4)
(
    python.Execute "from tik_manager import Sm3dsMax"
    python.Execute "tik_imageViewer = Sm3dsMax.MainUI()"
    python.Execute "tik_imageViewer.onIviewer()"
)

macroScript makePreview
category: "SceneManager"
tooltip: "Scene Manager - Make Preview"
ButtonText: "Make Preview"
icon: #("SceneManager",5)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "reload(Sm3dsMax)"
	python.Execute "Sm3dsMax.MaxManager().createPreview()"
)

macroScript projectMaterials
category: "SceneManager"
tooltip: "Scene Manager - Project Materials"
ButtonText: "Project Materials"
icon: #("SceneManager",6)
(
	python.Execute "from tik_manager import Sm3dsMax"
	python.Execute "tik_projectMaterials = Sm3dsMax.MainUI()"
	python.Execute "tik_projectMaterials.onPMaterials()"
)