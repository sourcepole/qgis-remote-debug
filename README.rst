=================
qgis-remote-debug
=================

Start Python remote debugger from QGIS plugin


PyDev Debugging (Eclipse)
-------------------------

`PyDev`_ is a Python IDE for Eclipse with `remote debugger`_ support.

The steps to debug an external program are:

- Go to the debug perspective
- Configure remote debugging of exceptions (PyDev > Manage Exception Breakpoints)
- Start the debug server (PyDev > Start Debug Server)
- Press the QGIS toolbar icon to activate remote debugging
- The debugger is activated when a breakpoint is reached or an expception is raised (configureable) 

.. _PyDev: http://pydev.org/
.. _remote debugger: http://pydev.org/manual_adv_remote_debugger.html


WinPDB Debugging
----------------

`WinPDB`_ Winpdb is a platform independent GPL Python debugger with support for multiple threads, namespace modification, embedded debugging, encrypted communication and is up to 20 times faster than pdb.

The steps to activate embedded debugging with WinPDB are:

- Start WinPDB
- open File->Attach
- Set password: "qgis"
- Press the QGIS toolbar icon to activate embedded debugging
- Control->Go in Debugger

Debugger is activated on an exception.
You can enter a plugin with the following steps:

- Control->Break in Debugger
- Activate e.g. a GUI element of your plugin

.. _WinPDB: http://winpdb.org/


ERIC4 Passive Debugging 
-----------------------

The steps to activate passive debugging with ERIC4 are:

- open Settings->Preferences->Debugging General
- activate the option "Passive Debugger Enabled"
- Restart the ERIC4 IDE
- Load the Plugin-Project
- Press the QGIS toolbar icon to activate passive debugging with eric4

