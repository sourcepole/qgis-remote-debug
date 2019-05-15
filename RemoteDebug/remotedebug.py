# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebug
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
    from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt4.QtGui import QAction, QIcon
    # Initialize Qt resources from file resources_rc.py
    from .resources_rc import *
else:
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtGui import QIcon
    # Initialize Qt resources from file resources5.py
    from .resources5 import *

import os
import sys

# Import the code for the dialog
from .remotedebug_dialog import RemoteDebugDialog
from .pyqtconfig import QSettingsManager


class RemoteDebug:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RemoteDebug_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = RemoteDebugDialog(self)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Remote Debug')
        self.toolbar = self.iface.pluginToolBar()

        # Using the remote debugger in Windows, it appears that sys.stdin etc can be None
        # According to:
        # https://stackoverflow.com/questions/17458728/when-is-sys-stdin-none-in-python
        # you can assign file descriptors to them in the following way (tested to work on Win10)
        if sys.stdin is None or sys.stdout is None or sys.stderr is None:
            for _name in ('stdin', 'stdout', 'stderr'):
                if getattr(sys, _name) is None:
                    setattr(sys, _name, open(os.devnull, 'r' if _name == 'stdin' else 'w'))
            del _name # clean up this module's name space a little (optional)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RemoteDebug', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RemoteDebug/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Remote Debug'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self._settings = QSettingsManager()
        self._settings.add_handler(
            'RemoteDebug/debugger', self.dlg.debugger_cbox)
        self._settings.add_handler(
            'RemoteDebug/pydev_path', self.dlg.pydev_path_ledit)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Remote Debug'),
                action)
            self.iface.removeToolBarIcon(action)
        self.dlg.hide()
        del self.dlg

    def run(self):
        """Show debugger dialog"""
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass

    def statusBar(self):
        return self.iface.mainWindow().statusBar()

    def push_message(self, text, title="RemoteDebug", level=0, duration=0):
        self.iface.messageBar().pushMessage(title, text, level, duration)
