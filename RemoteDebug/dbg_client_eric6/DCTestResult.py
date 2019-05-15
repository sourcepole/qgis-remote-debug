# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a TestResult derivative for the eric6 debugger.
"""

import select
from unittest import TestResult


class DCTestResult(TestResult):
    """
    A TestResult derivative to work with eric6's debug client.
    
    For more details see unittest.py of the standard python distribution.
    """
    def __init__(self, dbgClient, failfast):
        """
        Constructor
        
        @param dbgClient reference to the debug client
        @type DebugClientBase
        @param failfast flag indicating to stop at the first error
        @type bool
        """
        TestResult.__init__(self)
        self.__dbgClient = dbgClient
        self.failfast = failfast
        
    def addFailure(self, test, err):
        """
        Public method called if a test failed.
        
        @param test Reference to the test object
        @param err The error traceback
        """
        TestResult.addFailure(self, test, err)
        tracebackLines = self._exc_info_to_string(err, test)
        self.__dbgClient.sendJsonCommand("ResponseUTTestFailed", {
            "testname": str(test),
            "traceback": tracebackLines,
            "id": test.id(),
        })
        
    def addError(self, test, err):
        """
        Public method called if a test errored.
        
        @param test Reference to the test object
        @param err The error traceback
        """
        TestResult.addError(self, test, err)
        tracebackLines = self._exc_info_to_string(err, test)
        self.__dbgClient.sendJsonCommand("ResponseUTTestErrored", {
            "testname": str(test),
            "traceback": tracebackLines,
            "id": test.id(),
        })
        
    def addSkip(self, test, reason):
        """
        Public method called if a test was skipped.
        
        @param test reference to the test object
        @param reason reason for skipping the test (string)
        """
        TestResult.addSkip(self, test, reason)
        self.__dbgClient.sendJsonCommand("ResponseUTTestSkipped", {
            "testname": str(test),
            "reason": reason,
            "id": test.id(),
        })
        
    def addExpectedFailure(self, test, err):
        """
        Public method called if a test failed expected.
        
        @param test reference to the test object
        @param err error traceback
        """
        TestResult.addExpectedFailure(self, test, err)
        tracebackLines = self._exc_info_to_string(err, test)
        self.__dbgClient.sendJsonCommand("ResponseUTTestFailedExpected", {
            "testname": str(test),
            "traceback": tracebackLines,
            "id": test.id(),
        })
        
    def addUnexpectedSuccess(self, test):
        """
        Public method called if a test succeeded expectedly.
        
        @param test reference to the test object
        """
        TestResult.addUnexpectedSuccess(self, test)
        self.__dbgClient.sendJsonCommand("ResponseUTTestSucceededUnexpected", {
            "testname": str(test),
            "id": test.id(),
        })
        
    def startTest(self, test):
        """
        Public method called at the start of a test.
        
        @param test Reference to the test object
        """
        TestResult.startTest(self, test)
        self.__dbgClient.sendJsonCommand("ResponseUTStartTest", {
            "testname": str(test),
            "description": test.shortDescription(),
        })

    def stopTest(self, test):
        """
        Public method called at the end of a test.
        
        @param test Reference to the test object
        """
        TestResult.stopTest(self, test)
        self.__dbgClient.sendJsonCommand("ResponseUTStopTest", {})
        
        # ensure that pending input is processed
        rrdy, wrdy, xrdy = select.select(
            [self.__dbgClient.readstream], [], [], 0.01)

        if self.__dbgClient.readstream in rrdy:
            self.__dbgClient.readReady(self.__dbgClient.readstream)

#
# eflag: noqa = M702
