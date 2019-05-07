# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an asynchronous file like socket interface for the
debugger.
"""

import socket

from DebugUtilities import prepareJsonCommand

try:
    unicode
except NameError:
    unicode = str
    raw_input = input


def AsyncPendingWrite(file):
    """
    Module function to check for data to be written.
    
    @param file The file object to be checked
    @type file
    @return Flag indicating if there is data waiting
    @rtype int
    """
    try:
        pending = file.pendingWrite()
    except Exception:
        pending = 0

    return pending


class AsyncFile(object):
    """
    Class wrapping a socket object with a file interface.
    """
    maxtries = 10
    
    def __init__(self, sock, mode, name):
        """
        Constructor
        
        @param sock the socket object being wrapped
        @type socket
        @param mode mode of this file
        @type str
        @param name name of this file
        @type str
        """
        # Initialise the attributes.
        self.closed = False
        self.sock = sock
        self.mode = mode
        self.name = name
        self.nWriteErrors = 0
        self.encoding = "utf-8"
        self.errors = None
        self.newlines = None
        self.line_buffering = False
        
        self.wpending = []

    def __checkMode(self, mode):
        """
        Private method to check the mode.
        
        This method checks, if an operation is permitted according to
        the mode of the file. If it is not, an IOError is raised.
        
        @param mode the mode to be checked
        @type string
        @exception IOError raised to indicate a bad file descriptor
        """
        if mode != self.mode:
            raise IOError((9, '[Errno 9] Bad file descriptor'))

    def pendingWrite(self):
        """
        Public method that returns the number of strings waiting to be written.
        
        @return the number of strings to be written
        @rtype int
        """
        return len(self.wpending)

    def close(self, closeit=False):
        """
        Public method to close the file.
        
        @param closeit flag to indicate a close ordered by the debugger code
        @type bool
        """
        if closeit and not self.closed:
            self.flush()
            self.sock.close()
            self.closed = True

    def flush(self):
        """
        Public method to write all pending entries.
        """
        while self.wpending:
            try:
                buf = self.wpending.pop(0)
            except IndexError:
                break
            
            try:
                try:
                    buf = buf.encode('utf-8', 'backslashreplace')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass
                self.sock.sendall(buf)
                self.nWriteErrors = 0
            except socket.error:
                self.nWriteErrors += 1
                if self.nWriteErrors > self.maxtries:
                    self.wpending = []    # delete all output

    def isatty(self):
        """
        Public method to indicate whether a tty interface is supported.
        
        @return always false
        @rtype bool
        """
        return False

    def fileno(self):
        """
        Public method returning the file number.
        
        @return file number
        @rtype int
        """
        try:
            return self.sock.fileno()
        except socket.error:
            return -1

    def readable(self):
        """
        Public method to check, if the stream is readable.
        
        @return flag indicating a readable stream
        @rtype bool
        """
        return self.mode == "r"
    
    def read_p(self, size=-1):
        """
        Public method to read bytes from this file.
        
        @param size maximum number of bytes to be read
        @type int
        @return the bytes read
        @rtype str
        """
        self.__checkMode('r')

        if size < 0:
            size = 20000

        return self.sock.recv(size).decode('utf8', 'backslashreplace')

    def read(self, size=-1):
        """
        Public method to read bytes from this file.
        
        @param size maximum number of bytes to be read
        @type int
        @return the bytes read
        @rtype str
        """
        self.__checkMode('r')

        buf = raw_input()
        if size >= 0:
            buf = buf[:size]
        return buf
    
    def readCommand(self):
        """
        Public method to read a length prefixed command string.
        
        @return command string
        @rtype str
        """
        # The command string is prefixed by a 9 character long length field.
        length = self.sock.recv(9)
        length = int(length)
        data = b''
        while len(data) < length:
            newData = self.sock.recv(length - len(data))
            data += newData
        
        # step 2: convert the data
        return data.decode('utf8', 'backslashreplace')
    
    def readline_p(self, size=-1):
        """
        Public method to read a line from this file.
        
        <b>Note</b>: This method will not block and may return
        only a part of a line if that is all that is available.
        
        @param size maximum number of bytes to be read
        @type int
        @return one line of text up to size bytes
        @rtype str
        """
        self.__checkMode('r')

        if size < 0:
            size = 20000

        # The integration of the debugger client event loop and the connection
        # to the debugger relies on the two lines of the debugger command being
        # delivered as two separate events.  Therefore we make sure we only
        # read a line at a time.
        line = self.sock.recv(size, socket.MSG_PEEK)

        eol = line.find(b'\n')

        if eol >= 0:
            size = eol + 1
        else:
            size = len(line)

        # Now we know how big the line is, read it for real.
        return self.sock.recv(size).decode('utf8', 'backslashreplace')

    def readlines(self, sizehint=-1):
        """
        Public method to read all lines from this file.
        
        @param sizehint hint of the numbers of bytes to be read
        @type int
        @return list of lines read
        @rtype list of str
        """
        self.__checkMode('r')

        lines = []
        room = sizehint

        line = self.readline_p(room)
        linelen = len(line)

        while linelen > 0:
            lines.append(line)

            if sizehint >= 0:
                room = room - linelen

                if room <= 0:
                    break

            line = self.readline_p(room)
            linelen = len(line)

        return lines

    def readline(self, sizehint=-1):
        """
        Public method to read one line from this file.
        
        @param sizehint hint of the numbers of bytes to be read
        @type int
        @return one line read
        @rtype str
        """
        self.__checkMode('r')

        line = raw_input() + '\n'
        if sizehint >= 0:
            line = line[:sizehint]
        return line
    
    def seekable(self):
        """
        Public method to check, if the stream is seekable.
        
        @return flag indicating a seekable stream
        @rtype bool
        """
        return False
    
    def seek(self, offset, whence=0):
        """
        Public method to move the filepointer.
        
        @param offset offset to move the filepointer to
        @type int
        @param whence position the offset relates to
        @type int
        @exception IOError This method is not supported and always raises an
        IOError.
        """
        raise IOError((29, '[Errno 29] Illegal seek'))

    def tell(self):
        """
        Public method to get the filepointer position.
        
        @exception IOError This method is not supported and always raises an
        IOError.
        """
        raise IOError((29, '[Errno 29] Illegal seek'))

    def truncate(self, size=-1):
        """
        Public method to truncate the file.
        
        @param size size to truncate to
        @type int
        @exception IOError This method is not supported and always raises an
        IOError.
        """
        raise IOError((29, '[Errno 29] Illegal seek'))

    def writable(self):
        """
        Public method to check, if a stream is writable.
        
        @return flag indicating a writable stream
        @rtype bool
        """
        return self.mode == "w"
    
    def write(self, s):
        """
        Public method to write a string to the file.
        
        @param s text to be written
        @type str
        """
        self.__checkMode('w')
        
        cmd = prepareJsonCommand("ClientOutput", {
            "text": s,
        })
        self.wpending.append(cmd)
        self.flush()
    
    def write_p(self, s):
        """
        Public method to write a json-rpc 2.0 coded string to the file.
        
        @param s text to be written
        @type str
        """
        self.__checkMode('w')

        self.wpending.append(s)
        self.flush()

    def writelines(self, lines):
        """
        Public method to write a list of strings to the file.
        
        @param lines list of texts to be written
        @type list of str
        """
        self.write("".join(lines))

#
# eflag: noqa = M702
