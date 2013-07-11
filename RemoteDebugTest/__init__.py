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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "RemoteDebugTest"


def description():
    return "Plugin for testing remote debugger"


def version():
    return "Version 0.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"

def qgisMaximumVersion():
    return "2.99"

def author():
    return "Pirmin Kalberer, Sourcepole"

def email():
    return "pka@sourcepole.ch"

def classFactory(iface):
    # load RemoteDebugTest class from file RemoteDebugTest
    from remotedebugtest import RemoteDebugTest
    return RemoteDebugTest(iface)
