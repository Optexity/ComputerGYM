import logging
import os

import numpy as np
from PIL import Image


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


def save_str_obs(value: str, save_path: str, filename: str):
    if save_path is None:
        return
    os.makedirs(save_path, exist_ok=True)
    full_path = os.path.join(save_path, filename)
    with open(full_path, "w") as f:
        f.write(value)


# Convert numpy array to PIL Image and save
def save_screenshot(screenshot_array: np.ndarray, save_path: str, filename: str):
    if save_path is None:
        return
    os.makedirs(save_path, exist_ok=True)
    full_path = os.path.join(save_path, filename)
    if isinstance(screenshot_array, np.ndarray):
        img = Image.fromarray(screenshot_array)
        img.save(full_path)


def record_video():
    pass


def log_actions():
    pass


def log_trajectories():
    pass
