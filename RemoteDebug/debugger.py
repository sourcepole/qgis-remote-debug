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

import sys


class DebuggerClient:
    """Base class for Debugger clients"""

    def start_debugging(self, config=None):
        raise NotImplementedError


class EricClient(DebuggerClient):

    def start_debugging(self, config=None):
        started = False
        try:
            from dbg_client.DebugClient import DebugClient
            DBG = DebugClient()
            DBG.startDebugger(
                host='localhost', filename='', port=42424,
                exceptions=True, enableTrace=True, redirect=True)
            started = True
        except:
            pass
        return started


class PyDevClient(DebuggerClient):

    def start_debugging(self, config):
        started = False
        try:
            sys.path.append(config['pydev_path'])
            import pydevd
            pydevd.settrace(port=5678, suspend=False)
            started = True
        except:
            pass
        return started


class WinPDBClient(DebuggerClient):

    def start_debugging(self, config=None):
        started = False
        try:
            import rpdb2
            rpdb2.start_embedded_debugger('qgis', timeout=10.0)
            started = True
        except:
            pass
        return started


class Debugger:

    def __init__(self):
        self._debuggers = {}
        self._debuggers[0] = EricClient()
        self._debuggers[1] = PyDevClient()
        self._debuggers[2] = WinPDBClient()

    def client(self, debugger_id):
        return self._debuggers[debugger_id]
