import logging
from logging.handlers import RotatingFileHandler
import os

LOGDIR_NAME = 'logs'
LOG_PATH = os.path.join(LOGDIR_NAME, 'debug.log')

if not LOGDIR_NAME in os.listdir():
    os.mkdir(LOGDIR_NAME)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(LOG_PATH, maxBytes=1024*1024*5, backupCount=5)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
