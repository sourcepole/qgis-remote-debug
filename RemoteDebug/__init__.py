# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebug
                                 A QGIS plugin
 Plugin to connect different IDE remote debugger
                             -------------------
        begin                : 2012-07-30
        copyright            : (C) 2012 by Dr. Horst Düster / Pirmin Kalberer /Sourcepole AG
        email                : horst.duester@sourcepole.ch
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
    return "Remote Debug"
def description():
    return "Plugin to connect different IDE remote debugger"
def version():
    return "0.1.0"
def experimental():
    return True
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.8"
def classFactory(iface):
    # load RemoteDebug class from file RemoteDebug
    from remotedebug import RemoteDebug
    return RemoteDebug(iface)
