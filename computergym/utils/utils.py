import os

import numpy as np
from PIL import Image


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
