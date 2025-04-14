# general libraries
import os

# instagram libraries
from instagrapi import Client


def upload_to_instagram(image_path, caption, username, password):
    """Post image and caption to Instagram"""
    cl = Client()
    cl.login(username, password)
    cl.photo_upload(image_path, caption)