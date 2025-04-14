# general libraries
import os

# instagram libraries
from instagrapi import Client


def upload_to_instagram(image_path, caption):
    """Post image and caption to Instagram"""
    cl = Client()
    cl.login(os.getenv("IG_USERNAME"), os.getenv("IG_PASSWORD"))
    cl.photo_upload(image_path, caption)