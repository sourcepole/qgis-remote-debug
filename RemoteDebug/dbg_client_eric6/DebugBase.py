# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the debug base class which based originally on bdb.
"""

import sys
import os
import types
import atexit
import inspect
import ctypes
import time
from inspect import CO_GENERATOR

from BreakpointWatch import Breakpoint, Watch

if sys.version_info[0] == 2:
    import thread as _thread
    from inspect import getargvalues, formatargvalues
else:
    import _thread
    from DebugUtilities import getargvalues, formatargvalues
    unicode = str
    basestring = str

gRecursionLimit = 64


def printerr(s):
    """
    Module function used for debugging the debug client.
    
    @param s data to be printed
    """
    sys.__stderr__.write('{0!s}\n'.format(s))
    sys.__stderr__.flush()


def setRecursionLimit(limit):
    """
    Module function to set the recursion limit.
    
    @param limit recursion limit (integer)
    """
    global gRecursionLimit
    gRecursionLimit = limit


class DebugBase(object):
    """
    Class implementing base class of the debugger.

    Provides methods for the 'owning' client to call to step etc.
    """
    # Don't thrust distutils.sysconfig.get_python_lib: possible case mismatch
    #  on Windows
    lib = os.path.dirname(inspect.__file__)
    # tuple required because it's accessed a lot of times by startswith method
    pathsToSkip = ('<', os.path.dirname(__file__), inspect.__file__[:-1])
    filesToSkip = {}

    # cache for fixed file names
    _fnCache = {}
    
    # Stop all timers, when greenlets are used
    pollTimerEnabled = True

    def __init__(self, dbgClient):
        """
        Constructor
        
        @param dbgClient the owning client
        """
        self._dbgClient = dbgClient
        
        # Some informations about the thread
        self.isMainThread = False
        self.quitting = False
        self.id = -1
        self.name = ''
        
        self.tracePythonLibs(0)
        
        # Special handling of a recursion error
        self.skipFrames = 0
        
        self.isBroken = False
        self.cFrame = None
        
        # current frame we are at
        self.currentFrame = None
        
        # frames, where we want to stop or release debugger
        self.stopframe = None
        self.returnframe = None
        self.stop_everywhere = False
        
        self.__recursionDepth = -1
        self.setRecursionDepth(inspect.currentframe())
        
        # background task to periodicaly check for client interactions
        self.eventPollFlag = False
        self.timer = _thread.start_new_thread(self.__eventPollTimer, ())
        
        # provide a hook to perform a hard breakpoint
        # Use it like this:
        # if hasattr(sys, 'breakpoint): sys.breakpoint()
        sys.breakpoint = self.set_trace
        if sys.version_info[:2] >= (3, 7):
            sys.breakpointhook = self.set_trace

    def __eventPollTimer(self):
        """
        Private method to set a flag every 0.5 s to check for new messages.
        """
        while DebugBase.pollTimerEnabled:
            time.sleep(0.5)
            self.eventPollFlag = True
        
        self.eventPollFlag = False
    
    def getCurrentFrame(self):
        """
        Public method to return the current frame.
        
        @return the current frame
        @rtype frame object
        """
        # Don't show any local frames after the program was stopped
        if self.quitting:
            return None
        
        return self.currentFrame
    
    def getFrameLocals(self, frmnr=0):
        """
        Public method to return the locals dictionary of the current frame
        or a frame below.
        
        @keyparam frmnr distance of frame to get locals dictionary of. 0 is
            the current frame (int)
        @return locals dictionary of the frame
        """
        f = self.currentFrame
        while f is not None and frmnr > 0:
            f = f.f_back
            frmnr -= 1
        return f.f_locals
    
    def storeFrameLocals(self, frmnr=0):
        """
        Public method to store the locals into the frame, so an access to
        frame.f_locals returns the last data.
        
        @keyparam frmnr distance of frame to store locals dictionary to. 0 is
            the current frame (int)
        """
        cf = self.currentFrame
        while cf is not None and frmnr > 0:
            cf = cf.f_back
            frmnr -= 1
        
        try:
            if "__pypy__" in sys.builtin_module_names:
                import __pypy__
                __pypy__.locals_to_fast(cf)
                return
        except Exception:
            pass
        
        ctypes.pythonapi.PyFrame_LocalsToFast(
            ctypes.py_object(cf),
            ctypes.c_int(0))
    
    def step(self, traceMode):
        """
        Public method to perform a step operation in this thread.
        
        @param traceMode If it is True, then the step is a step into,
              otherwise it is a step over.
        """
        if traceMode:
            self.set_step()
        else:
            self.set_next(self.currentFrame)
    
    def stepOut(self):
        """
        Public method to perform a step out of the current call.
        """
        self.set_return(self.currentFrame)
    
    def go(self, special):
        """
        Public method to resume the thread.

        It resumes the thread stopping only at breakpoints or exceptions.
        
        @param special flag indicating a special continue operation
        """
        self.set_continue(special)
    
    def setRecursionDepth(self, frame):
        """
        Public method to determine the current recursion depth.
        
        @param frame The current stack frame.
        """
        self.__recursionDepth = 0
        while frame is not None:
            self.__recursionDepth += 1
            frame = frame.f_back
    
    def profileWithRecursion(self, frame, event, arg):
        """
        Public method used to trace some stuff independent of the debugger
        trace function.
        
        @param frame current stack frame
        @type frame object
        @param event trace event
        @type str
        @param arg arguments
        @type depends on the previous event parameter
        @exception RuntimeError raised to indicate too many recursions
        """
        if event == 'return':
            self.cFrame = frame.f_back
            self.__recursionDepth -= 1
            if self._dbgClient.callTraceEnabled:
                self.__sendCallTrace(event, frame, self.cFrame)
        elif event == 'call':
            if self._dbgClient.callTraceEnabled:
                self.__sendCallTrace(event, self.cFrame, frame)
            self.cFrame = frame
            self.__recursionDepth += 1
            if self.__recursionDepth > gRecursionLimit:
                raise RuntimeError(
                    'maximum recursion depth exceeded\n'
                    '(offending frame is two down the stack)')
    
    def profile(self, frame, event, arg):
        """
        Public method used to trace some stuff independent of the debugger
        trace function.
        
        @param frame current stack frame
        @type frame object
        @param event trace event
        @type str
        @param arg arguments
        @type depends on the previous event parameter
        """
        if event == 'return':
            self.__sendCallTrace(event, frame, frame.f_back)
        elif event == 'call':
            self.__sendCallTrace(event, frame.f_back, frame)
    
    def __sendCallTrace(self, event, fromFrame, toFrame):
        """
        Private method to send a call/return trace.
        
        @param event trace event
        @type str
        @param fromFrame originating frame
        @type frame object
        @param toFrame destination frame
        @type frame object
        """
        if not self.__skipFrame(fromFrame) and not self.__skipFrame(toFrame):
            fromInfo = {
                "filename": self._dbgClient.absPath(
                    self.fix_frame_filename(fromFrame)),
                "linenumber": fromFrame.f_lineno,
                "codename": fromFrame.f_code.co_name,
            }
            toInfo = {
                "filename": self._dbgClient.absPath(
                    self.fix_frame_filename(toFrame)),
                "linenumber": toFrame.f_lineno,
                "codename": toFrame.f_code.co_name,
            }
            self._dbgClient.sendCallTrace(event, fromInfo, toInfo)
    
    def trace_dispatch(self, frame, event, arg):
        """
        Public method reimplemented from bdb.py to do some special things.
        
        This specialty is to check the connection to the debug server
        for new events (i.e. new breakpoints) while we are going through
        the code.
        
        @param frame The current stack frame
        @type frame object
        @param event The trace event
        @type str
        @param arg The arguments
        @type depends on the previous event parameter
        @return local trace function
        @rtype trace function or None
        @exception SystemExit
        """
        # give the client a chance to push through new break points.
        if self.eventPollFlag:
            self._dbgClient.eventPoll()
            self.eventPollFlag = False
            
            if self.quitting:
                raise SystemExit
        
        if event == 'line':
            if self.stop_here(frame) or self.break_here(frame):
                if (self.stop_everywhere and frame.f_back and
                        frame.f_back.f_code.co_name == "prepareJsonCommand"):
                    # Just stepped into print statement, so skip these frames
                    self._set_stopinfo(None, frame.f_back)
                else:
                    self.user_line(frame)
            return self.trace_dispatch
        
        if event == 'call':
            if (self.stop_here(frame) or
                    self.__checkBreakInFrame(frame) or
                    Watch.watches != []):
                return self.trace_dispatch
            else:
                # No need to trace this function
                return None
        
        if event == 'return':
            if frame == self.returnframe:
                # Only true if we didn't stopped in this frame, because it's
                # belonging to the eric debugger.
                self._set_stopinfo(None, frame.f_back)
            return None
        
        if event == 'exception':
            if not self.__skipFrame(frame):
                # When stepping with next/until/return in a generator frame,
                # skip the internal StopIteration exception (with no traceback)
                # triggered by a subiterator run with the 'yield from'
                # statement.
                if not (frame.f_code.co_flags & CO_GENERATOR and
                        arg[0] is StopIteration and arg[2] is None):
                    self.user_exception(arg)
            # Stop at the StopIteration or GeneratorExit exception when the
            # user has set stopframe in a generator by issuing a return
            # command, or a next/until command at the last statement in the
            # generator before the exception.
            elif (self.stopframe and frame is not self.stopframe and
                    self.stopframe.f_code.co_flags & CO_GENERATOR and
                    arg[0] in (StopIteration, GeneratorExit)):
                self.user_exception(arg)
            return None

        if event == 'c_call':
            return None
        if event == 'c_exception':
            return None
        if event == 'c_return':
            return None
        
        print('DebugBase.trace_dispatch:'       # __IGNORE_WARNING_M801__
              ' unknown debugging event: ',
              repr(event))
        return self.trace_dispatch

    def set_trace(self, frame=None):
        """
        Public method to start debugging from 'frame'.

        If frame is not specified, debugging starts from caller's frame.
        Because of jump optimizations it's not possible to use sys.breakpoint()
        as last instruction in a function or method.
        
        @keyparam frame frame to start debugging from
        @type frame object
        """
        if frame is None:
            frame = sys._getframe().f_back  # Skip set_trace method
        
        if sys.version_info[0] == 2:
            stopOnHandleCommand = self._dbgClient.handleJsonCommand.func_code
        else:
            stopOnHandleCommand = self._dbgClient.handleJsonCommand.__code__
        
        frame.f_trace = self.trace_dispatch
        while frame.f_back is not None:
            # stop at eric's debugger frame or a threading bootstrap
            if (frame.f_back.f_code == stopOnHandleCommand):
                frame.f_trace = self.trace_dispatch
                break
            
            frame = frame.f_back
        
        self.stop_everywhere = True
        sys.settrace(self.trace_dispatch)
        sys.setprofile(self._dbgClient.callTraceEnabled)
    
    def bootstrap(self, target, args, kwargs):
        """
        Public method to bootstrap a thread.
        
        It wraps the call to the user function to enable tracing
        before hand.
        
        @param target function which is called in the new created thread
        @type function pointer
        @param args arguments to pass to target
        @type tuple
        @param kwargs keyword arguments to pass to target
        @type dict
        """
        try:
            # Because in the initial run method the "base debug" function is
            # set up, it's also valid for the threads afterwards.
            sys.settrace(self.trace_dispatch)
            
            target(*args, **kwargs)
        except Exception:
            excinfo = sys.exc_info()
            self.user_exception(excinfo, True)
        finally:
            sys.settrace(None)
            sys.setprofile(None)
    
    def run(self, cmd, globalsDict=None, localsDict=None, debug=True):
        """
        Public method to start a given command under debugger control.
        
        @param cmd command / code to execute under debugger control
        @type str or CodeType
        @keyparam globalsDict dictionary of global variables for cmd
        @type dict
        @keyparam localsDict dictionary of local variables for cmd
        @type dict
        @keyparam debug flag if command should run under debugger control
        @type bool
        """
        if globalsDict is None:
            import __main__
            globalsDict = __main__.__dict__
        
        if localsDict is None:
            localsDict = globalsDict
        
        if not isinstance(cmd, types.CodeType):
            cmd = compile(cmd, "<string>", "exec")
        
        if debug:
            # First time the trace_dispatch function is called, a "base debug"
            # function has to be returned, which is called at every user code
            # function call. This is ensured by setting stop_everywhere.
            self.stop_everywhere = True
            sys.settrace(self.trace_dispatch)
        
        try:
            exec(cmd, globalsDict, localsDict)
            atexit._run_exitfuncs()
            self._dbgClient.progTerminated(0)
        except SystemExit:
            atexit._run_exitfuncs()
            excinfo = sys.exc_info()
            exitcode, message = self.__extractSystemExitMessage(excinfo)
            self._dbgClient.progTerminated(exitcode, message)
        except Exception:
            excinfo = sys.exc_info()
            self.user_exception(excinfo, True)
        finally:
            self.quitting = True
            sys.settrace(None)

    def _set_stopinfo(self, stopframe, returnframe):
        """
        Protected method to update the frame pointers.
        
        @param stopframe the frame object where to stop
        @type frame object
        @param returnframe the frame object where to stop on a function return
        @type frame object
        """
        self.stopframe = stopframe
        self.returnframe = returnframe
        if returnframe is not None:
            # Ensure to be able to stop on the return frame
            returnframe.f_trace = self.trace_dispatch
        self.stop_everywhere = False

    def set_continue(self, special):
        """
        Public method to stop only on next breakpoint.
        
        @param special flag indicating a special continue operation
        @type bool
        """
        # Here we only set a new stop frame if it is a normal continue.
        if not special:
            self._set_stopinfo(None, None)
        
        # Disable tracing if not started in debug mode
        if not self._dbgClient.debugging:
            sys.settrace(None)
            sys.setprofile(None)

    def set_step(self):
        """
        Public method to stop after one line of code.
        """
        self._set_stopinfo(None, None)
        self.stop_everywhere = True

    def set_next(self, frame):
        """
        Public method to stop on the next line in or below the given frame.
        
        @param frame the frame object
        @type frame object
        """
        self._set_stopinfo(frame, frame.f_back)
        frame.f_trace = self.trace_dispatch

    def set_return(self, frame):
        """
        Public method to stop when returning from the given frame.
        
        @param frame the frame object
        @type frame object
        """
        self._set_stopinfo(None, frame.f_back)
    
    def move_instruction_pointer(self, lineno):
        """
        Public methode to move the instruction pointer to another line.
        
        @param lineno new line number
        @type int
        """
        try:
            self.currentFrame.f_lineno = lineno
            stack = self.getStack(self.currentFrame)
            self._dbgClient.sendResponseLine(stack)
        except Exception as e:
            printerr(e)

    def set_quit(self):
        """
        Public method to quit.
        
        Disables the trace functions and resets all frame pointer.
        """
        sys.setprofile(None)
        self.stopframe = None
        self.returnframe = None
        for debugThread in self._dbgClient.threads.values():
            debugThread.quitting = True
    
    def fix_frame_filename(self, frame):
        """
        Public method used to fixup the filename for a given frame.
        
        The logic employed here is that if a module was loaded
        from a .pyc file, then the correct .py to operate with
        should be in the same path as the .pyc. The reason this
        logic is needed is that when a .pyc file is generated, the
        filename embedded and thus what is readable in the code object
        of the frame object is the fully qualified filepath when the
        pyc is generated. If files are moved from machine to machine
        this can break debugging as the .pyc will refer to the .py
        on the original machine. Another case might be sharing
        code over a network... This logic deals with that.
        
        @param frame the frame object
        @type frame object
        @return fixed up file name
        @rtype str
        """
        # get module name from __file__
        fn = frame.f_globals.get('__file__')
        try:
            return self._fnCache[fn]
        except KeyError:
            if fn is None:
                return frame.f_code.co_filename
            
            absFilename = os.path.abspath(fn)
            if absFilename.endswith(('.pyc', '.pyo', '.pyd')):
                fixedName = absFilename[:-1]
                if not os.path.exists(fixedName):
                    fixedName = absFilename
            else:
                fixedName = absFilename
            # update cache
            self._fnCache[fn] = fixedName
            return fixedName

    def __checkBreakInFrame(self, frame):
        """
        Private method to check if the function / method has a line number
        which is a breakpoint.
        
        @param frame the frame object
        @type frame object
        @return Flag indicating a function / method with breakpoint
        @rtype bool
        """
        try:
            return Breakpoint.breakInFrameCache[
                frame.f_globals.get('__file__'),
                frame.f_code.co_firstlineno]
        except KeyError:
            filename = self.fix_frame_filename(frame)
            if filename not in Breakpoint.breakInFile:
                Breakpoint.breakInFrameCache[
                    frame.f_globals.get('__file__'),
                    frame.f_code.co_firstlineno] = False
                return False
            lineNo = frame.f_code.co_firstlineno
            lineNumbers = [lineNo]
            
            if sys.version_info[0] == 2:
                co_lnotab = map(ord, frame.f_code.co_lnotab[1::2])
            else:
                co_lnotab = frame.f_code.co_lnotab[1::2]
            
            # No need to handle special case if a lot of lines between
            # (e.g. closure), because the additional lines won't cause a bp
            for co_lno in co_lnotab:
                lineNo += co_lno
                lineNumbers.append(lineNo)
            
            for bp in Breakpoint.breakInFile[filename]:
                if bp in lineNumbers:
                    Breakpoint.breakInFrameCache[
                        frame.f_globals.get('__file__'),
                        frame.f_code.co_firstlineno] = True
                    return True
            Breakpoint.breakInFrameCache[
                frame.f_globals.get('__file__'),
                frame.f_code.co_firstlineno] = False
            return False
    
    def break_here(self, frame):
        """
        Public method reimplemented from bdb.py to fix the filename from the
        frame.
        
        See fix_frame_filename for more info.
        
        @param frame the frame object
        @type frame object
        @return flag indicating the break status
        @rtype bool
        """
        filename = self.fix_frame_filename(frame)
        if (filename, frame.f_lineno) in Breakpoint.breaks:
            bp, flag = Breakpoint.effectiveBreak(
                filename, frame.f_lineno, frame)
            if bp:
                # flag says ok to delete temp. bp
                if flag and bp.temporary:
                    self.__do_clearBreak(filename, frame.f_lineno)
                return True
        
        if Watch.watches != []:
            bp, flag = Watch.effectiveWatch(frame)
            if bp:
                # flag says ok to delete temp. watch
                if flag and bp.temporary:
                    self.__do_clearWatch(bp.cond)
                return True
        
        return False

    def __do_clearBreak(self, filename, lineno):
        """
        Private method called to clear a temporary breakpoint.
        
        @param filename name of the file the bp belongs to
        @type str
        @param lineno linenumber of the bp
        @type int
        """
        Breakpoint.clear_break(filename, lineno)
        self._dbgClient.sendClearTemporaryBreakpoint(filename, lineno)

    def __do_clearWatch(self, cond):
        """
        Private method called to clear a temporary watch expression.
        
        @param cond expression of the watch expression to be cleared
        @type str
        """
        Watch.clear_watch(cond)
        self._dbgClient.sendClearTemporaryWatch(cond)

    def getStack(self, frame=None, applyTrace=False):
        """
        Public method to get the stack.
        
        @keyparam frame frame object to inspect
        @type frame object or list
        @keyparam applyTrace flag to assign trace function to fr.f_trace
        @type bool
        @return list of lists with file name (string), line number (integer)
            and function name (string)
        """
        tb_lineno = None
        if frame is None:
            fr = self.getCurrentFrame()
        elif type(frame) == list:
            fr, tb_lineno = frame.pop(0)
        else:
            fr = frame
        
        stack = []
        while fr is not None:
            if applyTrace:
                # Reset the trace function so we can be sure
                # to trace all functions up the stack... This gets around
                # problems where an exception/breakpoint has occurred
                # but we had disabled tracing along the way via a None
                # return from dispatch_call
                fr.f_trace = self.trace_dispatch
            
            fname = self._dbgClient.absPath(self.fix_frame_filename(fr))
            # Always show at least one stack frame, even if it's from eric.
            if stack and os.path.basename(fname).startswith(
                    ("DebugBase.py", "DebugClientBase.py",
                     "ThreadExtension.py", "threading.py")):
                break
            
            fline = tb_lineno or fr.f_lineno
            ffunc = fr.f_code.co_name
            
            if ffunc == '?':
                ffunc = ''
            
            if ffunc and not ffunc.startswith("<"):
                argInfo = getargvalues(fr)
                try:
                    fargs = formatargvalues(
                        argInfo.args, argInfo.varargs,
                        argInfo.keywords, argInfo.locals)
                except Exception:
                    fargs = ""
            else:
                fargs = ""
            
            stack.append([fname, fline, ffunc, fargs])
            
            # is it a stack frame or exception list?
            if type(frame) == list:
                if frame != []:
                    fr, tb_lineno = frame.pop(0)
                else:
                    fr = None
            else:
                fr = fr.f_back
        
        return stack
    
    def user_line(self, frame):
        """
        Public method reimplemented to handle the program about to execute a
        particular line.
        
        @param frame the frame object
        """
        # We never stop on line 0.
        if frame.f_lineno == 0:
            return
        
        self.isBroken = True
        self.currentFrame = frame
        stack = self.getStack(frame, applyTrace=True)
        
        self._dbgClient.lockClient()
        self._dbgClient.currentThread = self
        self._dbgClient.currentThreadExec = self
        
        self._dbgClient.sendResponseLine(stack)
        self._dbgClient.eventLoop()
        
        self.isBroken = False
        self._dbgClient.unlockClient()
        
    def user_exception(self, excinfo, unhandled=False):
        """
        Public method reimplemented to report an exception to the debug server.
        
        @param excinfo details about the exception
        @type tuple(Exception, excval object, traceback frame object)
        @keyparam unhandled flag indicating an uncaught exception
        @type bool
        """
        exctype, excval, exctb = excinfo
        
        if ((exctype in [GeneratorExit, StopIteration] and
             unhandled is False) or
                exctype == SystemExit):
            # ignore these
            return
        
        if exctype in [SyntaxError, IndentationError]:
            try:
                # tuple could only occure on Python 2, but not always!
                if type(excval) == tuple:
                    message, details = excval
                    filename, lineno, charno, text = details
                else:
                    message = excval.msg
                    filename = excval.filename
                    lineno = excval.lineno
                    charno = excval.offset
                
                if filename is None:
                    realSyntaxError = False
                else:
                    if charno is None:
                        charno = 0
                    
                    filename = os.path.abspath(filename)
                    realSyntaxError = os.path.exists(filename)
                
            except (AttributeError, ValueError):
                message = ""
                filename = ""
                lineno = 0
                charno = 0
                realSyntaxError = True
            
            if realSyntaxError:
                self._dbgClient.sendSyntaxError(
                    message, filename, lineno, charno)
                self._dbgClient.eventLoop()
                return
        
        self.skipFrames = 0
        if (exctype == RuntimeError and
                str(excval).startswith('maximum recursion depth exceeded') or
                sys.version_info >= (3, 5) and
                exctype == RecursionError):  # __IGNORE_WARNING__
            excval = 'maximum recursion depth exceeded'
            depth = 0
            tb = exctb
            while tb:
                tb = tb.tb_next
                
                if (tb and tb.tb_frame.f_code.co_name == 'trace_dispatch' and
                        __file__.startswith(tb.tb_frame.f_code.co_filename)):
                    depth = 1
                self.skipFrames += depth
            
            # always 1 if running without debugger
            self.skipFrames = max(1, self.skipFrames)
        
        exctype = self.__extractExceptionName(exctype)
        
        if excval is None:
            excval = ''
        
        if unhandled:
            exctypetxt = "unhandled {0!s}".format(str(exctype))
        else:
            exctypetxt = str(exctype)
        
        if sys.version_info[0] == 2:
            try:
                excvaltxt = unicode(excval).encode(self._dbgClient.getCoding())
            except UnicodeError:
                excvaltxt = str(excval)
        else:
            excvaltxt = str(excval)
        
        # Don't step into libraries, which are used by our debugger methods
        if exctb is not None:
            self.stop_everywhere = False
        
        self.isBroken = True
        
        stack = []
        if exctb:
            frlist = self.__extract_stack(exctb)
            frlist.reverse()
            
            self.currentFrame = frlist[0][0]
            stack = self.getStack(frlist[self.skipFrames:])
        
        self._dbgClient.lockClient()
        self._dbgClient.currentThread = self
        self._dbgClient.currentThreadExec = self
        self._dbgClient.sendException(exctypetxt, excvaltxt, stack)
        self._dbgClient.dumpThreadList()
        
        if exctb is not None:
            # When polling kept enabled, it isn't possible to resume after an
            # unhandled exception without further user interaction.
            self._dbgClient.eventLoop(True)
        
        self.skipFrames = 0
        
        self.isBroken = False
        stop_everywhere = self.stop_everywhere
        self.stop_everywhere = False
        self.eventPollFlag = False
        self._dbgClient.unlockClient()
        self.stop_everywhere = stop_everywhere
    
    def __extractExceptionName(self, exctype):
        """
        Private method to extract the exception name given the exception
        type object.
        
        @param exctype type of the exception
        @return exception name (string)
        """
        if sys.version_info[0] == 2:
            if type(exctype) in [types.ClassType,   # Python up to 2.4
                                 types.TypeType]:   # Python 2.5+
                return exctype.__name__
            else:
                return exctype
        else:
            return str(exctype).replace("<class '", "").replace("'>", "")
    
    def __extract_stack(self, exctb):
        """
        Private member to return a list of stack frames.
        
        @param exctb exception traceback
        @return list of stack frames
        """
        tb = exctb
        stack = []
        while tb is not None:
            stack.append((tb.tb_frame, tb.tb_lineno))
            tb = tb.tb_next
        tb = None
        return stack

    def __extractSystemExitMessage(self, excinfo):
        """
        Private method to get the SystemExit code and message.
        
        @param excinfo details about the SystemExit exception
        @type tuple(Exception, excval object, traceback frame object)
        @return SystemExit code and message
        @rtype int, str
        """
        exctype, excval, exctb = excinfo
        if excval is None:
            exitcode = 0
            message = ""
        elif isinstance(excval, basestring):
            exitcode = 1
            message = excval
        elif isinstance(excval, bytes):
            exitcode = 1
            message = excval.decode()
        elif isinstance(excval, int):
            exitcode = excval
            message = ""
        elif isinstance(excval, SystemExit):
            code = excval.code
            if isinstance(code, basestring):
                exitcode = 1
                message = code
            elif isinstance(code, bytes):
                exitcode = 1
                message = code.decode()
            elif isinstance(code, int):
                exitcode = code
                message = ""
            else:
                exitcode = 1
                message = str(code)
        else:
            exitcode = 1
            message = str(excval)
        
        return exitcode, message

    def stop_here(self, frame):
        """
        Public method reimplemented to filter out debugger files.
        
        Tracing is turned off for files that are part of the
        debugger that are called from the application being debugged.
        
        @param frame the frame object
        @type frame object
        @return flag indicating whether the debugger should stop here
        @rtype bool
        """
        if self.__skipFrame(frame):
            return False
        
        return (self.stop_everywhere or
                frame is self.stopframe or
                frame is self.returnframe)

    def tracePythonLibs(self, enable):
        """
        Public method to update the settings to trace into Python libraries.
        
        @param enable flag to debug into Python libraries
        @type bool
        """
        pathsToSkip = list(self.pathsToSkip)
        # don't trace into Python library?
        if enable:
            pathsToSkip = [x for x in pathsToSkip if not x.endswith(
                ("site-packages", "dist-packages", self.lib))]
        else:
            pathsToSkip.append(self.lib)
            localLib = [x for x in sys.path if x.endswith(("site-packages",
                        "dist-packages")) and not x.startswith(self.lib)]
            pathsToSkip.extend(localLib)
        
        self.pathsToSkip = tuple(set(pathsToSkip))

    def __skipFrame(self, frame):
        """
        Private method to filter out debugger files.
        
        Tracing is turned off for files that are part of the
        debugger that are called from the application being debugged.
        
        @param frame the frame object
        @type frame object
        @return flag indicating whether the debugger should skip this frame
        @rtype bool
        """
        try:
            return self.filesToSkip[frame.f_code.co_filename]
        except KeyError:
            ret = frame.f_code.co_filename.startswith(self.pathsToSkip)
            self.filesToSkip[frame.f_code.co_filename] = ret
            return ret
        except AttributeError:
            # if frame is None
            return True
    
#
# eflag: noqa = M702
