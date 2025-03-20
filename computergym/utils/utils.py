import os

import numpy as np
from PIL import Image


def save_str_to_file(value: str, save_path: str, filename: str):
    if save_path is None:
        return
    os.makedirs(save_path, exist_ok=True)
    full_path = os.path.join(save_path, filename)
    with open(full_path, "w") as f:
        f.write(value)


def read_file(file_path):
    with open(file_path, "r") as f:
        data = f.read().strip()
    return data


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
