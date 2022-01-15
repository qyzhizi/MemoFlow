import logging
from logging.handlers import WatchedFileHandler
from logging import StreamHandler
from logging import Formatter
import sys
import traceback
import os
import inspect

DEFAULT_FORMAT_STYPE = (
    "%(asctime)s [%(process)d] %(levelname)-8.8s %(name)s: %(message)s"
)

DEFAULT_FORMAT = Formatter(fmt=DEFAULT_FORMAT_STYPE)


def get_program_name():
    return os.path.basename(inspect.stack()[-1][1])


def get_log_file_path(logfile=None, logdir=None,
                      program_name=None, logfile_suffix=".log"):
    logpath = None
    if logfile and logdir:
        logpath = os.path.join(logdir, logfile)
    if not logdir and logfile:
        logpath = logfile
    if not logdir and not logfile and program_name:
        logfile = "%s%s" % (program_name, logfile_suffix)
    if not logfile:
        raise ValueError("not found log file")
    return logpath


class Outs(object):
    def __init__(self, handler, level, formatter=DEFAULT_FORMAT):
        self.handler = handler
        if level:
            self.handler.setLevel(level)
        if formatter:
            self.handler.setFormatter(formatter)

    def add_handler_to_logger(self, logger):
        logger.addHandler(self.handler)


class StreamOut(Outs):

    def __init__(self, formatter=DEFAULT_FORMAT, level=None):
        handler = StreamHandler()
        super(StreamOut, self).__init__(handler, level, formatter)


class File(Outs):

    def __init__(self, filename=None, directory=None,
                 file_suffix=".log", formatter=DEFAULT_FORMAT,
                 level=None):
        programe_name = get_program_name()
        file_path = get_log_file_path(filename, directory, programe_name, file_suffix)
        handler = WatchedFileHandler(file_path)
        super(File, self).__init__(handler, level, formatter)


class RotatingFile(Outs):
    """Output to a file, rotating after a certain size."""

    def __init__(self, filename=None, directory=None, suffix='.log',
                 program_name=None, formatter=DEFAULT_FORMAT,
                 level=None, max_size_bytes=0, backup_count=0):
        """Rotating log file output."""
        logpath = get_log_file_path(filename, directory,
                                    program_name, suffix)
        handler = logging.handlers.RotatingFileHandler(
            logpath, maxBytes=max_size_bytes, backupCount=backup_count)
        super(RotatingFile, self).__init__(handler, level, formatter)

    def do_rollover(self):
        """Manually forces a log file rotation."""
        return self.handler.doRollover()


def setup(level=logging.WARNING, outs=[], program_name=None,
          capture_warnings=True):
    """Setup Python logging.
    This will setup basic handlers for Python logging.
    """
    root_logger = logging.getLogger(None)

    # Remove all handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    if not outs:
        raise ValueError("the outs clazz is None")
    for out in outs:
        out.add_handler_to_logger(root_logger)

    root_logger.setLevel(level)

    program_logger = logging.getLogger(program_name)

    def logging_excepthook(exc_type, value, tb):
        program_logger.critical(
            "".join(traceback.format_exception(exc_type, value, tb)))

    sys.excepthook = logging_excepthook

    if capture_warnings:
        logging.captureWarnings(True)
