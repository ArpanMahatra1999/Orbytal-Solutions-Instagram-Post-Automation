# general libraries
import os
import time
from dotenv import load_dotenv

# functions
from llm_functions import select_category, generate_post, create_caption
from image_functions import create_image
from instagram_functions import upload_to_instagram

# load .env variables
load_dotenv()

# main
if __name__ == "__main__":
    # create post and caption
    category = select_category()
    post = generate_post(category, openai_api_key=os.getenv("OPENAI_API_KEY"))
    caption = create_caption(post, openai_api_key=os.getenv("OPENAI_API_KEY"))
    time.sleep(60)

    # create image
    create_image(post)
    time.sleep(60)

    # post to instagram
    upload_to_instagram("post.png", caption)