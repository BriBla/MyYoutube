import os
import re
import threading
from models.model import VideoFormat, Video, Format
from models.Encoding_class import Encoding
from math import ceil
import ffmpeg


from __main__ import app, engine, session

class Scheduler():
    MAX_THREADS = 2

    def __init__(self, commit_func = None):
        self.pendingTasks = []
        self.threadList = []
        self.runningTasks = []
        self.commit_func = commit_func

    def addThread(self, thread):
        if len(self.threadList) < Scheduler.MAX_THREADS:
            self.threadList.append(thread)

    def cleanupThreads(self):
        i: int = 0
        l_l: int = len(self.threadList)
        while i < l_l:
            if not self.threadList[i].is_alive():
                self.threadList.pop(i)
                i -= 1
                l_l -= 1
            i += 1
        return l_l
    
    def addTask(self, source: str, format, video_id, format_id, encoding: Encoding):
        self.cleanupThreads()
        if len(self.threadList) < self.MAX_THREADS:
            self.threadList.append(EncoderThread(source, format, video_id, format_id, encoding, self))
            return self.threadList[-1]
        else:
            self.pendingTasks.append((source, format, video_id, format_id, encoding))
        return None

    def o_addTask(self, input, target):
        mutex = threading.Lock()
        mutex.acquire()
        thread: EncoderThread = None
        try:
            if self.cleanupThreads() < Scheduler.MAX_THREADS:
                self.threadList.append(EncoderThread())
                thread = self.threadList[-1]
            else:
                self.pendingTasks.append({"thread": thread, "input": input, "target": target})
        finally:
            mutex.release()
        return thread

    def commitEncoding(self, source, format_id, video_id, format, encoding):
        mutex = threading.Lock()
        mutex.acquire()
        try:
            self.commit_func(source, format_id, video_id, format, encoding)
        finally:
            mutex.release()
        

    def getPendingTask(self, thread: threading.Thread):
        task = None
        if thread.is_alive():
            mutex = threading.Lock()
            mutex.acquire()
            try:
                if len(self.pendingTasks):
                    task = self.pendingTasks.pop(0)
            finally:
                mutex.release()
        return task

    def popRunningTask(self, thread):
        self.runningTasks.pop(thread)
    
    def addPendingTask(self, input, target):
        thread = self.getMinLoad
        self.pendingTasks.append({"thread": thread, "input": input, "target": target})

    def popPendingTask(self, thread):
        self.threadList.pop(self.threadList.index(thread))
        for task in self.pendingTasks:
            if task["thread"] == thread:
                self.pendingTasks.pop(self.pendingTasks.index(task))


class EncoderThread(threading.Thread):
    def _o__init__(self, func=None, func_args: list=None, scheduler: Scheduler = None):
        threading.Thread.__init__(self)
        if func:
            self.setRun(func, func_args)
        else:
            self._func = None
            self._args = None
        self.scheduler: Scheduler = scheduler
    
    def __init__(self, source: str, format, video_id, format_id, encoding: Encoding, scheduler):
        threading.Thread.__init__(self)
        self.scheduler = scheduler
        self.renewArgs(source, format, video_id, format_id, encoding)

    def renewArgs(self, source: str, format, video_id, format_id, encoding: Encoding):
        self.video_id = video_id
        self.format_id = video_id
        self.source = source
        self.format = format
        self.format_id = format_id
        self.encoding = encoding
        split_source = source.split('/')
        if split_source[-2] == "sources":
            split_source[-2] = "formats"
        else:
            raise AttributeError("Source path is not valid")
        ext_id = split_source[-1].rfind('.')
        if ext_id >= 0:
            split_source[-1] = split_source[-1][:ext_id] + '_' + str(format) + split_source[-1][ext_id:]
        else:
            raise TypeError("Given source is not named well")
        self.format_source = os.path.join('/', *split_source)
        self.input = None
        print(self.format_source)

    def encode(self):
        self.input = ffmpeg.input(self.source)
        ratio = self.encoding.width() / self.encoding.height()
        enc_width: int = ceil(self.format * ratio)
        enc_width += enc_width % 2
        self.input = ffmpeg.filter(self.input, 'scale', enc_width, self.format)
        self.input = ffmpeg.output(self.input, self.format_source)
        self.input = ffmpeg.overwrite_output(self.input)
        self.encoding.addTarget(self.format)
        try:
            ffmpeg.run(self.input)
        except Exception as e:
            print('ffmpeg error: ', e)
            try:
                os.remove(self.format_source)
            except FileNotFoundError:
                pass #deleted while trying to commit, ok to ignore
        else:
            self.scheduler.commitEncoding(self.format_source, self.format_id, self.video_id, self.format, self.encoding)
            self.encoding.popTarget(self.format)

    def setRun(self, func, func_args):
        if not func or not callable(func):
            raise TypeError("EncoderThread.setRun argument 1: expected callable function object, got {0}".format(type(func)))
        if func_args and not isinstance(func_args, list) and not isinstance(func_args, tuple):
            raise TypeError("EncoderThread.setRun argument 2: expected list or tuple object, got {0}".format(type(func_args)))
        self._func = func
        self._args = func_args

    
    def run(self):
        self.encode()
        new_args: list = self.scheduler.getPendingTask(self)
        while new_args is not None:
            self.renewArgs(*new_args)
            self.encode()
            new_args = self.scheduler.getPendingTask(self)


    def getFunc(self):
        return self._func
    
    def getArgs(self):
        return self._args
    
    def setScheduler(self, scheduler):
        self.scheduler = scheduler

    @staticmethod
    def launchThread(func, func_args):
        thread: EncoderThread = EncoderThread(func, func_args)
        thread.start()
        return thread

    @staticmethod
    def count() -> int:
        return threading.active_count()
    
    @staticmethod
    def getThreads() -> list:
        return threading.enumerate()