# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebugTestDialog
                                 A QGIS plugin
 Plugin for testing remote debugger
                             -------------------
        begin                : 2013-07-11
        copyright            : (C) 2013 by Pirmin Kalberer, Sourcepole
        email                : pka@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_remotedebugtest import Ui_RemoteDebugTest
# create the dialog for zoom to point


class RemoteDebugTestDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_RemoteDebugTest()
        self.ui.setupUi(self)
