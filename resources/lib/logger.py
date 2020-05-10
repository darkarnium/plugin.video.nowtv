''' Provides an XBMC compatible LogHandler for python logging. '''

import xbmc
import logging


def get(name):
    '''
    Retrieves a logger with the appropriate Kodi handlers installed.

    Args:
        name (str): The name of the logger to retrieve.

    Returns:
        A Logger object pre-configured to emit logs to Kodi.
    '''
    logger = logging.getLogger(name)
    logger.addHandler(LogHandler())
    return logger


class LogHandler(logging.StreamHandler):
    ''' Implements a log handler compatible with Kodi. '''
    LOG_LEVELS = {
        logging.CRITICAL: xbmc.LOGFATAL,
        logging.ERROR: xbmc.LOGERROR,
        logging.WARNING: xbmc.LOGWARNING,
        logging.INFO: xbmc.LOGINFO,
        logging.DEBUG: xbmc.LOGDEBUG,
        logging.NOTSET: xbmc.LOGNONE,
    }

    def emit(self, record):
        '''
        Ensures that all messages are emitted via the Kodi log handler, and
        with the appropriate level set.

        Args:
            record (logging.LogRecord): The logging record to emit.
        '''
        xbmc.log(
            self.format(record),
            self.LOG_LEVELS.get(record.levelno, xbmc.LOGWARNING),
        )
