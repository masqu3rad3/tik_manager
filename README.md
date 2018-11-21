# TIK Scene Manager

Tik Scene Manager is a lightweight multi platform asset and project management system.
A project manager helps team members to maintain focus on the task at hand.
Regardless of the scale of the project, without a project manager, people tend to waste 
precious time while trying to stay organized or -much worse- they waste more time or data because of not
being organized.

The goal of TIK Scene Manager is to create an easy to install and easier to learn project manager across different platforms.
Whole system requires little or no maintenance and all database is contained within the project folders. This means it is possible to copy the entire project folder,
and continue to work on another network drive or local disk.
Tik Scene Manager is aimed for small to medium ranged groups as well as individuals.

It has been tested and used on dozens of tv commercials and several feature films.

Tik Scene Manager has following features / tools:
* Consistent naming of scenes and versions
* Version and reference controlling
* Supports Maya, 3ds Max, Houdini, Nuke
* Standalone version to view and launch all the scenes created with supported softwares
* Adjustable Categories for each category and software version. (Default categories are: Model, Shading, Rig, Layout, Render, Other)
* Sub-project support for each project and software version. 
* Alerts the user for possible problems (Mismatching FPS, mismatching software version etc.)
* Thumbnails for versions
* Management of animation previews with logging and playback support
* Custom version notes.
* User database for tracking who works on which scene
* Makes the workflow safer while preventing data loss. Basically no accidental overwriting is possible
* Image Manager (Maya only)
    * Checks the scene for possible errors before rendering
    * Resolves a consistent render path, makes tracking of rendered images easier
    * Supports Mental Ray, Vray, Arnold and Redshift render engines
* Image Viewer
    * Lists rendered images (or footages) as collapsed items
    * Double clicking executes the sequence with the application defined by the OS
    * Option to send the selected sequences to a remote path in a dated folder maintining the folder structure.
* Project Materials tool for organizing and viewing brief documents, concepts, artworks, references etc.
* Very easy setup with single CLI installer. (Windows only)

TIK Scene Manager follows a simple folder hierarchy. 
The folder structure stays logical to observe and continue working on even without using Scene Manager
while minimizing nested folders. At some point, if you decide to stop using Scene Manager, you can continue safely
However, Scenes saved after that stage wont be included to the Scene Manager database

Scene Manager has a hiearachy like this:
* Project Folder
    * Category
        * Sub-Project (If any)
            * Base Scene
                * Version 01
                * Version 02
                * ...
                
Scene Manager main window is not a browser window. It is NOT POSSIBLE TO OVERWRITE ANY PREVIOUS FILE.
With admin password, it is possible to delete entire base scene along with all versions, which ideally should not happen.
