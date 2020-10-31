from tik_manager.core import asset_library

reload(asset_library)
pathList = ["E:\\backup\\_CharactersLibrary", "E:\\backup\\_BalikKrakerAssetLibrary", "E:\\backup\\_AssetLibrary", "M:\\Projects\\_CharactersLibrary", "M:\\Projects\\_BalikKrakerAssetLibrary", "M:\\Projects\\_AssetLibrary"]

for path in pathList:
    lib = asset_library.AssetLibrary(path)
    lib.scanAssets()
    for item in lib.assetsList:
        data = lib._getData(item)
        # data["sourceProject"] = "Maya(ma)"
        # data["notes"] = "N/A"
        # data["version"] = "N/A"
        # if data["Faces/Triangles"] == "Nothing counted : no polygonal object is selected./Nothing counted : no polygonal object is selected.":
        #     data["Faces/Triangles"] = "N/A"
        data["notes"]=""
        # data["Faces/Triangles"] = data["Faces/Trianges"]
        lib._setData(item, data)
