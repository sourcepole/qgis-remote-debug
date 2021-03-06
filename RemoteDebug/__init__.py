# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteDebug
                                 A QGIS plugin
 Plugin to connect different IDE remote debugger
                             -------------------
        begin                : 2012-07-30
        copyright            : (C) 2012-2015 by Pirmin Kalberer & Dr. Horst Düster / Sourcepole AG
        email                : pka@sourcepole.ch
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RemoteDebug class from file RemoteDebug.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .remotedebug import RemoteDebug
    return RemoteDebug(iface)
