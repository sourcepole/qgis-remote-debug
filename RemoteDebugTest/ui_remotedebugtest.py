# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_remotedebugtest.ui'
#
# Created: Thu Jul 11 23:50:57 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RemoteDebugTest(object):
    def setupUi(self, RemoteDebugTest):
        RemoteDebugTest.setObjectName(_fromUtf8("RemoteDebugTest"))
        RemoteDebugTest.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(RemoteDebugTest)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.textEdit = QtGui.QTextEdit(RemoteDebugTest)
        self.textEdit.setGeometry(QtCore.QRect(20, 20, 361, 201))
        self.textEdit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))

        self.retranslateUi(RemoteDebugTest)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RemoteDebugTest.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RemoteDebugTest.reject)
        QtCore.QMetaObject.connectSlotsByName(RemoteDebugTest)

    def retranslateUi(self, RemoteDebugTest):
        RemoteDebugTest.setWindowTitle(QtGui.QApplication.translate("RemoteDebugTest", "RemoteDebugTest", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit.setHtml(QtGui.QApplication.translate("RemoteDebugTest", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">This dialog throws an exception for testing remote debugging.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Preparation (PyDev):</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Go to the debug perspective</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Configure remote debugging of exceptions (PyDev &gt; Manage Exception Breakpoints)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Start the debug server (PyDev &gt; Start Debug Server)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- Press the QGIS toolbar icon to activate remote debugging</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- The debugger is activated when a breakpoint is reached or an expception is raised (configureable) </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

