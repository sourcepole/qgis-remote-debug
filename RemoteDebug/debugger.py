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
"""


class Debugger:

    def __init__(self, iface):
        self.iface = iface

    def startDebugging(self):
        active = self.startEricClient()
        if not active:
            active = self.startPyDevClient()
        if not active:
            active = self.startWindPDBClient()
        if not active:
            self._statusBar().showMessage(u"Debugging connection failed")

    def startEricClient(self):
        started = False
        try:
            from dbg_client.DebugClient import DebugClient
            DBG = DebugClient()
            DBG.startDebugger(host='localhost', filename='', port=42424, exceptions=True, enableTrace=True, redirect=True)
            started = True
            self._statusBar().showMessage(u"Eric4 debugging active")
        except:
            pass
        return started

    def startPyDevClient(self):
        started = False
        try:
            from pysrc import pydevd
            pydevd.settrace(port=5678, suspend=False)
            started = True
            self._statusBar().showMessage(u"PyDev debugging active")
        except:
            pass
        return started

    def startWindPDBClient(self):
        started = False
        try:
            import rpdb2
            rpdb2.start_embedded_debugger('qgis', timeout=10.0)
            started = True
            self._statusBar().showMessage(u"WinPDB debugging active")
        except:
            pass
        return started

    def _statusBar(self):
        return self.iface.mainWindow().statusBar()
