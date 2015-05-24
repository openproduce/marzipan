import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.handlers.WatchedFileHandler("/tmp/logged_it.log")
logger.addHandler(handler)
logger.setLevel("DEBUG")

logger.debug("START LOGGING")
logger.debug("=============")



