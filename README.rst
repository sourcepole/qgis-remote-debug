=================
qgis-remote-debug
=================

Start Python remote debugger from QGIS plugin


PyDev Debugging (Eclipse)
-------------------------

`PyDev`_ is a Python IDE for Eclipse with `remote debugger`_ support.

The steps to debug an external program are:

- Configure remote debugging of Exceptions (PyDev > Manage Exception Breakpoints)
- Start the remote debugger server
- Go to the debug perspective
- Press the QGIS toolbar icon to activate remote debugging
- The debugger is activated when a breakpoint is reached or an expception is raised (configureable) 

.. _PyDev: http://pydev.org/
.. _remote debugger: http://pydev.org/manual_adv_remote_debugger.html
