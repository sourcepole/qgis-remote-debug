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

/***************************************************************************
 Modified for Python3, PyQT5, QGIS3
        by Reiner Borchert, Hansa Luftbild AG, borchert@hansaluftbild.de
        in May 2018
 
"""

from sys import version_info
if version_info < (3, 0):
    from PyQt4 import QtGui, uic
    from PyQt4.QtCore import Qt, pyqtSlot
    from PyQt4.QtGui import QDialog, QFileDialog   
else:
    from PyQt5 import QtGui, uic
    from PyQt5.QtCore import Qt, pyqtSlot
    from PyQt5.QtWidgets import QDialog, QFileDialog
    
import os
from .debugger import Debugger

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'remotedebug_dialog_base.ui'))


class RemoteDebugDialog(QDialog, FORM_CLASS):

    def __init__(self, plugin, parent=None):
        """Constructor."""
        super(RemoteDebugDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html#widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self._plugin = plugin
        self._debugger = Debugger()

    @pyqtSlot()
    def on_pydevd_path_but_clicked(self):
        pydevd_path = QFileDialog.getExistingDirectory(
            None, "Select pydev directory containing pydevd.py",
            self.pydev_path_ledit.text())
        if not pydevd_path:
            return  # dialog canceled
        self.pydev_path_ledit.setText(pydevd_path)

    @pyqtSlot()
    def on_connect_but_clicked(self):
        self.setCursor(Qt.WaitCursor)
        try:
            self.start_debugging()
        finally:
            self.unsetCursor()

    @pyqtSlot()
    def on_exception_but_clicked(self):
        raise Exception()

    def start_debugging(self):
        debugger = self._debugger.client(
            self.debugger_cbox.currentIndex())
        self._plugin.statusBar().showMessage(
            u"Connecting to remote debugger...")
        active = debugger.start_debugging(self._debugger_config())
        self._plugin.statusBar().showMessage("")
        if active:
            self.accept()
            self._plugin.push_message(
                u"Debugging connection activated", duration=2)
        else:
            self._plugin.push_message(
                u"Debugging connection failed", level=1, duration=2)

    def _debugger_config(self):
        return {'pydev_path': self.pydev_path_ledit.text()}
