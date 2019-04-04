#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# Copyright (c) 2017-2018, Arda Kutlu (ardakutlu@gmail.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

# Module to access Library of global assets

import os

FORCE_QT4 = bool(os.getenv("FORCE_QT4"))

# Enabele FORCE_QT4 for compiling with pyinstaller
# FORCE_QT4 = True

if FORCE_QT4:
    from PyQt4 import QtCore, Qt
    from PyQt4 import QtGui as QtWidgets
else:
    import Qt
    from Qt import QtWidgets, QtCore, QtGui

import json
import os, fnmatch
import logging

logging.basicConfig()
logger = logging.getLogger('smALroot')
logger.setLevel(logging.WARNING)

class AssetLibrary(dict):
    """
    Asset Library Logical operations Class. This Class holds the main functions (save,import,scan)
    """

    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(directory):
            logger.error("Cannot reach the library directory: \n" + directory)

    def saveAsset(self, assetName, screenshot=True, moveCenter=False, selectionOnly=True, exportUV=True, exportOBJ=True, **info):
        """
        Saves the selected object(s) as an asset into the predefined library
        Args:
            assetName: (Unicode) Asset will be saved as with this name
            screenshot: (Bool) If true, screenshots (Screenshot, Thumbnail, Wireframe, UV Snapshots) will be taken with playblast. Default True
            directory: (Unicode) Default Library location. Default is predefined outside of this class
            moveCenter: (Bool) If True, selected object(s) will be moved to World 0 point. Pivot will be the center of selection. Default False
            **info: (Any) Extra information which will be hold in the .json file

        Returns:
            None

        """

        pass


    def scan(self):
        """
        Scans the directory for .json files, and gather info.
        Args:
            directory: (Unicode) Default Library location. Default is predefined outside of this class

        Returns:
            None

        """
        if not os.path.exists(self.directory):
            return
        self.clear()
        # first collect all the json files from second level subfolders
        subDirs = next(os.walk(self.directory))[1]

        # subDirs= (subDirs.sort())
        print subDirs
        allJson = []
        # for d in subDirs:
        #     dir = os.path.join(self.directory, d)
        #     for file in os.listdir(dir):
        #         if file.endswith(".json"):
        #             # assetName, ext = os.path.splitext(file)
        #             file = os.path.join(dir, file)
        #             allJson.append(file)
        #             with open(file, 'r') as f:
        #                 # The JSON module will read our file, and convert it to a python dictionary
        #                 data = json.load(f)
        #                 name = data["assetName"]
        #                 self[name] = data

        # for d in subDirs:
        #     dir = os.path.join(self.directory, d)
        #     for file in os.listdir(dir):
        #         if file.endswith(".json"):
        #             # assetName, ext = os.path.splitext(file)
        #             file = os.path.join(dir, file)
        #             allJson.append(file)
        #             with open(file, 'r') as f:
        #                 # The JSON module will read our file, and convert it to a python dictionary
        #                 data = json.load(f)
        #                 name = data["assetName"]
        #                 self[name] = data

    def importAsset(self, name, copyTextures, mode="maPath"):
        """
        Imports the selected asset into the current scene

        Args:
            name: (Unicode) Name of the asset which will be imported
            copyTextures: (Bool) If True, all texture files of the asset will be copied to the current project directory

        Returns:
            None

        """

        pass

    def savePreviews(self, name, assetDirectory, uvSnap=True, selectionOnly=True):
        """
        Saves the preview files under the Asset Directory
        Args:
            name: (Unicode) Name of the Asset
            assetDirectory: (Unicode) Directory of Asset

        Returns:
            (Tuple) Thumbnail path, Screenshot path, Wireframe path

        """

        pass

    def updatePreviews(self, name, assetDirectory):

        pass
