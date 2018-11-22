# TIK Scene Manager

Tik Scene Manager is a lightweight multi platform asset and project management system.

A project manager helps team members to maintain focus on the task at hand.
Regardless of the scale of the project. Without a project manager, artists tend to waste 
precious time while trying to stay organized or -much worse- they waste more time/data due to the lack of organization.

The goal is to create an everyday project manager which is easy to install and easier to use across different platforms.
Whole system requires little or no maintenance and all database is contained within the project folders. This means it is possible to copy or move the entire project
to another network drive or local disk and continue working.
Small to medium ranged teams are aimed as well as individuals.

Tik Scene Manager already has been tested and used on dozens of tv commercials and several feature films.

Tik Scene Manager has following features / tools:
* Consistent naming of scenes and versions
* Version and reference controlling
* Supports Maya, 3ds Max, Houdini, Nuke
* Standalone version to view and launch all the scenes created with supported softwares
* Adjustable Categories for each project and software version. (Default categories are: Model, Shading, Rig, Layout, Render, Other)
* Sub-project support seperately for each project and software version. 
* Alerts the user for possible problems (FPS mismatch, never/older software version etc.)
* Thumbnails for versions
* Easy and consistent animation previews with logging and playback support
* Custom version notes.
* User database for tracking project progress
* Makes the workflow safer while preventing data loss. No accidental overwriting is possible
* Image Manager (Maya only)
    * Checks the scene for possible errors before rendering
    * Resolves a consistent render path and makes tracking of rendered images easier
    * Supports Mental Ray, Vray, Arnold and Redshift render engines
* Image Viewer
    * Lists rendered images (or footages) as collapsed items
    * Executing the sequences within the application by double clicking
    * Option to send the selected sequences to a remote path in a dated folder
* Project Materials tool for organizing and viewing brief documents, concepts, artworks, references etc.
* Easy installation single CLI installer. (Windows only)

TIK Scene Manager follows a simple folder hierarchy. 
The folder structure makes sense for manual browsing. There are minimal nested folders. If at some
point it has been decided to stop using Scene Manager, it is possible to continue working without relying on it.
However, Scenes saved after that stage wont be included to the Scene Manager database

Scene Manager has the following hierarchy:
* Project Folder
    * Category
        * Sub-Project (If any)
            * Base Scene
                * Version 01
                * Version 02
                * ...
                
Scene Manager main window is not a browser window. It is NOT POSSIBLE TO OVERWRITE ANY PREVIOUS FILE.
With admin password, it is possible to delete entire base scene along with all versions, which ideally should not happen.
