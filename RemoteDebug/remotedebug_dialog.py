# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebugDialog
                                 A QGIS plugin
 Plugin to connect different IDE remote debugger
                             -------------------
        begin                : 2012-07-30
        git sha              : $Format:%H$
        copyright            : (C) 2012-2015 by Pirmin Kalberer & Dr. Horst Düster / Sourcepole AG
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

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'remotedebug_dialog_base.ui'))


class RemoteDebugDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(RemoteDebugDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    @pyqtSlot(int)
    def on_debugger_cbox_activated(self, entry):
        self.pydevd_frm.setEnabled(entry == 1)
