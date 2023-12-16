import os

# lib
import wget


def save_image(url: str) -> str:
    image = wget.download(url)
    return image


def delete_image(image):
    os.remove(image)
