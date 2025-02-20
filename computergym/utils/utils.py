import logging
import os


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_file: str = "computergym.log",
    log_to_console: bool = True,
    log_path: str = None,
):

    handlers = []
    if log_file:
        os.makedirs(log_path, exist_ok=True)
        handlers.append(logging.FileHandler(os.path.join(log_path, log_file)))
    if log_to_console:
        handlers.append(logging.StreamHandler())

    try:
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
    except Exception as e:
        pass

    logging.basicConfig(
        level=level,  # Set the logging level
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        handlers=handlers,
    )

    logger = logging.getLogger(name)
    return logger


def record_video():
    pass


def log_actions():
    pass


def log_screenshots():
    pass


def log_trajectories():
    pass
