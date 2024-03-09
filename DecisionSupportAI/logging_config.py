# logging_config.py
import logging
from logging import FileHandler

def setup_logging():
    log_file = 'your_log_file.log'

    handler = FileHandler(log_file, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(logging.DEBUG)

