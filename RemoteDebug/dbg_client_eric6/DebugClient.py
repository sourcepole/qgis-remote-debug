# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the standard debug client.
"""

from DebugBase import DebugBase
from DebugClientBase import DebugClientBase
from ThreadExtension import ThreadExtension


class DebugClient(DebugClientBase, DebugBase, ThreadExtension):
    """
    Class implementing the client side of the debugger.
    
    This variant of the debugger implements the standard debugger client
    by subclassing all relevant base classes.
    """
    def __init__(self):
        """
        Constructor
        """
        DebugClientBase.__init__(self)
        
        DebugBase.__init__(self, self)
        
        ThreadExtension.__init__(self)
        
        self.variant = 'Standard'

# We are normally called by the debugger to execute directly.

if __name__ == '__main__':
    debugClient = DebugClient()
    debugClient.main()

#
# eflag: noqa = M702
