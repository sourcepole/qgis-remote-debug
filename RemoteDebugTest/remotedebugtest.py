# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebugTest
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from remotedebugtestdialog import RemoteDebugTestDialog


class RemoteDebugTest:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/remotedebugtest"

        self.dlg = RemoteDebugTestDialog()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/remotedebugtest/icon.png"),
            u"Test", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        self.iface.addPluginToMenu(u"&Remote Debug", self.action)

    def unload(self):
        self.iface.removePluginMenu(u"&Remote Debug", self.action)

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            self.raiseException()

    def raiseException(self):
        #Local vars for testing value display in debugger
        t01 = QgsApplication.pluginPath()
        t02 = QgsApplication.svgPaths()
        #t03 = QChar('x')
        t05 = QPoint()
        t06 = QPointF()
        t07 = QRect()
        t08 = QRectF()
        t09 = QSize()
        t10 = QSizeF()
        t12 = QDate()
        t13 = QTime()
        t14 = QDateTime()
        t15 = QDir()
        t16 = QFile()
        t17 = QFont()
        t18 = QUrl()
        t19 = QModelIndex()
        t20 = QRegExp()
        t21 = self.action
        #t22 = QKeySequence()
        #t23 = QDomAttr()
        #t24 = QDomCharacterData()
        #t25 = QDomComment()
        #t26 = QDomDocument()
        #t27 = QDomElement()
        #t28 = QDomText()
        #t29 = QModelIndex()
        #t30 = QHostAddress()
        t20 = QRegExp()

        #QVariant tests
        tv01 = QSettings().value("locale/userLocale")

        x01 = 42
        x02 = 'fortytwo'
        x03 = u'unitext'

        raise Exception('Exception raised. Check local variables in your debugger.')
