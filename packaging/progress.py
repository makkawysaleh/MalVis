#!/usr/local/bin/python
import sys, time, datetime

class Inplace:
    def __init__(self, title="", stream=sys.stderr):
        # Initialize the Inplace class with a title and stream
        self.stream, self.title = stream, title
        self.last = 0

    def tick(self, s):
        # Update the progress display with the given string
        if not self.stream:
            return
        w = "\r%s%s"%(self.title, s)
        self.last = len(w)
        self.stream.write(w)
        self.stream.flush()

    def inject(self, txt):
        # Inject a new line of text into the stream
        self.stream.write("\n")
        self.clear()
        self.stream.write("%s\n"%txt)
        self.stream.flush()

    def clear(self):
        # Clear the current line in the stream
        if not self.stream:
            return
        spaces = " "*self.last
        self.stream.write("\r%s\r"%spaces)


class Progress(Inplace):
    bookend = "|"
    done = "="
    current = ">"
    todo = " "
    def __init__(self, target, title="", width=40, stream=sys.stderr):
        # Initialize the Progress class with target, title, width, and stream
        Inplace.__init__(self, title, stream=stream)
        self.width, self.target = width, target
        self.prev = -1
        self.startTime = None
        self.window = None

    def tick(self, val):
        # Update the progress bar based on the current value
        if not self.stream:
            return
        if not self.startTime:
            self.startTime = datetime.datetime.now()
        pp = val/float(self.target)
        progress = int(pp * self.width)
        t = datetime.datetime.now() - self.startTime
        runsecs = t.days*86400 + t.seconds + t.microseconds/1000000.0
        if pp == 0:
            eta = "?:??:??"
        else:
            togo = runsecs * (1 - pp)/pp
            eta = datetime.timedelta(seconds = int(togo))
        if pp > self.prev:
            self.prev = pp
            l = self.done * progress
            r = self.todo * (self.width - progress)
            now = time.time()
            s = "%s%s%s%s%s %s" % (
                self.bookend, l,
                self.current,
                r, self.bookend, eta
            )
            Inplace.tick(self, s)

    def set_target(self, t):
        # Set a new target value for the progress bar
        self.target = t

    def restoreTerm(self):
        # Restore terminal settings if using curses
        if self.window:
            #begin nocover
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self.window = None
            #end nocover

    def clear(self):
        # Clear the progress bar and restore terminal settings
        Inplace.clear(self)
        self.restoreTerm()

    def __del__(self):
        # Destructor to restore terminal settings
        self.restoreTerm()

    def full(self):
        # Complete the progress bar
        self.tick(self.target)


class Dummy:
    def __init__(self, *args, **kwargs): 
        # Initialize the Dummy class
        pass
    def tick(self, *args, **kwargs): 
        # Dummy tick method
        pass
    def restoreTerm(self, *args, **kwargs): 
        # Dummy restoreTerm method
        pass
    def clear(self, *args, **kwargs): 
        # Dummy clear method
        pass
    def full(self, *args, **kwargs): 
        # Dummy full method
        pass
    def set_target(self, *args, **kwargs): 
        # Dummy set_target method
        pass

