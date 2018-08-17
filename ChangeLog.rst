=============================
Scene Manager Version History
=============================

1.92
-----
* **New.0:** add/remove user functions added
* **Update.0:** IMPORTANT user preferences (smSettings.json) structure changed. Delete old preference data under user/Documents
* **Update.0:** method for getting necessary scene paths has re-written
* **Update.0:** Documentation and Docstring updates
* **Update.0:** Various code clean-ups
* **Update.0:** Added .tif extension to the imageViewer
* **Fix.0** Sub-menu item connections fixed
* **Fix.0** imageViewer refreshing issues fixed
* **Fix.1** Thumbnails are now stored as relative paths in the json db
* **Update.2** ImageViewer root search added
* **Fix.2** When browsing for raid, updating the paths fixed.
* **Update.2** sequence transfer commands moved to seqCopyProgress module.
* **Fix.3** 'Current user resetting to the first one' issue fixed.

1.91
----
* **New:** added scriptJob to the manager class for project change
* **Update:** refresh method added

1.9
----
* **New:** imageManager and connections added
* **New:** ImageViewer added
* **Update:** scriptJobs added for imageManager connection.

1.82
----
* **Update:** various code and UI optimizations

1.8
----
* **Update:** color code yellow added for the scenes if the referenced version is not the last version
* **Fix:** playblast bug fixes
* **Update:** minor code optimizations

1.7
----
* **New:** added thumbnails

1.65
----
* **Fix:** Linux compatibility issues fixed

1.63
----
* **Update:** UI improvements

1.62
----
* **Fix:** when switching projects, subproject index will be reset to 0 now

1.61
----
* **Fix:** create new project bugfix (workspace.mel creation)

1.6
----
* **New:** added "add note" function
* **Fix:** minor code improvements with the playblast, and note checking methods

1.58
----
* **Fix:** minor bug fixes with createPlayblast method

1.57
----
* **Update:** Kill Turtle method updated
* **Update:** Version Number added to the scene dialog

1.56
----
* **Update:** After loading new scene menu refreshes

1.55
----
* **New:** regularSaveUpdate function added for Save callback
* **Fix:** sound problem fixed with playblasts

1.45
----
* **New:** Create New Project Function added, Settings menu renamed as File

1.44
----
* **Fix:** Bug fix with playblasts Maya 2017 (hud display camera location was inproper)

1.43
----
* **New:** current scene info line added to the top of the window

1.42
----
* **New:** sceneInfo right click menu added for base scenes

1.41
----
* **Update:** namespace added while referencing a scene

1.4
----
* **New:** added wire on shaded and default material settings to the playblast settings file

1.3
----
* **Update:** suMod removed. Everything is in a single file. For password protection share only the compiled version.
* **Fix:** various bug fixes

1.2
----
* **Fix:** loading and referencing system fixed. Now it checks for the selected rows 'name' not the list number id.
* **Update:** the name check for duplicate base scenes. It doesnt allow creating base scenes with the same name disregarding it
has lower case or upper case characters.

1.1
----
* **New:** "Frame Range" Hud option is added to playblast settings.
* **Update:** In "Reference Mode" Scene List highlighted with red border for visual reference.

1.0
----
* initial