import logging
import os

def prep_loggers():
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)

    logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    full_handler = logging.FileHandler(os.path.join(log_dir, "full.log"))
    full_handler.setFormatter(logformat)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logformat)

    user_handler = logging.FileHandler(os.path.join(log_dir, "user.log"))
    user_handler.setFormatter(logformat)
    user_logger = logging.getLogger("src.models.User")
    user_logger.addHandler(full_handler)
    user_logger.addHandler(user_handler)
    user_logger.addHandler(console_handler)
    user_logger.setLevel(logging.DEBUG)

    data_ingestion_handler = logging.FileHandler(os.path.join(log_dir, "data_ingestion.log"))
    data_ingestion_handler.setFormatter(logformat)
    data_ingestion_logger = logging.getLogger("src.models.data_ingestion")
    data_ingestion_logger.addHandler(full_handler)
    data_ingestion_logger.addHandler(data_ingestion_handler)
    data_ingestion_logger.addHandler(console_handler)
    data_ingestion_logger.setLevel(logging.DEBUG)

    logic_handler = logging.FileHandler(os.path.join(log_dir, "logic.log"))
    logic_handler.setFormatter(logformat)
    logic_logger = logging.getLogger("src.logic")
    logic_logger.addHandler(full_handler)
    logic_logger.addHandler(logic_handler)
    logic_logger.addHandler(console_handler)
    logic_logger.setLevel(logging.DEBUG)


def log_and_raise(logger, level, message, exception):
    logger.log(level, message)
    raise exception(message)