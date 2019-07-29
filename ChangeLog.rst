=============================
Tik Manager Version History
=============================

3.0
---
* **New.0** Photoshop module added
* **Update.0** Software icons added to each software
* **Update.0** Common database folder seperated from core files
* **Fix.0** Fixed Error in asset library Maya preventing the merge option.
* **New.0** One single executable installer (Windows)
* **New.0** Completely new settings menu
* **Update.0** Redesigned and improved Asset Library including 3ds Max and Houdini support
* **New.0** Transfer Central
* **Update.0** Image Viewer improvements
* **New.0** MP4 conversion support
* **Update.0** UI improvements
* **Fix.23** Fixed wrong header image in Image Viewer
* **Fix.23** Removed the excess "change remote directory' menu item
* **Fix.24** Fixed bug which prevents removing users (unicode)
* **Fix.24** Potential crash cause removed from settings _usersContent
* **Update.24** TikPhotoshop added to the executable and icon creation group in installer.
* **Update.25** UI Improvements
* **Update.27** Linux compatibility issues (path and ffmpeg)
* **Fix.28** Project Materials - Drag/Drop foolcheck
* **Update.28** Project Materials - statusbar updates
* **Update.4** Standalone and Photoshop modules using PyQt5 now.
* **Update.42** Maya Playblast - "As it is" options
* **Update.43** Naming Conventions - <subproject> added

2.5
---
* **Fix.0** 3ds Max 2018-2019 support
* **Update.0** Installation Update - Callback functions wont cause a crash if the tik_manager path is not valid anymore
* **Update.4** Asset Library Alembic Support added
* **Update.4** Asset Library - Software version check before importing source
* **Fix.4** Import Base Scene option for 3ds Max fixed and renamed as Merge
* **New.5** Checking for updates and new versions option added
* **New.5** Import Footage option added Image Viewer for creating Read nodes in Nuke
* **Update.5** Default root path for Image Viewer changed to the project directory.
* **Fix.5** The bug when browsing the root in Image Viewer fixed. Now it starts browsing from the current defined root.
* **Update.5** Image Viewer default window sizes changed.
* **Update.51** Basic Houdini hiplc compatibility added
* **Fix.51** Linux and MacOs show in folder method fixed
* **Update.52** File name resolves added to save base Scene and Save Version Screens

2.4
---
* **New.0:** Asset Library added
* **New.1:** Sending to Batch Render and Image Sequencer options added to Image Manager (Maya)
* **Update.1:** SmNuke default categories changes (Only Comp by default)
* **Update.2:** SmStandalone now asks for the common database folder on first run.
* **Update.2:** Change Common Database option for SmStandalone
* **Update.3:** Add/Remove User GUI renewed

2.3
---
* **Fix.001:** Bug fix - 'make reference' checkbox removed from save version dialog if runs from Houdini
* **Update.001:** ImageViewer update --> date show/sort feature for collapsed sequences
* **Update.001:** ImageViewer update --> now accepts multiple folder selections

2.2
---
* **New.0:** Project Materials tool added
* **Fix.01:** Button sizes fixed
* **Update.01:** SmMaya imports optimized (pymel is not used anymore)
* **New.02:** Basic Nuke support added
* **Fix.02:** Bug fix when dropping items with standalone project materials
* **Fix.03:** Bug fix with multi camera preview playing (Standalone)
* **Update.03:** Documentation and comment updates
* **Update.04:** softwareDatabase.json file for easy module integration
* **Fix.04:** Bug fix Unicode character dragging to project materials
* **New.04:** New Icon set
* **New.04:** Show In Explorer Root/Raid folders added for image viewer
* **Update.04:** Added project line to the project materials
* **Update.05:** Search filter added to the Set Project Window
* **Update.06:** Image Manager now works on all categories. Send To Deadline is enabled for only Render Layer
* **Update.07:** Previews in Maya supports Camera sequences now.
* **Fix.071:** When references loaded, it asks to set the time range
* **Fix.071:** Minor UI fixes
* **Fix.072:** Houdini open file path fix ("\\" => "/")
* **Fix.072:** Bug fix when canceling the item selection in project materials
* **Fix.073:** Bug fix with default categories when trying to open scene manager from a non-scene manager project
* **Fix.073:** Bug fix - Image Manager / querying shading groups
* **Fix.074:** Bug fix - Image Manager / Unusable Referenced Render Layer checking error fixed
* **Fix.075:** Bug fix - Houdini Module loading and importing modules setting $HIP location fixed
* **Fix.076:** Bug fix - 'make reference' checkbox removed from save version dialog if runs from Houdini

2.1
---
* **Update.0:** Boilerplate UI for all modules
* **Fix.0:** Various bug fixes on all modules
* **Update.0:** Various UI updates
* **New.01:** Added "Show Project Folder" right click menu
* **Fix.01:** Standalone Manager bug with emtpy scenes fixed
* **Update.02:** Sub-projects database file moved to the Database root. It is now common for all softwares

2.0
---
* **New.0:** 3ds Max support added
* **New.0:** Houdini support added
* **New.0:** Standalone Module added
* **New.0:** manager module seperated into SmRoot and SmMaya modules and re-written
* **Update.0:** Lots of UI improvements.
* **Fix.0:** Various bug fixes
* **Update.1:** added hashed password check and change password menu
* **Fix.11:** Fixed callback crash in 3ds max
* **Fix.11:** User update bug with Standalone version
* **Fix.12:** Various fixes and SmStandalone Houdini connection

1.93
----
* **Update.0:** database operations moved to a seperate module
* **New.1:** Brand new Set Project Scene (WIP)
* **TODO** Copy the upgrades from sequence viewer to image viewer

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
* **Fix.4** currentProject check bug with imageManager
* **Fix.5** I/O error fixed when uploading the files to remote directory

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
* **Update:** the name check for duplicate base scenes. It doesnt allow creating base scenes with the same name disregarding it has lower case or upper case characters.

1.1
----
* **New:** "Frame Range" Hud option is added to playblast settings.
* **Update:** In "Reference Mode" Scene List highlighted with red border for visual reference.

1.0
----
* initial