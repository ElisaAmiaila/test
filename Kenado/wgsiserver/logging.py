import logging
import sys

logger = logging.getLogger("server_logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                              datefmt='%a, %d %b %Y %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)