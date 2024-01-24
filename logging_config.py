# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_file = 'your_log_file.log'
    max_file_size = 5 * 1024 * 1024
    backup_count = 5

    handler = RotatingFileHandler(log_file, maxBytes=max_file_size, backupCount=backup_count)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(logging.DEBUG)
